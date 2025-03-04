from copy import copy
from enum import Flag, auto
import logging
import os
import sys
from typing import cast, Dict, List, Literal, Optional, Tuple, overload

from ymmsl import (Identifier, Operator, SettingValue, Port, Reference,
                   Settings)

from libmuscle.api_guard import APIGuard
from libmuscle.checkpoint_triggers import TriggerManager
from libmuscle.communicator import Communicator, Message
from libmuscle.settings_manager import SettingsManager
from libmuscle.logging import LogLevel
from libmuscle.logging_handler import MuscleManagerHandler
from libmuscle.mpp_message import ClosePort
from libmuscle.mmp_client import MMPClient
from libmuscle.mmsf_validator import MMSFValidator
from libmuscle.peer_info import PeerInfo
from libmuscle.port_manager import PortManager
from libmuscle.profiler import Profiler
from libmuscle.profiling import (
        ProfileEvent, ProfileEventType, ProfileTimestamp)
from libmuscle.snapshot_manager import SnapshotManager
from libmuscle.util import extract_log_file_location


_logger = logging.getLogger(__name__)


_FInitCacheType = Dict[Tuple[str, Optional[int]], Message]


class InstanceFlags(Flag):
    """Enumeration of properties that an instance may have.

    You may combine multiple flags using the bitwise OR operator `|`. For
    example:

    .. code-block:: python

        from libmuscle import (
                Instance, USES_CHECKPOINT_API, DONT_APPLY_OVERLAY)

        ports = ...
        flags = USES_CHECKPOINT_API | DONT_APPLY_OVERLAY
        instance = Instance(ports, flags)
    """

    DONT_APPLY_OVERLAY = auto()
    """Do not apply the received settings overlay during prereceive of F_INIT
    messages. If you're going to use :meth:`Instance.receive_with_settings` on
    your F_INIT ports, you need to set this flag when creating an
    :class:`Instance`.

    If you don't know what that means, do not specify this flag and everything
    will be fine. If it turns out that you did need to specify the flag, MUSCLE3
    will tell you about it in an error message and you can add it still.
    """

    USES_CHECKPOINT_API = auto()
    """Indicate that this instance supports checkpointing.

    You may not use any checkpointing API calls when this flag is not supplied.
    """

    KEEPS_NO_STATE_FOR_NEXT_USE = auto()
    """Indicate this instance does not carry state between iterations of the
    reuse loop. Specifying this flag is equivalent to
    :external:py:attr:`ymmsl.KeepsStateForNextUse.NO`.

    By default, (if neither :attr:`KEEPS_NO_STATE_FOR_NEXT_USE` nor
    :attr:`STATE_NOT_REQUIRED_FOR_NEXT_USE` are provided), the instance is assumed
    to keep state between reuses, and to require that state (equivalent to
    :external:py:attr:`ymmsl.KeepsStateForNextUse.NECESSARY`).
    """

    STATE_NOT_REQUIRED_FOR_NEXT_USE = auto()
    """Indicate this instance carries state between iterations of the
    reuse loop, however this state is not required for restarting.
    Specifying this flag is equivalent to
    :external:py:attr:`ymmsl.KeepsStateForNextUse.HELPFUL`.

    By default, (if neither :attr:`KEEPS_NO_STATE_FOR_NEXT_USE` nor
    :attr:`STATE_NOT_REQUIRED_FOR_NEXT_USE` are provided), the instance is assumed
    to keep state between reuses, and to require that state (equivalent to
    :external:py:attr:`ymmsl.KeepsStateForNextUse.NECESSARY`).
    """

    SKIP_MMSF_SEQUENCE_CHECKS = auto()
    """Disable the checks whether the MMSF is strictly followed when sending/receiving
    messages.

    See :class:`~libmuscle.mmsf_validator.MMSFValidator` for a detailed description of
    the checks.
    """


_CHECKPOINT_SUPPORT_MASK = (
        InstanceFlags.USES_CHECKPOINT_API |
        InstanceFlags.KEEPS_NO_STATE_FOR_NEXT_USE |
        InstanceFlags.STATE_NOT_REQUIRED_FOR_NEXT_USE)


class Instance:
    """Represents a component instance in a MUSCLE3 simulation.

    This class provides a low-level send/receive API for the instance
    to use.
    """
    def __init__(
            self, ports: Optional[Dict[Operator, List[str]]] = None,
            flags: InstanceFlags = InstanceFlags(0)) -> None:
        """Create an Instance.

        Args:
            ports: A list of port names for each
                :external:py:class:`~ymmsl.Operator` of this component.
            flags: Indicate properties for this instance. See
                :py:class:`InstanceFlags` for a detailed description of possible
                flags.
        """
        self.__is_shut_down = False

        self._flags = InstanceFlags(flags)

        # Note that these are accessed by Muscle3, but otherwise private.
        self._name, self._index = self.__make_full_name()
        """Name and index of this instance."""

        self._instance_id = self._name + self._index
        """Full id of this instance."""

        mmp_location = self.__extract_manager_location()
        self.__manager = MMPClient(self._instance_id, mmp_location)
        """Client object for talking to the manager."""

        self.__set_up_logging()

        self._api_guard = APIGuard(
                InstanceFlags.USES_CHECKPOINT_API in self._flags)
        """Checks that the user uses the API correctly."""

        self._profiler = Profiler(self.__manager)
        """Profiler for this instance."""

        self._port_manager = PortManager(self._index, ports)
        """PortManager for this instance."""

        self._communicator = Communicator(
                self._name, self._index, self._port_manager, self._profiler,
                self.__manager)
        """Communicator for this instance."""

        self._declared_ports = ports
        """Declared ports for this instance."""

        self._settings_manager = SettingsManager()
        """Settings for this instance."""

        self._snapshot_manager = SnapshotManager(
                self._instance_id, self.__manager, self._port_manager)
        """Resumes, loads and saves snapshots."""

        self._trigger_manager = TriggerManager()
        """Keeps track of checkpoints and triggers snapshots."""

        self._first_run: Optional[bool] = None
        """Whether this is the first iteration of the reuse loop"""

        self._do_reuse: Optional[bool] = None
        """Whether to enter this iteration of the reuse loop

        This is None during the reuse loop, and set between
        should_save_final_snapshot and reuse_instance.
        """

        self._do_resume = False
        """Whether to resume on this iteration of the reuse loop"""

        self._do_init = False
        """Whether to do f_init on this iteration of the reuse loop"""

        self._f_init_cache: _FInitCacheType = {}
        """Stores pre-received messages for f_init ports"""

        self._register()
        self._connect()
        # Note: self._setup_checkpointing() needs to have the ports initialized
        # so it comes after self._connect()
        self._setup_checkpointing()
        # profiling and logging need settings, so come after register_()
        self._set_local_log_level()
        self._set_remote_log_level()
        self._setup_profiling()
        self._setup_receive_timeout()
        # MMSFValidator needs a connected port manager, and does some logging
        self._mmsf_validator = (
                None if InstanceFlags.SKIP_MMSF_SEQUENCE_CHECKS in self._flags
                else MMSFValidator(self._port_manager))

    def reuse_instance(self) -> bool:
        """Decide whether to run this instance again.

        In a multiscale simulation, instances get reused all the time.
        For example, in a macro-micro simulation, the micromodel does a
        complete run for every timestep of the macromodel. Rather than
        starting up a new instance of the micromodel, which could be
        expensive, we reuse a single instance many times.

        This may bring other advantages, such as faster convergence
        when starting from the previous final state, and in some
        cases may be necessary if micromodel state needs to be
        preserved from one macro timestep to the next.

        So in MUSCLE, submodels run in a *reuse loop*, which runs them
        over and over again until their work is done and they should be
        shut down. Whether to do another F_INIT, O_I, S, O_F cycle
        is decided by this method.

        This method must be called at the beginning of the reuse loop,
        i.e. before the F_INIT operator, and its return value should
        decide whether to enter that loop again.

        Raises:
            RuntimeError:
                When implementing the checkpointing API, but libmuscle detected
                incorrect API calls. The description of the RuntimeError
                indicates which calls are incorrect or missing. For more
                information see the checkpointing API documentation in
                :meth:`resuming`, :meth:`load_snapshot`,
                :meth:`should_save_snapshot`, :meth:`save_snapshot`,
                :meth:`should_save_final_snapshot` and
                :meth:`save_final_snapshot`, or the checkpointing tutorial.
        """
        self._api_guard.verify_reuse_instance()
        if self._mmsf_validator:
            self._mmsf_validator.reuse_instance()

        if self._do_reuse is not None:
            # thank you, should_save_final_snapshot, for running this already
            do_reuse = self._do_reuse
            self._do_reuse = None
        else:
            do_reuse = self._decide_reuse_instance()

        if self._do_resume and not self._do_init and self._mmsf_validator:
            self._mmsf_validator.skip_f_init()

        # now _first_run, _do_resume and _do_init are also set correctly

        do_implicit_checkpoint = (
                not self._first_run and
                InstanceFlags.USES_CHECKPOINT_API not in self._flags and
                (InstanceFlags.STATE_NOT_REQUIRED_FOR_NEXT_USE in self._flags or
                 InstanceFlags.KEEPS_NO_STATE_FOR_NEXT_USE in self._flags))

        if do_implicit_checkpoint:
            if self._trigger_manager.should_save_final_snapshot(
                    do_reuse, self.__f_init_max_timestamp):
                # store a None instead of a Message
                self._save_snapshot(None, True, self.__f_init_max_timestamp)

        if not do_reuse:
            self.__shutdown()

        self._api_guard.reuse_instance_done(do_reuse)
        return do_reuse

    def error_shutdown(self, message: str) -> None:
        """Logs an error and shuts down the Instance.

        If you detect that something is wrong (invalid input, invalid
        settings, simulation diverged, or anything else really), you
        should call this method before calling exit() or raising
        an exception that you don't expect to catch.

        If you do so, the Instance will tell the rest of the simulation
        that it encountered an error and will shut down. That makes it
        easier to debug the situation (the message will be logged), and
        it reduces the chance that other parts of the simulation will
        sit around waiting forever for a message that this instance was
        supposed to send.

        Args:
            message: An error message describing the problem.
        """
        self.__shutdown(message)

    def list_settings(self) -> List[str]:
        """List settings by name.

        This function returns a list of names of the available settings.

        Return:
            A list of setting names.
        """
        return self._settings_manager.list_settings(self._instance_id)

    @overload
    def get_setting(self, name: str, typ: Literal['str']) -> str:
        ...

    @overload
    def get_setting(self, name: str, typ: Literal['int']) -> int:
        ...

    @overload
    def get_setting(self, name: str, typ: Literal['float']) -> float:
        ...

    @overload
    def get_setting(self, name: str, typ: Literal['bool']) -> bool:
        ...

    @overload
    def get_setting(self, name: str, typ: Literal['[int]']) -> List[int]:
        ...

    @overload
    def get_setting(self, name: str, typ: Literal['[float]']) -> List[float]:
        ...

    @overload
    def get_setting(
            self, name: str, typ: Literal['[[float]]']) -> List[List[float]]:
        ...

    @overload
    def get_setting(self, name: str, typ: None = None) -> SettingValue:
        ...

    def get_setting(self, name: str, typ: Optional[str] = None
                    ) -> SettingValue:
        """Returns the value of a model setting.

        Args:
            name: The name of the setting, without any instance
                    prefix.
            typ: The expected type of the value. If the value does
                    not match this type, a TypeError will be raised.
                    If not specified, any of the supported types
                    will be accepted, and you'll have to figure out
                    what you got yourself.

        Raises:
            KeyError: If no value was set for this setting.
            TypeError: If the type of the setting's value was not
                    as expected.
        """
        return self._settings_manager.get_setting(
                self._instance_id, Reference(name), typ)

    def list_ports(self) -> Dict[Operator, List[str]]:
        """Returns a description of the ports that this Instance has.

        Note that the result has almost the same format as the port
        declarations you pass when making an Instance. The only
        difference is that the port names never have `[]` at the end,
        even if the port is a vector port.

        Returns:
            A dictionary, indexed by :external:py:class:`~ymmsl.Operator`,
            containing lists of port names. Operators with no associated ports
            are not included.
        """
        return self._port_manager.list_ports()

    def is_connected(self, port: str) -> bool:
        """Returns whether the given port is connected.

        Args:
            port: The name of the port to inspect.

        Returns:
            True if there is a conduit attached to this port, False
            if not.
        """
        return self._port_manager.get_port(port).is_connected()

    def is_vector_port(self, port: str) -> bool:
        """Returns whether a port is a vector or scalar port

        If a port has been declared to be a vector port (i.e. the
        name passed when creating this Instance had '[]' at the
        end), then you can pass a 'slot' argument when sending or
        receiving. It's like the port is a vector of slots on which
        you can send or receive messages.

        This function returns True if the given port is a vector
        port, and False if it is a scalar port.

        Args:
            port: The port to check this property of.
        """
        return self._port_manager.get_port(port).is_vector()

    def is_resizable(self, port: str) -> bool:
        """Returns whether the given port is resizable.

        Scalar ports are never resizable. Whether a vector port is
        resizable depends on what it is connected to.

        Args:
            port: Name of the port to inspect.

        Returns:
            True if the port can be resized.
        """
        return self._port_manager.get_port(port).is_resizable()

    def get_port_length(self, port: str) -> int:
        """Returns the current length of the port.

        Args:
            port: The name of the port to measure.

        Raises:
            RuntimeError: If this is a scalar port.
        """
        return self._port_manager.get_port(port).get_length()

    def set_port_length(self, port: str, length: int) -> None:
        """Resizes the port to the given length.

        You should check whether the port is resizable using
        :meth:`is_resizable()` first; whether it is depends on how this
        component is wired up, so you should check.

        Args:
            port: Name of the port to resize.
            length: The new length.

        Raises:
            RuntimeError: If the port is not resizable.
        """
        self._port_manager.get_port(port).set_length(length)

    def send(self, port_name: str, message: Message,
             slot: Optional[int] = None) -> None:
        """Send a message to the outside world.

        Sending is non-blocking, a copy of the message will be made
        and stored in memory until the receiver is ready to receive it.

        Args:
            port_name: The port on which this message is to be sent.
            message: The message to be sent.
            slot: The slot to send the message on, if any.
        """
        self.__check_port(port_name, slot, True)
        if self._mmsf_validator:
            self._mmsf_validator.check_send(port_name, slot)
        if message.settings is None:
            message = copy(message)
            message.settings = self._settings_manager.overlay

        self._communicator.send_message(
                port_name, message, slot,
                self._trigger_manager.checkpoints_considered_until())

    def receive(self, port_name: str, slot: Optional[int] = None,
                default: Optional[Message] = None
                ) -> Message:
        """Receive a message from the outside world.

        Receiving is a blocking operation. This function will contact
        the sender, wait for a message to be available, and receive and
        return it.

        If the port you are receiving on is not connected, the default
        value you specified will be returned exactly as you passed it.
        If you didn't specify a default value (e.g. because there is no
        reasonable default, you really need the outside input) and the
        port is not connected, you'll get a RuntimeError.

        Args:
            port_name: The endpoint on which a message is to be
                    received.
            slot: The slot to receive the message on, if any.
            default: A default value to return if this port is not
                    connected.

        Returns:
            The received message. The settings attribute of the
            received message will be None.

        Raises:
            RuntimeError: If the given port is not connected and no
                    default value was given.
        """
        return self.__receive_message(port_name, slot, default, False)

    def receive_with_settings(
            self, port_name: str, slot: Optional[int] = None,
            default: Optional[Message] = None
            ) -> Message:
        """Receive a message with attached settings overlay.

        This function should not be used in submodels. It is intended
        for use by special component that are ensemble-aware and
        have to pass on overlay settings explicitly.

        Receiving is a blocking operation. This function will contact
        the sender, wait for a message to be available, and receive and
        return it.

        If the port you are receiving on is not connected, the default
        value you specified will be returned exactly as you passed it.
        If you didn't specify a default value (e.g. because there is no
        reasonable default, and you really need the outside input) and
        the port is not connected, then you'll get a RuntimeError.

        Args:
            port_name: The endpoint on which a message is to be
                    received.
            slot: The slot to receive the message on, if any.
            default: A default value to return if this port is not
                    connected.

        Returns:
            The received message. The settings attribute will
            contain the received Settings, and will not be None.

        Raises:
            RuntimeError: If the given port is not connected and no
                    default value was given.
        """
        return self.__receive_message(port_name, slot, default, True)

    def resuming(self) -> bool:
        """Check if this instance is resuming from a snapshot.

        Must be used by submodels that implement the checkpointing API. You'll
        get a RuntimeError when not calling this method in an iteration of the
        reuse loop.

        This method returns True for the first iteration of the reuse loop after
        resuming from a previously taken snapshot. When resuming from a
        snapshot, the submodel must load its state from the snapshot as returned
        by :meth:`load_snapshot`.

        Returns:
            True iff the submodel must resume from a snapshot.
        """
        self._api_guard.verify_resuming()
        self._api_guard.resuming_done(self._do_resume)
        return self._do_resume

    def should_init(self) -> bool:
        """Check if this instance should initialize.

        Must be used by submodels that implement the checkpointing API.

        When resuming from a previous snapshot, instances need not always
        execute the F_INIT phase of the submodel execution loop. Use this method
        before attempting to receive data on F_INIT ports.

        Returns:
            True if the submodel must execute the F_INIT step, False otherwise.
        """
        self._api_guard.verify_should_init()
        self._api_guard.should_init_done()
        return self._do_init

    def load_snapshot(self) -> Message:
        """Load a snapshot.

        Must only be called when :meth:`resuming` returns True.

        Returns:
            Message object containing the state as saved in a previous run
            through :meth:`save_snapshot` or :meth:`save_final_snapshot`.

        Raises:
            RuntimeError: if not resuming from a snapshot.
        """
        self._api_guard.verify_load_snapshot()
        result = self._snapshot_manager.load_snapshot()
        self._api_guard.load_snapshot_done()
        return result

    def should_save_snapshot(self, timestamp: float) -> bool:
        """Check if a snapshot should be saved after the S Operator of the
        submodel.

        This method checks if a snapshot should be saved right now, based on the
        provided timestamp and passed wallclock time.

        When this method returns True, the submodel must also save a snapshot
        through :meth:`save_snapshot`. A RuntimeError will be generated if this
        is not done.

        See also :meth:`should_save_final_snapshot` for the variant that must be
        called at the end of the reuse loop.

        Args:
            timestamp: current timestamp of the submodel.

        Returns:
            True iff a snapshot should be taken by the submodel according to the
            checkpoint rules provided in the ymmsl configuration.
        """
        self._api_guard.verify_should_save_snapshot()
        result = self._trigger_manager.should_save_snapshot(timestamp)
        self._api_guard.should_save_snapshot_done(result)
        return result

    def save_snapshot(self, message: Message) -> None:
        """Save a snapshot after the S Operator of the submodel.

        Before saving a snapshot, you should check using
        :meth:`should_save_snapshot` if a snapshot should be saved according to
        the checkpoint rules specified in the ymmsl configuration. You should
        use the same timestamp in the provided Message object as used to query
        `should_save_snapshot`.

        See also :meth:`save_final_snapshot` for the variant that must be called
        at the end of the reuse loop.

        Args:
            message: Message object that is saved as snapshot. The message
                timestamp attribute should be the same as passed to
                :meth:`should_save_snapshot`. The data attribute can be used to
                store the internal state of the submodel.
        """
        self._api_guard.verify_save_snapshot()
        if message is None:
            raise RuntimeError('Please specify a Message to save as snapshot.')
        self._save_snapshot(message, False)
        self._api_guard.save_snapshot_done()

    def should_save_final_snapshot(self) -> bool:
        """Check if a snapshot should be saved at the end of the reuse loop.

        This method checks if a snapshot should be saved at the end of the reuse
        loop. All your communication on O_F ports must be finished before calling
        this method, otherwise your simulation may deadlock.

        When this method returns True, the submodel must also save a snapshot
        through :meth:`save_final_snapshot`. A :class:`RuntimeError` will be
        generated if this is not done.

        See also :meth:`should_save_snapshot` for the variant that may be called
        inside of a time-integration loop of the submodel.

        .. note::
            This method will block until it can determine whether a final
            snapshot should be taken, because it must determine if this
            instance is reused.

        Returns:
            True iff a final snapshot should be taken by the submodel according
            to the checkpoint rules provided in the ymmsl configuration.
        """
        self._api_guard.verify_should_save_final_snapshot()

        self._do_reuse = self._decide_reuse_instance()
        result = self._trigger_manager.should_save_final_snapshot(
                self._do_reuse, self.__f_init_max_timestamp)

        self._api_guard.should_save_final_snapshot_done(result)
        return result

    def save_final_snapshot(self, message: Message) -> None:
        """Save a snapshot at the end of the reuse loop.

        Before saving a snapshot, you should check using
        :meth:`should_save_final_snapshot` if a snapshot should be saved
        according to the checkpoint rules specified in the ymmsl configuration.

        See also :meth:`save_snapshot` for the variant that may be called after
        each S Operator of the submodel.

        Args:
            message: Message object that is saved as snapshot. The data
                attribute can be used to store the internal state of the
                submodel.
        """
        self._api_guard.verify_save_final_snapshot()
        if message is None:
            raise RuntimeError('Please specify a Message to save as snapshot.')
        self._save_snapshot(message, True, self.__f_init_max_timestamp)
        self._api_guard.save_final_snapshot_done()

    @property
    def __f_init_max_timestamp(self) -> Optional[float]:
        """Return max timestamp of pre-received F_INIT messages
        """
        return max(
                (msg.timestamp for msg in self._f_init_cache.values()),
                default=None)

    def _register(self) -> None:
        """Register this instance with the manager.
        """
        register_event = ProfileEvent(
                ProfileEventType.REGISTER, ProfileTimestamp())
        locations = self._communicator.get_locations()
        port_list = self.__list_declared_ports()
        self.__manager.register_instance(locations, port_list)
        self._profiler.record_event(register_event)
        _logger.info('Registered with the manager')

    def _connect(self) -> None:
        """Connect this instance to the given peers / conduits.
        """
        connect_event = ProfileEvent(
                ProfileEventType.CONNECT, ProfileTimestamp())

        conduits, peer_dims, peer_locations = self.__manager.request_peers()

        peer_info = PeerInfo(
                self._name, self._index, conduits, peer_dims, peer_locations)
        self._port_manager.connect_ports(peer_info)
        self._communicator.set_peer_info(peer_info)

        self._settings_manager.base = self.__manager.get_settings()

        self._profiler.record_event(connect_event)
        _logger.info('Received peer locations and base settings')

    def _deregister(self) -> None:
        """Deregister this instance from the manager.
        """
        # Make sure we record this even if profiling is disabled, so
        # that we always have register, connect and deregister at
        # least.
        self._profiler.set_level('all')

        deregister_event = ProfileEvent(
                ProfileEventType.DEREGISTER, ProfileTimestamp())
        # We need to finish the event right away, because we need to
        # submit it before deregistering, which is the last interaction
        # with the manager we'll have.
        self._profiler.record_event(deregister_event)

        # This is the last thing we'll profile, so flush messages
        self._profiler.shutdown()
        self.__manager.deregister_instance()

        # Remove handler, the manager may be gone at this point so we
        # cannot send it any more log messages.
        logging.getLogger().removeHandler(self._mmp_handler)
        _logger.info('Deregistered from the manager')

    def _setup_checkpointing(self) -> None:
        """Setup checkpointing.
        """
        checkpoint_info = self.__manager.get_checkpoint_info()

        elapsed_time, checkpoints = checkpoint_info[0:2]
        self._trigger_manager.set_checkpoint_info(elapsed_time, checkpoints)

        if checkpoints and not (self._flags & _CHECKPOINT_SUPPORT_MASK):
            err_msg = (
                    'The workflow has requested checkpoints, but this instance'
                    ' does not support checkpointing. Please consult the'
                    ' MUSCLE3 checkpointing documentation how to add'
                    ' checkpointing support.')
            self.__shutdown(err_msg)
            raise RuntimeError(err_msg)

        resume_snapshot, snapshot_dir = checkpoint_info[2:4]
        saved_at = self._snapshot_manager.prepare_resume(
                resume_snapshot, snapshot_dir)
        # Resume settings overlay
        overlay = self._snapshot_manager.resume_overlay
        if overlay is not None:
            self._settings_manager.overlay = overlay

        if saved_at is not None:
            self._trigger_manager.update_checkpoints(saved_at)

    @staticmethod
    def __extract_manager_location() -> str:
        """Gets the manager network location from the command line.

        We use a --muscle-manager=<host:port> argument to tell the
        MUSCLE library how to connect to the manager. This function
        will extract this argument from the command line arguments,
        if it is present. If not, it will check the MUSCLE_MANAGER
        environment variable, and if that is not set, fall back to
        the default.

        Returns:
            A connection string, or None.
        """
        # Neither getopt, optparse, or argparse will let me pick out
        # just one option from the command line and ignore the rest.
        # So we do it by hand.
        prefix = '--muscle-manager='
        for arg in sys.argv[1:]:
            if arg.startswith(prefix):
                return arg[len(prefix):]

        return os.environ.get('MUSCLE_MANAGER', 'tcp:localhost:9000')

    def __set_up_logging(self) -> None:
        """Adds logging handlers for one or more instances.
        """
        id_str = str(self._instance_id)

        logfile = extract_log_file_location('muscle3.{}.log'.format(id_str))
        if logfile is not None:
            local_handler = logging.FileHandler(str(logfile), mode='w')
            formatter = logging.Formatter(
                    '%(asctime)-15s: %(levelname)-7s %(name)s: %(message)s')
            local_handler.setFormatter(formatter)
            logging.getLogger('libmuscle').addHandler(local_handler)
            logging.getLogger('ymmsl').addHandler(local_handler)

        if self.__manager is not None:
            self._mmp_handler = MuscleManagerHandler(id_str, logging.WARNING,
                                                     self.__manager)
            logging.getLogger().addHandler(self._mmp_handler)

    def _setup_profiling(self) -> None:
        """Configures profiler with settings from settings.
        """
        try:
            profile_level_str = self.get_setting('muscle_profile_level', 'str')
        except KeyError:
            profile_level_str = 'all'

        if profile_level_str not in ('none', 'all'):
            _logger.warning(
                    'Invalid value for muscle_profile_level:'
                    f' {profile_level_str}. Please specify "none" or "all".'
                    ' Using default value "all".')
            profile_level_str = 'all'

        self._profiler.set_level(profile_level_str)

    def _setup_receive_timeout(self) -> None:
        """Configures receive timeout with settings from settings.
        """
        try:
            timeout = self.get_setting('muscle_deadlock_receive_timeout', 'float')
            if 0 <= timeout < 0.1:
                _logger.info(
                        "Provided muscle_deadlock_receive_timeout (%f) was less than "
                        "the minimum of 0.1 seconds, setting it to 0.1.", timeout)
                timeout = 0.1
            self._communicator.set_receive_timeout(timeout)
        except KeyError:
            pass  # do nothing and keep the default
        _logger.debug(
                "Timeout on receiving messages set to %f",
                self._communicator._receive_timeout)

    def _decide_reuse_instance(self) -> bool:
        """Decide whether and how to reuse the instance.

        This sets self._first_run, self._do_resume and self._do_init, and
        returns whether to reuse one more time. This is the real top of
        the reuse loop, and it gets called by reuse_instance and
        should_save_final_snapshot.
        """
        if self._first_run is None:
            self._first_run = True
        elif self._first_run:
            self._first_run = False

        # resume from intermediate
        if self._first_run and self._snapshot_manager.resuming_from_intermediate():
            self._do_resume = True
            self._do_init = False
            return True

        f_init_connected = self._have_f_init_connections()

        # resume from final
        if self._first_run and self._snapshot_manager.resuming_from_final():
            if f_init_connected:
                got_f_init_messages = self._pre_receive()
                self._do_resume = True
                self._do_init = True
                return got_f_init_messages
            else:
                self._do_resume = False     # unused
                self._do_init = False       # unused
                return False

        # fresh start or resuming from implicit snapshot
        self._do_resume = False

        # simple straight single run without resuming
        if not f_init_connected:
            self._do_init = self._first_run
            return self._first_run

        # not resuming and f_init connected, run while we get messages
        got_f_init_messages = self._pre_receive()
        self._do_init = got_f_init_messages
        return got_f_init_messages

    def _save_snapshot(
            self, message: Optional[Message], final: bool,
            f_init_max_timestamp: Optional[float] = None) -> None:
        """Save a snapshot to disk and notify manager.

        Args:
            message: The data to save
            final: Whether this is a final snapshot or an intermediate
                one
            f_init_max_timestamp: Timestamp for final snapshots
        """
        triggers = self._trigger_manager.get_triggers()
        walltime = self._trigger_manager.elapsed_walltime()
        timestamp = self._snapshot_manager.save_snapshot(
                message, final, triggers, walltime,
                f_init_max_timestamp, self._settings_manager.overlay)
        self._trigger_manager.update_checkpoints(timestamp)

    def __receive_message(
            self, port_name: str, slot: Optional[int],
            default: Optional[Message], with_settings: bool
            ) -> Message:
        """Receives a message on the given port.

        This implements receive and receive_with_settings, see the
        description of those.
        """
        self.__check_port(port_name, slot, False, True)
        if self._mmsf_validator:
            self._mmsf_validator.check_receive(port_name, slot)

        port = self._port_manager.get_port(port_name)
        if port.operator == Operator.F_INIT:
            if (port_name, slot) in self._f_init_cache:
                msg = self._f_init_cache[(port_name, slot)]
                del self._f_init_cache[(port_name, slot)]
                if with_settings and msg.settings is None:
                    err_msg = ('If you use receive_with_settings()'
                               ' on an F_INIT port, then you have to'
                               ' set the flag'
                               ' :attr:`InstanceFlag.DONT_APPLY_OVERLAY` when'
                               ' creating the :class:`Instance`, otherwise the'
                               ' settings will already have been applied by'
                               ' MUSCLE.')
                    self.__shutdown(err_msg)
                    raise RuntimeError(err_msg)
            else:
                if port.is_connected():
                    err_msg = (('Tried to receive twice on the same'
                                ' port "{}", that\'s not possible.'
                                ' Did you forget to call'
                                ' reuse_instance() in your reuse loop?'
                                ).format(port_name))
                    self.__shutdown(err_msg)
                    raise RuntimeError(err_msg)
                else:
                    if default is not None:
                        return default
                    err_msg = (('Tried to receive on port "{}",'
                                ' which is not connected, and no'
                                ' default value was given. Please'
                                ' connect this port!').format(port_name))
                    self.__shutdown(err_msg)
                    raise RuntimeError(err_msg)

        else:
            if not port.is_connected():
                if default is None:
                    raise RuntimeError(('Tried to receive on port "{}", which is'
                                        ' disconnected, and no default value was'
                                        ' given. Either specify a default, or'
                                        ' connect a sending component to this'
                                        ' port.').format(port_name))
                else:
                    _logger.debug(
                            f'No message received on {port_name} as it is not'
                            ' connected')
                    return default

            else:
                msg, saved_until = self._communicator.receive_message(port_name, slot)
                if not port.is_open(slot):
                    err_msg = (('Port {} was closed while trying to'
                                ' receive on it, did the peer crash?'
                                ).format(port_name))
                    self.__shutdown(err_msg)
                    raise RuntimeError(err_msg)
                if not with_settings:
                    self.__check_compatibility(port_name, msg.settings)
                    msg.settings = None
                self._trigger_manager.harmonise_wall_time(saved_until)
        return msg

    def __make_full_name(self
                         ) -> Tuple[Reference, List[int]]:
        """Returns instance name and index.

        This takes the argument to the --muscle-instance= command-line
        option and splits it into a component name and an index.
        """
        def split_reference(ref: Reference) -> Tuple[Reference, List[int]]:
            index: List[int] = []
            i = 0
            while i < len(ref) and isinstance(ref[i], Identifier):
                i += 1
            name = ref[:i]

            while i < len(ref) and isinstance(ref[i], int):
                index.append(cast(int, ref[i]))
                i += 1

            return name, index

        # Neither getopt, optparse, or argparse will let me pick out
        # just one option from the command line and ignore the rest.
        # So we do it by hand.
        prefix_tag = '--muscle-instance='
        for arg in sys.argv[1:]:
            if arg.startswith(prefix_tag):
                prefix_str = arg[len(prefix_tag):]
                prefix_ref = Reference(prefix_str)
                name, index = split_reference(prefix_ref)
                break
        else:
            if 'MUSCLE_INSTANCE' in os.environ:
                prefix_ref = Reference(os.environ['MUSCLE_INSTANCE'])
                name, index = split_reference(prefix_ref)
            else:
                raise RuntimeError((
                    'A --muscle-instance command line argument or'
                    ' MUSCLE_INSTANCE environment variable is required to'
                    ' identify this instance. Please add one.'))
        return name, index

    def __list_declared_ports(self) -> List[Port]:
        """Returns a list of declared ports.

        This returns a list of ymmsl.Port objects, which have only the
        name and the operator, not libmuscle.Port, which has more.
        """
        result = list()
        if self._declared_ports is not None:
            for operator, port_names in self._declared_ports.items():
                for name in port_names:
                    if name.endswith('[]'):
                        name = name[:-2]
                    result.append(Port(Identifier(name), operator))
        return result

    def __check_port(
            self, port_name: str, slot: Optional[int], is_send: bool,
            allow_slot_out_of_range: bool = False) -> None:
        if not self._port_manager.port_exists(port_name):
            err_msg = (('Port "{}" does not exist on "{}". Please check'
                        ' the name and the list of ports you gave for'
                        ' this component.').format(port_name, self._name))
            self.__shutdown(err_msg)
            raise RuntimeError(err_msg)

        port = self._port_manager.get_port(port_name)
        if is_send:
            if not port.operator.allows_sending():
                err_msg = (f'Port "{port_name}" does not allow sending messages.')
                self.__shutdown(err_msg)
                raise RuntimeError(err_msg)
        else:
            if not port.operator.allows_receiving():
                err_msg = (f'Port "{port_name}" does not allow receiving messages.')
                self.__shutdown(err_msg)
                raise RuntimeError(err_msg)

        if slot is not None:
            if not port.is_vector():
                err_msg = (
                        f'Port "{port_name}" is not a vector port, but a slot was'
                        ' given. Please check your send call and your port'
                        ' declarations')
                self.__shutdown(err_msg)
                raise RuntimeError(err_msg)

            if port.is_connected():
                # This check needs to be revised for resizable instance sets
                if not (port.is_resizable() and allow_slot_out_of_range):
                    if port.get_length() <= slot:
                        err_msg = (
                                f'Tried to send or receive on slot {slot} of port'
                                f' "{port_name}", which has length {port.get_length()}.'
                                f' Please check your code and/or the multiplicities in'
                                f' the model description.')
                        self.__shutdown(err_msg)
                        raise RuntimeError(err_msg)

    def _have_f_init_connections(self) -> bool:
        """Checks whether we have connected F_INIT ports.

        This includes muscle_settings_in, and any user-defined ports.
        """
        ports = self._port_manager.list_ports()
        f_init_connected = any(
                [self.is_connected(port)
                 for port in ports.get(Operator.F_INIT, [])])
        return f_init_connected or self._port_manager.settings_in_connected()

    def _pre_receive(self) -> bool:
        """Pre-receives on all ports.

        This includes muscle_settings_in and all user-defined ports.

        Returns:
            True iff no ClosePort messages were received.
        """
        sw_event = ProfileEvent(ProfileEventType.SHUTDOWN_WAIT, ProfileTimestamp())

        all_ports_open = True
        if not self._port_manager.settings_in_connected():
            self._settings_manager.overlay = Settings()
        else:
            all_ports_open = self.__receive_settings()

        self.__pre_receive_f_init()
        for message in self._f_init_cache.values():
            if isinstance(message.data, ClosePort):
                all_ports_open = False

        if not all_ports_open:
            self._profiler.record_event(sw_event)

        return all_ports_open

    def __receive_settings(self) -> bool:
        """Receives settings on muscle_settings_in.

        Returns:
            False iff the port is connnected and ClosePort was received.
        """
        message, saved_until = self._communicator.receive_message('muscle_settings_in')

        if isinstance(message.data, ClosePort):
            return False
        if not isinstance(message.data, Settings):
            err_msg = ('"{}" received a message on'
                       ' muscle_settings_in that is not a'
                       ' Settings. It seems that your'
                       ' simulation is miswired or the sending'
                       ' instance is broken.'.format(self._instance_id))
            self.__shutdown(err_msg)
            raise RuntimeError(err_msg)

        settings = cast(Settings, message.settings).copy()
        for key, value in message.data.items():
            settings[key] = value
        self._settings_manager.overlay = settings

        self._trigger_manager.harmonise_wall_time(saved_until)
        return True

    def __pre_receive_f_init(self) -> None:
        """Receives on all ports connected to F_INIT.

        This receives all incoming messages on F_INIT and stores them
        in self._f_init_cache.
        """
        apply_overlay = InstanceFlags.DONT_APPLY_OVERLAY not in self._flags

        def pre_receive(port_name: str, slot: Optional[int]) -> None:
            msg, saved_until = self._communicator.receive_message(port_name, slot)
            if apply_overlay:
                self.__apply_overlay(msg)
                self.__check_compatibility(port_name, msg.settings)
                msg.settings = None
            self._f_init_cache[(port_name, slot)] = msg
            self._trigger_manager.harmonise_wall_time(saved_until)

        self._f_init_cache = dict()
        ports = self._port_manager.list_ports()
        for port_name in ports.get(Operator.F_INIT, []):
            _logger.debug('Pre-receiving on port {}'.format(port_name))
            port = self._port_manager.get_port(port_name)
            if not port.is_connected():
                continue
            if not port.is_vector():
                pre_receive(port_name, None)
            else:
                pre_receive(port_name, 0)
                # The above receives the length, if needed, so now we can
                # get the rest.
                for slot in range(1, port.get_length()):
                    pre_receive(port_name, slot)

    def _set_remote_log_level(self) -> None:
        """Sets the remote log level.

        This is the minimum level a message must have to be sent to
        the manager. It gets this from the muscle_remote_log_level
        setting.

        Note that this also sets the global log level to this level
        if it is currently higher, otherwise we still get no output.
        """
        try:
            log_level_str = self.get_setting('muscle_remote_log_level', 'str')
        except KeyError:
            # muscle_remote_log_level not set, do nothing and keep the default
            return

        try:
            log_level = LogLevel[log_level_str.upper()]
            if log_level == LogLevel.LOCAL:
                raise KeyError()

            py_level = log_level.as_python_level()
            self._mmp_handler.setLevel(py_level)
            if not logging.getLogger().isEnabledFor(py_level):
                logging.getLogger().setLevel(py_level)

        except KeyError:
            _logger.warning(
                ('muscle_remote_log_level is set to {}, which is not a'
                 ' valid remote log level. Please use one of DEBUG, INFO,'
                 ' WARNING, ERROR, CRITICAL, or DISABLED').format(
                     log_level_str))
            return

    def _set_local_log_level(self) -> None:
        """Sets the local log level.

        This sets the local log level for libmuscle and ymmsl, from the
        muscle_local_log_level setting.

        It also attaches a FileHandler which outputs to a local file named
        after the instance. This name can be overridden by the
        --muscle-log-file command line option.
        """
        try:
            log_level_str = self.get_setting('muscle_local_log_level', 'str')
        except KeyError:
            # muscle_remote_log_level not set, do nothing and keep the default
            return

        try:
            log_level = LogLevel[log_level_str.upper()]
        except KeyError:
            _logger.warning(
                ('muscle_local_log_level is set to {}, which is not a'
                 ' valid log level. Please use one of DEBUG, INFO,'
                 ' WARNING, ERROR, CRITICAL, or DISABLED').format(
                     log_level_str))
            return

        py_level = log_level.as_python_level()
        logging.getLogger('libmuscle').setLevel(py_level)
        logging.getLogger('ymmsl').setLevel(py_level)

    def __apply_overlay(self, message: Message) -> None:
        """Sets local overlay if we don't already have one.

        Args:
            message: The message to apply the overlay from.
        """
        if len(self._settings_manager.overlay) == 0:
            if message.settings is not None:
                self._settings_manager.overlay = message.settings

    def __check_compatibility(self, port_name: str,
                              overlay: Optional[Settings]) -> None:
        """Checks whether a received overlay matches the current one.

        Args:
            port_name: Name of the port on which the overlay was
                    received.
            overlay: The received overlay.
        """
        if overlay is None:
            return
        if self._settings_manager.overlay != overlay:
            err_msg = (('Unexpectedly received data from a'
                        ' parallel universe on port "{}". My'
                        ' settings are "{}" and I received'
                        ' from a universe with "{}".').format(
                            port_name, self._settings_manager.overlay,
                            overlay))
            self.__shutdown(err_msg)
            raise RuntimeError(err_msg)

    def __shutdown(self, message: Optional[str] = None) -> None:
        """Shuts down simulation.

        This logs the given error message, if any, communicates to the
        peers that we're shutting down, and deregisters from the manager.
        """
        if not self.__is_shut_down:
            if message is not None:
                _logger.critical(message)
            self._communicator.shutdown()
            self._deregister()
            self.__manager.close()
            self.__is_shut_down = True
