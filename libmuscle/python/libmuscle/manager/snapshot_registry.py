from dataclasses import dataclass, field
from datetime import datetime
from enum import Flag, auto
from functools import lru_cache
from itertools import chain, zip_longest
from operator import attrgetter
from pathlib import Path
from queue import Queue
from threading import Thread
from typing import Dict, Optional, Set, FrozenSet, List, Tuple, TypeVar

from ymmsl import (
        Reference, Model, Identifier, Implementation, save,
        PartialConfiguration)

from libmuscle.manager.topology_store import TopologyStore
from libmuscle.snapshot import SnapshotMetadata


_MAX_FILE_EXISTS_CHECK = 100

_SnapshotDictType = Dict[Reference, List["SnapshotNode"]]
_ConnectionType = Tuple[Identifier, Identifier, "_ConnectionInfo"]
_QueueItemType = Optional[Tuple[Reference, SnapshotMetadata]]
_T = TypeVar("_T")

# this snapshot is used as a placeholder for restarting from scratch
_NULL_SNAPSHOT = SnapshotMetadata(["Instance start"], 0, 0, None, {}, True, '')


def safe_get(lst: List[_T], index: int, default: _T) -> _T:
    """Get an item from the list, returning default when it does not exist.

    Args:
        lst: List to get the item from
        index: Which item to get, should be >= 0
        default: Value to return when hitting an IndexError
    """
    try:
        return lst[index]
    except IndexError:
        return default


class _ConnectionInfo(Flag):
    SELF_IS_SENDING = auto()
    SELF_IS_VECTOR = auto()
    PEER_IS_VECTOR = auto()


def calc_consistency(
        num1: int, num2: int, first_is_sent: bool, num2_is_restart: bool
        ) -> bool:
    """Calculate consistency of message counts.

    Args:
        num1: message count of instance 1
        num2: message count of instance 2
        first_is_sent: True iff instance 1 is sending messages over this conduit
        num2_is_restart: True iff the snapshot of num2 is a full restart

    Returns:
        True iff the two message counts are consistent
    """
    return (num1 == num2 or                             # strong
            num1 + 1 == num2 and first_is_sent or       # weak (1 = sent)
            # weak (2 = sent) - only allow if num2 is not a restart
            num2 + 1 == num1 and not first_is_sent and not num2_is_restart)


def calc_consistency_list(
        num1: List[int], num2: List[int], first_is_sent: bool,
        num2_is_restart: bool) -> bool:
    """Calculate consistency of message counts.

    Args:
        num1: message count of instance 1
        num2: message count of instance 2
        first_is_sent: True iff instance 1 is sending messages over this conduit
        num2_is_restart: True iff the snapshot of num2 is a full restart

    Returns:
        True iff the two message counts are consistent
    """
    if first_is_sent:
        allow_weak = True
        slot_iter = zip_longest(num1, num2, fillvalue=0)
    else:
        allow_weak = not num2_is_restart
        slot_iter = zip_longest(num2, num1, fillvalue=0)
    return all(slot_sent == slot_received or                    # strong
               slot_sent + 1 == slot_received and allow_weak    # weak
               for slot_sent, slot_received in slot_iter)


@dataclass
class SnapshotNode:
    """Represents a node in the snapshot graph.

    Attributes:
        num: The number of the snapshot. Unique for this instance. Later
            snapshots always have a higher num.
        instance: Which instance this is a snapshot of.
        snapshot: The snapshot metadata reported by the instance.
        peers: The set of peers that the instance is connected to.
        consistent_peers: Keeps track of snapshots per peer that are consistent
            with this one.
    """
    num: int
    instance: Reference
    snapshot: SnapshotMetadata
    peers: FrozenSet[Reference]
    consistent_peers: Dict[Reference, List["SnapshotNode"]] = field(
            default_factory=dict, repr=False)

    def __hash__(self) -> int:
        return object.__hash__(self)

    @property
    def consistent(self) -> bool:
        """Returns True iff there is a consistent checkpoint with all peers.
        """
        return self.consistent_peers.keys() == self.peers

    def do_consistency_check(
            self,
            peer_node: "SnapshotNode",
            connections: List[_ConnectionType]) -> bool:
        """Check if the snapshot of the peer is consistent with us.

        When the peer snapshot is consistent, adds it to our list of consistent
        peer snapshots (in :attr:`consistent_peers`) and vice versa.

        Args:
            peer_node: Snapshot of one of our peers
            connections: All connections from our instance to the peer instance

        Returns:
            True iff the peer snapshot is consistent with ours.
        """
        i_snapshot = self.snapshot
        p_snapshot = peer_node.snapshot
        peer_is_restart = p_snapshot is _NULL_SNAPSHOT
        for connection in connections:
            i_port, p_port, conn = connection
            is_sending = bool(conn & _ConnectionInfo.SELF_IS_SENDING)
            i_msg_counts = i_snapshot.port_message_counts.get(str(i_port), [])
            p_msg_counts = p_snapshot.port_message_counts.get(str(p_port), [])
            if conn & _ConnectionInfo.SELF_IS_VECTOR:
                slot = int(peer_node.instance[-1])
                consistent = calc_consistency(
                        safe_get(i_msg_counts, slot, 0),
                        safe_get(p_msg_counts, 0, 0),
                        is_sending, peer_is_restart)
            elif conn & _ConnectionInfo.PEER_IS_VECTOR:
                slot = int(self.instance[-1])
                consistent = calc_consistency(
                        safe_get(i_msg_counts, 0, 0),
                        safe_get(p_msg_counts, slot, 0),
                        is_sending, peer_is_restart)
            else:
                consistent = calc_consistency_list(
                        i_msg_counts, p_msg_counts, is_sending, peer_is_restart)
            if not consistent:
                return False
        self.consistent_peers.setdefault(
                peer_node.instance, []).append(peer_node)
        peer_node.consistent_peers.setdefault(
                self.instance, []).append(self)
        return True


class SnapshotRegistry(Thread):
    """Registry of all snapshots taken by instances.

    Current snapshots are stored in a graph. Every node represents a snapshot
    taken by an instance (see :class:`SnapshotNode`). When snapshots from peer
    instances are consistent, the nodes are connected to each other.

    This class manages the snapshot nodes. New snapshots are registered through
    :meth:`register_snapshot`.
    """

    def __init__(
            self, config: PartialConfiguration, snapshot_folder: Path,
            topology_store: TopologyStore) -> None:
        """Create a snapshot graph using provided configuration.

        Args:
            config: ymmsl configuration describing the workflow.
        """
        super().__init__(name='SnapshotRegistry')

        if config.model is None or not isinstance(config.model, Model):
            raise ValueError('The yMMSL experiment description does not'
                             ' contain a (complete) model section, so there'
                             ' is nothing to run!')
        self._configuration = config
        self._model = config.model
        self._snapshot_folder = snapshot_folder
        self._topology_store = topology_store

        self._queue: Queue[_QueueItemType] = Queue()
        self._snapshots: _SnapshotDictType = {}

        self._instances: Set[Reference] = set()
        for component in config.model.components:
            self._instances.update(component.instances())

        # Create snapshot nodes for starting from scratch
        for instance in self._instances:
            self.register_snapshot(instance, _NULL_SNAPSHOT)

    def register_snapshot(
            self, instance: Reference, snapshot: SnapshotMetadata) -> None:
        """Register a new snapshot.

        Args:
            instance: The instance that created the snapshot
            snapshot: Metadata describing the snapshot
        """
        self._queue.put((instance, snapshot))

    def run(self) -> None:
        """Code executed in a separate thread
        """
        while True:
            item = self._queue.get()
            if item is None:
                return
            self._add_snapshot(*item)

    def shutdown(self) -> None:
        """Stop the snapshot registry thread
        """
        self._queue.put(None)

    def _add_snapshot(
            self, instance: Reference, snapshot: SnapshotMetadata) -> None:
        """Register a new snapshot.

        Args:
            instance: The instance that created the snapshot
            snapshot: Metadata describing the snapshot
        """
        stateful_peers = self._get_peers(instance)

        i_snapshots = self._snapshots.setdefault(instance, [])
        # get next number of the snapshot
        num = 1 if not i_snapshots else i_snapshots[-1].num + 1
        snapshotnode = SnapshotNode(num, instance, snapshot, stateful_peers)
        i_snapshots.append(snapshotnode)

        # check consistency with all peers
        for peer in stateful_peers:
            for peer_snapshot in self._snapshots.get(peer, []):
                snapshotnode.do_consistency_check(
                        peer_snapshot, self._get_connections(instance, peer))

        # finally, check if this snapshotnode is now part of a workflow snapshot
        if snapshot is not _NULL_SNAPSHOT:
            self._save_workflow_snapshot(snapshotnode)

    def _save_workflow_snapshot(self, snapshotnode: SnapshotNode) -> None:
        """Save snapshot if a workflow snapshot exists with the provided node.

        Args:
            snapshotnode: The snapshot node that must be part of the workflow
                snapshot.
        """
        workflow_snapshots = self._get_workflow_snapshots(snapshotnode)
        for workflow_snapshot in workflow_snapshots:
            self._write_snapshot_ymmsl(workflow_snapshot)
        self._cleanup_snapshots(workflow_snapshots)

    def _get_workflow_snapshots(
            self, snapshot: SnapshotNode) -> List[List[SnapshotNode]]:
        """Return all workflow snapshots which contain the provided node.

        Args:
            snapshotnode: The snapshot node that must be part of the workflow
                snapshot.

        Returns:
            List of workflow snapshots. Each workflow snapshot is a list of
            instance snapshot nodes.
        """
        if not snapshot.consistent:
            return []

        # Instances that don't have a snapshot node chosen yet:
        instances_to_cover = list(self._instances - {snapshot.instance})
        # Allowed snapshots per instance. This is updated during the heuristic
        # to further restrict the sets of snapshots as peer snapshots are
        # selected.
        # First restriction is that the snapshots have to be locally consistent.
        allowed_snapshots: Dict[Reference, FrozenSet[SnapshotNode]] = {}
        for instance in instances_to_cover:
            allowed_snapshots[instance] = frozenset(
                    i_snapshot
                    for i_snapshot in self._snapshots.get(instance, [])
                    if i_snapshot.consistent)
            if not allowed_snapshots[instance]:
                # there cannot be a workflow snapshot if this instance has no
                # consistent snapshot nodes
                return []
        instance = snapshot.instance
        allowed_snapshots[instance] = frozenset({snapshot})

        def num_allowed_snapshots(instance: Reference) -> int:
            """Get number of allowed snapshots at this point for this instance.

            The allowed snapshots are those that are consistent with all
            selected snapshots at this point in the heuristic.
            """
            return len(allowed_snapshots[instance])

        # Do a full, depth-first search for all workflow snapshots
        # ========================================================

        workflow_snapshots = []
        selected_snapshots = [snapshot]
        # This stack stores history of allowed_snapshots and enables roll back
        stack: List[Dict[Reference, FrozenSet[SnapshotNode]]] = []

        # Update allowed_snapshots for peers of the selected snapshot
        for peer, snapshots in snapshot.consistent_peers.items():
            intersection = allowed_snapshots[peer].intersection(snapshots)
            if not intersection:
                return []
            allowed_snapshots[peer] = intersection

        while True:
            # 1. Select most constrained instance
            #
            # Note: we're only interested in the instance with the least allowed
            # snapshots. Better performance may be possible by not doing a full
            # sort, but it should be tested. Expectation is that
            # instances_to_cover remains mostly sorted (as the only counts that
            # are changing are for peers of the previous selected instance).
            # Python's sort algorithm is O(N) when the list is already sorted
            # (which is the same as max()).
            #
            # We cannot use a priority queue (heapq) because
            # num_allowed_snapshots is changing every iteration.
            instances_to_cover.sort(key=num_allowed_snapshots, reverse=True)
            instance = instances_to_cover.pop()

            # 2. Select the oldest snapshot of this instance
            snapshot = min(allowed_snapshots[instance], key=attrgetter('num'))
            selected_snapshots.append(snapshot)
            # A shallow copy is ok: the values are immutable frozensets
            stack.append(allowed_snapshots.copy())

            # 3. Update allowed snapshots based on the newly selected
            allowed_snapshots[instance] = frozenset({snapshot})
            for peer, snapshots in snapshot.consistent_peers.items():
                intersection = allowed_snapshots[peer].intersection(snapshots)
                if not intersection:
                    break  # roll back
                allowed_snapshots[peer] = intersection
            else:
                # 4. Selected snapshot is okay to explore further
                if instances_to_cover:
                    # 4a. There are still instance to cover, return to the start
                    #     of the while loop.
                    continue
                # 4b. We have found a complete workflow snapshot
                workflow_snapshots.append(selected_snapshots.copy())
                # Next: perform a roll-back to continue the search

            # 5. Roll back
            # stop when selected_snapshots only contains the one we forced to be
            # part of the workflow snapshot
            while len(selected_snapshots) > 1:
                snapshot = selected_snapshots.pop()
                instance = snapshot.instance
                instances_to_cover.append(instance)
                allowed_snapshots = stack.pop()
                intersection = allowed_snapshots[instance] - {snapshot}
                allowed_snapshots[instance] = intersection
                if intersection:
                    # We have a valid next snapshot to try for this instance
                    break
                # No allowed_snapshots, try another roll back
            else:
                # Exhausted all roll back possibilities, so we are done now
                return workflow_snapshots

    def _write_snapshot_ymmsl(
            self, selected_snapshots: List[SnapshotNode]) -> None:
        """Write the snapshot ymmsl file to the snapshot folder.

        Args:
            selected_snapshots: All snapshot nodes of the workflow snapshot.
        """
        now = datetime.now()
        config = self._generate_snapshot_config(selected_snapshots, now)
        time = now.strftime('%Y%m%d_%H%M%S')
        for i in range(_MAX_FILE_EXISTS_CHECK):
            if i:
                snapshot_filename = f'snapshot_{time}_{i}.ymmsl'
            else:
                snapshot_filename = f'snapshot_{time}.ymmsl'
            savepath = self._snapshot_folder / snapshot_filename
            if not savepath.exists():
                save(config, savepath)
                return
        raise RuntimeError('Could not find an available filename for storing'
                           f' the next workflow snapshot: {savepath} already'
                           ' exists.')

    def _generate_snapshot_config(
                self, selected_snapshots: List[SnapshotNode], now: datetime
                ) -> PartialConfiguration:
        """Generate ymmsl configuration for snapshot file
        """
        selected_snapshots.sort(key=attrgetter('instance'))
        resume = {}
        for node in selected_snapshots:
            if node.snapshot is not _NULL_SNAPSHOT:
                # Only store resume information when it is an actual snapshot
                # created by the instance. Otherwise the instance can just be
                # restarted from the beginning.
                resume[node.instance] = Path(node.snapshot.snapshot_filename)
        description = self._generate_description(selected_snapshots, now)
        return PartialConfiguration(resume=resume, description=description)

    def _generate_description(
            self, selected_snapshots: List[SnapshotNode], now: datetime) -> str:
        """Generate a human-readable description of the workflow snapshot.
        """
        triggers: Dict[str, List[str]] = {}
        component_info = []
        max_instance_len = len('Instance ')
        for node in selected_snapshots:
            for trigger in node.snapshot.triggers:
                triggers.setdefault(trigger, []).append(str(node.instance))
            component_info.append((
                    str(node.instance),
                    f'{node.snapshot.timestamp:<11.6g}',
                    f'{node.snapshot.wallclock_time:<11.6g}',
                    ("Intermediate", "Final")[node.snapshot.is_final_snapshot]))
            max_instance_len = max(max_instance_len, len(str(node.instance)))
        instance_with_padding = 'Instance'.ljust(max_instance_len)
        component_table = [
                f'{instance_with_padding} t           Wallclock time  Type',
                f'{"-" * (max_instance_len + 41)}']
        component_table += [
                f'{name.ljust(max_instance_len)} {timestamp} {walltime}'
                f'     {typ}'
                for name, timestamp, walltime, typ in component_info]
        return (f'Workflow snapshot for {self._model.name}'
                f' taken on {now.strftime("%Y-%m-%d %H:%M:%S")}.\n'
                'Snapshot triggers:\n' +
                '\n'.join(f'- {trigger} ({", ".join(triggers[trigger])})'
                          for trigger in sorted(triggers)) +
                '\n\n' +
                '\n'.join(component_table) + '\n')

    def _cleanup_snapshots(
            self, workflow_snapshots: List[List[SnapshotNode]]) -> None:
        """Remove all snapshots that are older than the selected snapshots.

        Args:
            selected_snapshots: All snapshot nodes of a workflow snapshot
        """
        if not workflow_snapshots:
            return

        # Find the newest snapshots per instance
        newest_snapshots = {snapshot.instance: snapshot
                            for snapshot in workflow_snapshots[0]}
        for workflow_snapshot in workflow_snapshots[1:]:
            for snapshot in workflow_snapshot:
                if newest_snapshots[snapshot.instance].num < snapshot.num:
                    newest_snapshots[snapshot.instance] = snapshot

        # Remove all snapshots that are older than the newest snapshots
        removed_snapshots: Set[SnapshotNode] = set()
        for snapshot in newest_snapshots.values():
            all_snapshots = self._snapshots[snapshot.instance]
            idx = all_snapshots.index(snapshot)
            self._snapshots[snapshot.instance] = all_snapshots[idx:]
            removed_snapshots.update(all_snapshots[:idx])

        # Remove all references in SnapshotNode.peer_snapshot to the snapshots
        # that are cleaned up
        for snapshot in removed_snapshots:
            for peer_snapshot in chain.from_iterable(
                    snapshot.consistent_peers.values()):
                if peer_snapshot in removed_snapshots:
                    # snapshot is removed anyway, no need to update references
                    continue
                # peer_snapshot is still there, remove reference to us
                peer_snapshot.consistent_peers[snapshot.instance].remove(
                        snapshot)

    @lru_cache(maxsize=None)
    def _get_peers(self, instance: Reference) -> FrozenSet[Reference]:
        """Return the set of peers for the given instance.

        Note: instance is assumed to contain the full index, not just the
        component name.

        Args:
            instance: Instance to get peers of.

        Returns:
            Frozen set with all peer instances (including their index).
        """
        return frozenset(self._topology_store.get_peer_instances(instance))

    @lru_cache(maxsize=None)
    def _get_connections(self, instance: Reference, peer: Reference
                         ) -> List[_ConnectionType]:
        """Get the list of connections between instance and peer.

        Args:
            instance: Instance reference (including index)
            peer: Peer reference (including index)

        Returns:
            A list of tuples describing all conduits between instance and peer:
                instance_port (Reference): the port of instance that is
                    connected to
                peer_port (Reference): the port on the peer instance
                info (_ConnectionInfo): flag describing the connection. The
                    instance is sending when
                    ``info & _ConnectionInfo.SELF_IS_SENDING`` and receiving
                    otherwise. When the instance port is a vector port and the
                    peer port is a non-vector port, the flag
                    ``_ConnectionInfo.SELF_IS_VECTOR`` is set. In the reverse
                    situation the flag ``_ConnectionInfo.PEER_IS_VECTOR`` is
                    set. When both ports are vector or non-vector, neither flag
                    is set.
        """
        instance_kernel = instance.without_trailing_ints()
        peer_kernel = peer.without_trailing_ints()

        connected_ports: List[_ConnectionType] = []
        for conduit in self._model.conduits:
            if (conduit.sending_component() == instance_kernel and
                    conduit.receiving_component() == peer_kernel):
                conn_type = _ConnectionInfo.SELF_IS_SENDING
            elif (conduit.receiving_component() == instance_kernel and
                    conduit.sending_component() == peer_kernel):
                conn_type = _ConnectionInfo(0)
            else:
                continue
            instance_ndim = (len(instance) - len(instance_kernel))
            peer_ndim = (len(peer) - len(peer_kernel))
            if instance_ndim < peer_ndim:
                conn_type |= _ConnectionInfo.SELF_IS_VECTOR
            if instance_ndim > peer_ndim:
                conn_type |= _ConnectionInfo.PEER_IS_VECTOR
            # we cannot distinguish scalar-scalar vs. vector-vector
            # but it does not matter for this logic :)
            if conn_type & _ConnectionInfo.SELF_IS_SENDING:
                connected_ports.append((
                        conduit.sending_port(),
                        conduit.receiving_port(),
                        conn_type))
            else:
                connected_ports.append((
                        conduit.receiving_port(),
                        conduit.sending_port(),
                        conn_type))
        return connected_ports

    @lru_cache(maxsize=None)
    def _implementation(self, kernel: Reference) -> Optional[Implementation]:
        """Return the implementation of a kernel.

        Args:
            kernel: The kernel to get the implementation for.

        Returns:
            Implementation for the kernel, or None if not provided in the
            configuration.
        """
        implementation = None
        for component in self._model.components:
            if component.name == kernel:
                implementation = component.implementation
        if implementation in self._configuration.implementations:
            return self._configuration.implementations[implementation]
        return None
