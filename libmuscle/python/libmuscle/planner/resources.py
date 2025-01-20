"""Module for describing compute resources

There's a huge comment here because there's a big mess here that took me forever to
figure out, so now I'm going to document it for the future.


Identifying hardware resources

Today's computers all contain multi-core CPUs, often with symmetric multithreading
(SMT), also known as hyperthreading. This means that we have hardware threads
(hwthreads) and also cores, and then there's caches and memory as well but we're not
going into NUMA here.

Cores and hwthreads are identified by number, but they have multiple different numbers
that are referred to by different names in different contexts, making everything very
confusing. So here are some definitions to disambiguate things.  Note that this is still
a rather simplified representation, but it's enough for what we're doing here in
MUSCLE3.


Hardware threads

A *hardware thread (hwthread)* is, at the hardware level, an instruction decoder. It
points to wherever in the code we are currently executing, and it can read the next
couple of instructions and figure out how to execute them. It can't actually execute
anything however, because it doesn't have the hardware that does that.

Intel refers to hwthreads as "logical processors" and so does Linux, hwloc calls them
"processing units" or PUs and so does OpenMPI unless it uses the term hwthread just to
confuse things a bit more.

Cores

A *core* contains at least one hwthread, and at least one functional unit, which is a
hardware component that actually does calculations and other data processing. Within a
core, the hwthread(s) read instructions and pass them to the functional units to be
executed. If a core has more than one hwthread, then the CPU supports SMT.

Intel refers to cores as "physical processors", hwloc calls them cores and so do most
other sources. We'll use cores here.

Since a hwthread cannot do anything on its own, it's always part of a core.

CPUs

The term CPU is used in many ways by various bits of documentation, sometimes referring
to a hwthread or a core, but here we'll take it to mean a collection of cores in a
plastic box. Similar terms are *package* (referring to that plastic box with very many
metal pins) and *socket* (the thing the package mounts into), or *processor*, which was
originally used to refer to all of the above when CPUs still had only one core with only
one hwthread, and has now become ambiguous.

Weird things can happen here, I've seen CPUs that as far as I can tell are a single
package, but nevertheless claim to have two sockets. I suspect that that's two physical
chips in a single plastic box, but I don't know for sure.

Here, we're concerned with hwthreads and cores and how to identify them and assign
instances to them.


Linux

On modern operating systems, hardware access is mediated by the operating system, and
we're mainly concerned with Linux here because that is what all the clusters are running
(see the note on macOS below). Information about the CPU(s) can be obtained on Linux
from the /proc/cpuinfo file, or equivalently but more modernly, from the files in
/sys/devices/system/cpu/cpu<x>/topology/.

Linux collects information about processors because it needs to run processes (programs,
software threads) on them on behalf of the user. Processes are assigned to hwthreads, so
that is what Linux considers a *processor*.  /proc/cpuinfo lists all these processors,
and they each have their own directory /sys/devices/system/cpu/cpu<x>.

On Linux, processors have an id, which is that number <x> in the directory, and is
listed under "processor" in /proc/cpuinfo. Since this number identifies a hwthread and
is assigned by Linux rather than being baked into the hardware, I'm calling it a
"logical hwthread id", this being a logical id of a hwthread, not an id of a logical
hwthread. It's also the id of a logical processor in Intel-speak.

Hwthreads actually have a second number associated with them, which does come from the
hardware. In /proc/cpuinfo, that's listed under "apicid"; it doesn't seem to be
available from sysfs. Hwloc call this the "physical PU (its name for a hwthread) id",
and OpenMPI's mpirun manpage also refers to it as a "physical processor location".

There's great potential for confusion here: the "physical PU id" and "physical processor
location" both identify a hardware-specified number (a physical id or a physical
location) for a hwthread. This is something completely different than what Intel calls a
"physical processor", which they use to refer to a core.

MUSCLE3 uses logical hwthread ids everywhere, it does not use physical ids.

Linux knows about how hwthreads are grouped into bigger things of course. Cores are
identified in Linux using the "core id", which is listed in /proc/cpuinfo and in
/sys/devices/system/cpu/cpu<x>/topology/core_id. So for each hwthread, identified by its
logical id, we can look up which core it is a part of. The core id is a logical id,
assigned by Linux, not by the hardware.  While logical hwthread ids seem to always be
consecutive at least on the hardware I've seen so far, core ids may have gaps.

MUSCLE3 does not use core ids, although it uses groups of hwthread ids that contain all
the hwthreads for a given core.


Resource binding

Running processes need something to run on, a hwthread. The assignment of process to
hwthread is done by the operating system's scheduler: when a process is ready to run,
the scheduler will try to find it a free hwthread to run on.

The scheduler can be constrained in which hwthreads it considers for a given process,
which is known as binding the process. This may have performance benefits, because
moving a process from one hwthread to another takes time. In MUSCLE3, when running on a
cluster, each process is assigned its own specific set of hwthreads to run on, and we
try to bind the instance to the assigned hwthreads.

Taskset

How this is done depends on how the instance is started. For non-MPI instances, we use a
Linux utility named 'taskset' that starts another program with a giving binding. The
binding is expressed as an *affinity mask*, a string of bits that say whether a given
processor (hwthread) can be used by the process or not. Each position in the string of
bits corresponds to the hwthread with that logical id.

OpenMPI

OpenMPI can bind cores in various ways, we use a rankfile and the --use-hwthread-cpus
option to specify the logical hwthread ids we want to bind each MPI process (rank) to.
Note that OpenMPI by default binds to cores, and can also bind to various other things
including sockets.

MPICH

MPICH doesn't support binding, as far as I can see.

Intel MPI

Intel MPI uses logical hwthread ids-based masks, specified in an environment variable,
to go with a machinefile that lists the nodes to put each process on.

Slurm srun

Slurm's srun has a CPU_BIND environment variable that likewise contains logical hwthread
ids-based masks, and a hostfile that lists the nodes to put each process on.

Here are some disambiguation tables to help with the confusion:


```
MUSCLE3     hwthread        logical hwthread id         physical hwthread id

Linux       processor       processor                   apicid
                                                        (/proc/cpuinfo only)

cgroups                     always uses these

taskset                     always uses these

hwloc       PU              PU L#<x>                    PU P#<x>

OpenMPI     hwthread        used in rankfile if         used in rankfile if
                            --use-hwthread-cpus         rmaps_rank_file_physical
                            is specified                MCA param set

Intel       logical         logical processor
            processor       number

srun                        used by --bind-to

psutil      logical         returned by Process.cpu_affinity()
            core            counted by psutil.cpu_count(logical=True)
```


```
MUSCLE3     core            core id

Linux       core            core id

Hwloc       core            core L#<x>

OpenMPI     core            used in rankfile if
                            --use-hwthread-cpus not
                            specified

psutil      physical        counted by psutil.cpu_count(logical=False)
            core
```

"""
from copy import copy, deepcopy
from typing import Dict, Iterable, Iterator, List, Optional, Set, Tuple


class Core:
    """Describes a CPU core or designates a core or one or more hwthreads.

    A core is a group of functional units with one or more instruction decoders. If the
    core supports symmetric multithreading (SMT, aka hyperthreading) then there will be
    more than one instruction decoder or hardware thread in the core.

    Note that the term "logical CPU" refers to an instruction decoder/hwthread. If the
    processor does not support SMT, then each core has a single decoder and so a logical
    CPU is also a core.

    This class can be used in different ways with slighly different interpretations.
    When describing hardware resources, it describes a core and all of its hwthreads. In
    this case, cid is the core id, and hwthreads contains the hwthread ids of all
    hwthreads on this core. If no SMT is supported, then there will be only one
    hwthread id.

    When designating a whole core (e.g. for use by a process), cid is set to the id of
    the core, and hwthreads contains all of the hwthreads on that core. When designating
    a hwthread on a particular core, cid is set to the id of the core and hwthreads
    contains the designated (single) hwthread.

    MUSCLE3 never assigns swthreads to subsets of hwthreads on a core, it assigns them
    to either a single hwthread or a single whole core. So if more than one hwthread is
    given, then we can assume that those are all the hwthreads on that core.

    Objects of this class automatically deepcopy when copied. This means that you can
    make a copy using copy.copy() and modify that copy anywhere without changing the
    original.

    Args:
        cid: ID of this core, to be used to refer to it
        hwthreads: Ids of hwthreads (logical CPUs) belonging to this core
    """
    def __init__(self, cid: int, hwthreads: Set[int]) -> None:
        """Create a Core"""
        self.cid = cid
        self.hwthreads = copy(hwthreads)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Core):
            return NotImplemented

        return self.cid == other.cid and self.hwthreads == other.hwthreads

    def __len__(self) -> int:
        return len(self.hwthreads)

    def __copy__(self) -> 'Core':
        return Core(self.cid, self.hwthreads)

    def __or__(self, other: object) -> 'Core':
        if not isinstance(other, Core):
            return NotImplemented

        if other.cid != self.cid:
            raise ValueError('Cannot merge hwthreads on different cores')

        return Core(self.cid, self.hwthreads | other.hwthreads)

    def __ior__(self, other: object) -> 'Core':
        if not isinstance(other, Core):
            return NotImplemented

        if other.cid != self.cid:
            raise ValueError('Cannot merge hwthreads on different cores')

        self.hwthreads |= other.hwthreads
        return self

    def __isub__(self, other: object) -> 'Core':
        if not isinstance(other, Core):
            return NotImplemented

        if other.cid != self.cid:
            raise ValueError('Cannot merge hwthreads on different cores')

        self.hwthreads -= other.hwthreads
        return self

    def __str__(self) -> str:
        hwthreads = ','.join(map(str, sorted(self.hwthreads)))
        return f'{self.cid}({hwthreads})'

    def __repr__(self) -> str:
        hwthreads = ','.join(map(str, sorted(self.hwthreads)))
        return f'Core({self.cid}, {{{hwthreads}}})'

    def isdisjoint(self, other: 'Core') -> bool:
        """Returns whether we share resources with other."""
        if self.cid != other.cid:
            raise ValueError('Cannot compare hwthreads on different cores')

        return self.hwthreads.isdisjoint(other.hwthreads)


class CoreSet:
    """A set of cores on a single node.

    This exists to make it a bit easier to operate on sets of cores, merging and
    subtracting them.

    Objects of this class automatically deepcopy when copied. This means that you can
    make a copy using copy.copy() and modify that copy anywhere without changing the
    original.
    """
    def __init__(self, cores: Iterable[Core]) -> None:
        """Create a CoreSet

        Args:
            cores: A set of cores to contain.
        """
        self._cores = {c.cid: c for c in cores}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CoreSet):
            return NotImplemented

        if len(self._cores) != len(other._cores):
            return False

        for cid, core in self._cores.items():
            if cid not in other._cores:
                return False
            if core.hwthreads != other._cores[cid].hwthreads:
                return False

        return True

    def __len__(self) -> int:
        return len(self._cores)

    def __iter__(self) -> Iterator[Core]:
        return iter(self._cores.values())

    def __copy__(self) -> 'CoreSet':
        return CoreSet(deepcopy(list(self._cores.values())))

    def __ior__(self, other: object) -> 'CoreSet':
        if not isinstance(other, CoreSet):
            return NotImplemented

        for cid, core in other._cores.items():
            if cid in self._cores:
                self._cores[cid] |= core
            else:
                self._cores[cid] = copy(core)

        return self

    def __isub__(self, other: object) -> 'CoreSet':
        if not isinstance(other, CoreSet):
            return NotImplemented

        for cid, core in other._cores.items():
            if cid in self._cores:
                self._cores[cid] -= core
                if not self._cores[cid].hwthreads:
                    del self._cores[cid]

        return self

    def __str__(self) -> str:
        def collapse_ranges(ids: List[int]) -> str:
            if len(ids) == 0:
                return ''

            result = list()
            start = 0
            i = 1
            while i <= len(ids):
                if (i == len(ids)) or (ids[i-1] != ids[i] - 1):
                    if start == i - 1:
                        # run of one
                        result.append(str(ids[i-1]))
                    else:
                        # run of at least two
                        result.append(f'{ids[start]}-{ids[i-1]}')
                    start = i
                i += 1
            return ','.join(result)

        cores = sorted((c.cid for c in self._cores.values()))
        hwthreads = sorted((t for c in self._cores.values() for t in c.hwthreads))

        return f'{collapse_ranges(cores)}({collapse_ranges(hwthreads)})'

    def __repr__(self) -> str:
        cores = ', '.join(map(repr, sorted(self._cores.values(), key=lambda c: c.cid)))
        return f'CoreSet({{{cores}}})'

    def isdisjoint(self, other: 'CoreSet') -> bool:
        """Returns whether we share resources with other."""
        for cid, core in self._cores.items():
            if cid in other._cores:
                if not core.isdisjoint(other._cores[cid]):
                    return False
        return True

    def get_first_cores(self, num_cores: int) -> 'CoreSet':
        """Returns the first num_cores cores in this set.

        Args:
            The number of cores to select.
        """
        result = copy(self)
        cids = list(self._cores.keys())
        selected = cids[:num_cores]
        if len(selected) < num_cores:
            raise RuntimeError('Tried to get more cores than available')

        result._cores = {c.cid: c for c in result._cores.values() if c.cid in selected}
        return result


class OnNodeResources:
    """Resources on a single node, currently only CPU cores.

    This represents a set of resources on a single node, either all of the resources
    available or some subset of interest.

    Objects of this class automatically deepcopy when copied. This means that you can
    make a copy using copy.copy() and modify that copy anywhere without changing the
    original.
    """
    def __init__(self, node_name: str, cpu_cores: CoreSet) -> None:
        """Create an OnNodeResources.

        Args:
            name: (Host)name of the node.
            cpu_cores: A set of cores for this node.
        """
        self.node_name = node_name
        self.cpu_cores = cpu_cores

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OnNodeResources):
            return NotImplemented

        return (
                isinstance(other, OnNodeResources) and
                self.node_name == other.node_name and
                self.cpu_cores == other.cpu_cores)

    def __copy__(self) -> 'OnNodeResources':
        return OnNodeResources(self.node_name, copy(self.cpu_cores))

    def __ior__(self, other: object) -> 'OnNodeResources':
        if not isinstance(other, OnNodeResources):
            return NotImplemented

        if self.node_name != other.node_name:
            raise ValueError('Cannot merge resources on different nodes')

        self.cpu_cores |= other.cpu_cores
        return self

    def __isub__(self, other: object) -> 'OnNodeResources':
        if not isinstance(other, OnNodeResources):
            return NotImplemented

        if self.node_name != other.node_name:
            raise ValueError('Cannot remove resources on different nodes')

        self.cpu_cores -= other.cpu_cores
        return self

    def __str__(self) -> str:
        return f'OnNodeResources({self.node_name}, c: {str(self.cpu_cores)})'

    def __repr__(self) -> str:
        return f'OnNodeResources("{self.node_name}", {repr(self.cpu_cores)})'

    def hwthreads(self) -> Iterable[int]:
        """Return the hwthreads in this node."""
        return (thread for core in self.cpu_cores for thread in core.hwthreads)

    def total_cores(self) -> int:
        """Return the number of CPU cores in this node."""
        return len(self.cpu_cores)

    def isdisjoint(self, other: 'OnNodeResources') -> bool:
        """Returns whether we share resources with other."""
        return (
                self.node_name != other.node_name or
                self.cpu_cores.isdisjoint(other.cpu_cores))


class Resources:
    """Designates a (sub)set of resources.

    Whether these resources are free or allocated in general or by something specific
    depends on the context, this just says which resources we're talking about.

    Objects of this class automatically deepcopy when copied. This means that you can
    make a copy using copy.copy() and modify that copy anywhere without changing the
    original.

    Attributes:
        nodes: A collection of nodes to include in this resource set
    """
    def __init__(self, nodes: Optional[Iterable[OnNodeResources]] = None) -> None:
        """Create a Resources object with the given nodes.

        Args:
            nodes: OnNodeResourcess to be designated by this object.
        """
        if nodes is None:
            self._nodes: Dict[str, OnNodeResources] = {}
        else:
            self._nodes = {n.node_name: n for n in nodes}

    def __len__(self) -> int:
        return len(self._nodes)

    def __iter__(self) -> Iterator[OnNodeResources]:
        return iter(self._nodes.values())

    def __getitem__(self, node_name: str) -> OnNodeResources:
        return self._nodes[node_name]

    def __eq__(self, other: object) -> bool:
        """Check for equality."""
        if not isinstance(other, Resources):
            return NotImplemented

        if len(self._nodes) != len(other._nodes):
            return False

        for node_name, node in self._nodes.items():
            if node_name not in other._nodes:
                return False
            if other._nodes[node_name] != node:
                return False

        return True

    def __copy__(self) -> 'Resources':
        """Copy the object."""
        return Resources((copy(n) for n in self._nodes.values()))

    def __ior__(self, other: object) -> 'Resources':
        """Add the resources in the argument to this object."""
        if not isinstance(other, Resources):
            return NotImplemented

        for node_name, other_node in other._nodes.items():
            if node_name in self._nodes:
                self._nodes[node_name] |= other_node
            else:
                self._nodes[node_name] = copy(other_node)

        return self

    def __isub__(self, other: object) -> 'Resources':
        """Remove the resources in the argument from this object."""
        if not isinstance(other, Resources):
            return NotImplemented

        for node_name, other_node in other._nodes.items():
            if node_name in self._nodes:
                self._nodes[node_name] -= other_node
                if not self._nodes[node_name]:
                    del self._nodes[node_name]

        return self

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        nodes = ','.join(
                map(str, sorted(self._nodes.values(), key=lambda n: n.node_name)))
        return f'Resources({nodes})'

    def __repr__(self) -> str:
        """Return a string representation."""
        nodes = sorted(self._nodes.values(), key=lambda n: n.node_name)
        return f'Resources({nodes})'

    def nodes(self) -> Iterable[str]:
        """Return the names of the nodes on which we designate resources."""
        return self._nodes.keys()

    def total_cores(self) -> int:
        """Return the total number of cores (not hwthreads) designated."""
        return sum((len(n.cpu_cores) for n in self._nodes.values()))

    def cores(self) -> Iterable[Tuple[str, int]]:
        """Return this resources as a list of node, core."""
        return (
                (node.node_name, core.cid)
                for node in self._nodes.values() for core in node.cpu_cores)

    def hwthreads(self) -> Iterable[Tuple[str, int]]:
        """Return this resources as a list of node, hwthread."""
        return (
                (node.node_name, hwthread)
                for node in self._nodes.values() for hwthread in node.hwthreads())

    def isdisjoint(self, other: 'Resources') -> bool:
        """Return whether we share resources with other."""
        for node_name, node in self._nodes.items():
            if node_name in other._nodes:
                if not node.isdisjoint(other._nodes[node_name]):
                    return False
        return True

    def add_node(self, node_res: OnNodeResources) -> None:
        """Add a node's resources.

        This absorbs node_res into this Resources object, so if you change node_res
        after adding it, the changes will be reflected in this Resources.

        Args:
            node_res: Resources on a node not yet included in this Resources.

        Raises:
            RuntimeError: if we already have a node with this node name.
        """
        if node_res.node_name in self._nodes:
            raise RuntimeError(
                    'Tried to add a OnNodeResources to a Resources for a node that is'
                    ' already present. This is a bug in MUSCLE3, please report it on'
                    ' GitHub.')

        self._nodes[node_res.node_name] = node_res

    def merge_node(self, node_res: OnNodeResources) -> None:
        """Merges a node's resources

        This always copies the object.

        Args:
            node_res: Resources on a node that may already be included in this
                    Resources.
        """
        if node_res.node_name in self._nodes:
            self._nodes[node_res.node_name] |= node_res
        else:
            self._nodes[node_res.node_name] = copy(node_res)

    @staticmethod
    def union(resources: Iterable['Resources']) -> 'Resources':
        """Combines the resources into one.

        Args:
            resources: A collection of resources to merge.

        Return:
            A Resources object referring to all the resources in the
            input.
        """
        result = Resources()
        for cur_resources in resources:
            result |= cur_resources
        return result
