import logging
from typing import Any, Optional, Tuple

from libmuscle import Instance, Message
from libmuscle.runner import run_simulation
from ymmsl import (
        Component, Conduit, Configuration, Model, Operator, Ports, Settings)


def submodel() -> None:
    """A simple submodel which sends its iteration count.

    This model doesn't simulate anything, it just serves to demonstrate
    a scale-overlapping coupling with different step sizes.
    """
    instance = Instance({
            Operator.O_I: ['boundary_out'],
            Operator.S: ['boundary_in']})

    while instance.reuse_instance():
        # F_INIT
        t_max = instance.get_setting('t_max', 'float')
        dt = instance.get_setting('dt', 'float')

        step = 0
        t_cur = 0.0
        while t_cur < t_max:
            # O_I
            t_next = t_cur + dt
            if t_next >= t_max:
                t_next = None
            logging.info(f'Sending {step} at {t_cur}, next at {t_next}')
            instance.send('boundary_out', Message(t_cur, t_next, step))

            # S
            msg = instance.receive('boundary_in')
            logging.info(
                    f'Received {msg.data} from time {msg.timestamp},'
                    f' next at {msg.next_timestamp}')
            t_cur += dt
            step += 1

        # O_F


class DataCache:
    """Stores data from received messages and interpolates as needed.

    This keeps the data and timestamps from the last two messages
    received from a peer, and interpolates between them to produce data
    for intermediate time points.
    """
    def __init__(self) -> None:
        """Create a DataCache.

        The cache starts out empty.
        """
        self.t_cur = None       # type: Optional[float]
        self.data_cur = None    # type: Optional[Any]
        self.t_next = None      # type: Optional[float]
        self.data_next = None   # type: Optional[Any]

    def add_data(self, t: float, data: Any) -> None:
        """Add new data to the cache.

        If the cache is currently empty, both the current and the next
        data item are set to the new data, at which point we can
        interpolate only for that exact point. As the next message
        arrives, the new data item is saved as the 'next' value, and
        the previous 'next' value becomes the 'cur' value.
        """
        if self.t_cur is None:
            self.t_cur = t
            self.data_cur = data

            self.t_next = t
            self.data_next = data
        else:
            self.t_cur = self.t_next
            self.data_cur = self.data_next

            self.t_next = t
            self.data_next = data

    def get_data(self, t: float) -> Tuple[float, Any]:
        """Return a data value for a given time point.

        This function interpolates the stored data to produce an
        intermediate value. In this example, we simply assume that
        each data item is valid until it is replaced by the next item.
        Hence, no calculation is needed, we just return the current
        value. A more advanced, model-specific coupler would interpolate
        here.

        This value is returned with its corresponding time point here,
        because it makes it easier to see what happens in the log file.
        If `t` is returned instead, as should be done when there's an
        actual interpolation, then to the two submodels being connected
        it looks exactly as if they are running in lockstep.

        If one of the models runs for longer than the other model, then
        the shorter-running model will stop producing new data while
        the longer-running model still needs inputs. In this case, `t`
        can be beyond `self.t_next`, and we need to extrapolate. Here
        we do that by returning the `next` data rather than the `cur`
        data. This also covers the corner case of both models hitting
        the exact same timepoint.
        """
        if self.t_next <= t:
            return self.t_next, self.data_next
        else:
            return self.t_cur, self.data_cur


class Peer:
    """Tracks state for a peer.

    This is a helper class which for one of the peers keeps track of
    the most recent messages it has sent, at which point in simulated
    time the most recent message was received, when the next message
    needs to be sent, and what the next timepoint of the model is.

    This information can then be used to determine whether the model is
    still running, whether we can receive from it or whether we need to
    send a message to it first. For the latter, it also checks whether
    the necessary data is available.

    Finally, this class does the actual communication with the peer,
    via the instance object.
    """
    def __init__(
            self, instance: Instance, in_port: str, out_port: str) -> None:
        """Create a Peer object.

        This also receives an initial message from the peer model, and
        uses the received data to initialise the cache and the state.

        Args:
            instance: The instance to use for communication
            in_port: The port to receive on for this peer
            out_port: The port to send on for this peer
        """
        self.instance = instance
        self.in_port = in_port
        self.out_port = out_port
        self.cache = DataCache()

        msg = self.instance.receive(self.in_port)
        self.cache.add_data(msg.timestamp, msg.data)
        self.rcvd = msg.timestamp
        self.to_send = msg.timestamp
        self.next = msg.next_timestamp

    def done(self) -> bool:
        """Return whether we are done commmunicating with this peer."""
        return self.to_send is None

    def can_receive(self) -> bool:
        """Return whether we can receive a message from this peer."""
        return self.next is not None and self.next <= self.to_send

    def receive(self) -> None:
        """Receive a message from this peer and update the cache."""
        msg = self.instance.receive(self.in_port)
        self.cache.add_data(msg.timestamp, msg.data)
        self.rcvd = msg.timestamp
        self.next = msg.next_timestamp

    def can_send(self, peer_rcvd: float, peer_next: Optional[float]) -> bool:
        """Return whether we can send to this peer.

        This determines whether our next interaction with the peer
        should be sending a message to it, which depends on whether
        the peer will try to receive again, and on whether we have
        data available to send to it.

        The latter depends on whether we have received the data from
        the other peer that we need to create a message for the time
        point at which this peer expects to receive. That information
        is passed into this function.

        Args:
            peer_recvd: When we last received from the other peer.
            peer_next: If and when the other peer will send again.
        """
        if self.to_send is None:
            return False
        return self.to_send <= peer_rcvd or peer_next is None

    def send(self, t: float, data: Any) -> None:
        """Send the next message to this peer.

        This sends a message to the peer containing the given data
        and timestamp, and marks this send as done.

        Args:
            t: Timestamp corresponding to the data
            data: Data to send
        """
        self.instance.send(self.out_port, Message(t, self.next, data))
        self.to_send = self.next


def temporal_coupler() -> None:
    """Model component connecting two scale-overlapping submodels.

    This component sits in between two scale-overlapping submodels
    running at different (and potentially variable) timesteps and
    ensures that each of these peers receives a message whenever it
    expects one, and can send a message whenever it expects to do so.

    Structurally, this looks like a model, but as you can see there
    are no clearly separated O_I and S stages. Instead, we send and
    receive in just the right order to mirror each peer's receive and
    send operations. Information from the timestamps on the received
    messages is used to ensure the correct order of operations.

    To ensure that we have data to interpolate between, we always
    prefer to receive, and only send if we cannot receive.
    """
    instance = Instance({
        Operator.O_I: ['a_out', 'b_out'],
        Operator.S: ['a_in', 'b_in']})

    while instance.reuse_instance():
        # Receive initial messages and initialise state
        a = Peer(instance, 'a_in', 'a_out')
        b = Peer(instance, 'b_in', 'b_out')

        # Send and receive as needed
        while not a.done() or not b.done():
            if a.can_receive():
                a.receive()
            elif b.can_receive():
                b.receive()
            elif a.can_send(b.rcvd, b.next):
                t, data = b.cache.get_data(a.to_send)
                a.send(t, data)
            elif b.can_send(a.rcvd, a.next):
                t, data = a.cache.get_data(b.to_send)
                b.send(t, data)


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    components = [
            Component(
                'left', 'model', None,
                Ports(o_i=['boundary_out'], s=['boundary_in'])),
            Component(
                'right', 'model', None,
                Ports(o_i=['boundary_out'], s=['boundary_in'])),
            Component(
                'coupler', 'temporal_coupler', None,
                Ports(o_i=['a_out', 'b_out'], s=['a_in', 'b_in']))]

    conduits = [
            Conduit('left.boundary_out', 'coupler.a_in'),
            Conduit('right.boundary_out', 'coupler.b_in'),
            Conduit('coupler.a_out', 'left.boundary_in'),
            Conduit('coupler.b_out', 'right.boundary_in')]

    model = Model('interact_coupling', components, conduits)

    settings = Settings({
        't_max': 100.0,
        'left.dt': 5.0,
        'right.dt': 13.0,
        })

    configuration = Configuration(model, settings)

    implementations = {'model': submodel, 'temporal_coupler': temporal_coupler}
    run_simulation(configuration, implementations)
