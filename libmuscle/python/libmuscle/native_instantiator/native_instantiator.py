"""Module for examining resources and instantiating instances on them

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
MUSCLE3     core            (uses list of hwthread ids)

Linux       core            core id

Hwloc       core            core L#<x>

OpenMPI     core            used in rankfile if
                            --use-hwthread-cpus not
                            specified

psutil      physical        counted by psutil.cpu_count(logical=False)
            core
```

"""
import logging
import multiprocessing as mp
from os import chdir
from pathlib import Path
import queue
import sys
from time import sleep
import traceback
from typing import Dict, List, Optional

from libmuscle.errors import ConfigurationError
from libmuscle.manager.instantiator import (
        CancelAllRequest, CrashedResult, create_instance_env, InstantiationRequest,
        Process, ProcessStatus, reconfigure_logging, ShutdownRequest)
from libmuscle.native_instantiator.agent_manager import AgentManager
from libmuscle.native_instantiator.global_resources import global_resources
from libmuscle.native_instantiator.run_script import make_script, prep_resources
from libmuscle.planner.planner import Resources
from ymmsl import MPICoresResReq, MPINodesResReq, ResourceRequirements, ThreadedResReq


_logger = logging.getLogger(__name__)


class NativeInstantiator(mp.Process):
    """Instantiates instances on the local machine."""
    def __init__(
            self, resources: mp.Queue, requests: mp.Queue, results: mp.Queue,
            log_records: mp.Queue, run_dir: Path) -> None:
        """Create a NativeInstantiator

        Args:
            resources: Queue for returning the available resources
            requests: Queue to take requests from
            results: Queue to communicate finished processes over
            log_messages: Queue to push log messages to
            run_dir: Run directory for the current run
        """
        super().__init__(name='NativeInstantiator')
        self._resources_out = resources
        self._requests_in = requests
        self._results_out = results
        self._log_records_out = log_records
        self._run_dir = run_dir

        self._processes: Dict[str, Process] = dict()

    def run(self) -> None:
        """Entry point for the process"""
        try:
            m3_dir = self._run_dir / 'muscle3'
            m3_dir.mkdir(exist_ok=True)
            chdir(m3_dir)

            self._agent_manager = AgentManager(m3_dir)

            reconfigure_logging(self._log_records_out)
            self._send_resources()
            self._main()

        except ConfigurationError as e:
            self._results_out.put(CrashedResult(e))

        except:     # noqa
            for line in traceback.format_exception(*sys.exc_info()):
                _logger.error(line)

            result = CrashResult(sys.exc_info()[1])
            self._resources_out.put(result)
            self._results_out.put(result)

    def _main(self) -> None:
        """Main function for the background process.

        This accepts requests for instantiating jobs, stopping them, or shutting down.
        Results of finished jobs are returned via the results queue.
        """
        shutting_down = False
        done = False
        while not done:
            while not shutting_down:
                try:
                    request = self._requests_in.get_nowait()
                    if isinstance(request, ShutdownRequest):
                        _logger.debug('Got ShutdownRequest')
                        shutting_down = True

                    elif isinstance(request, CancelAllRequest):
                        _logger.debug('Got CancelAllRequest')
                        self._agent_manager.cancel_all()

                    elif isinstance(request, InstantiationRequest):
                        _logger.debug('Got InstantiationRequest')
                        if not shutting_down:
                            self._instantiate(request)

                except queue.Empty:
                    break

            self._report_failed_processes()
            self._report_finished_processes()

            if shutting_down:
                _logger.debug(f'Remaining processes: {self._processes}')
                done = not self._processes

            if not done:
                sleep(0.1)

        self._agent_manager.shutdown()

    def _send_resources(self) -> None:
        """Detect resources and report them to the manager.

        We have potentially two sources of truth here: the Slurm environment variables
        and what the agents report based on what they're bound to. These should be
        consistent, but we check that and then try to be conservative to try to not
        step outside our bounds even if the cluster doesn't constrain processes to their
        assigned processors.
        """
        already_logged_smt = False
        resources = Resources()

        agent_cores = self._agent_manager.get_resources()

        env_ncpus = dict(
                zip(global_resources().nodes, global_resources().logical_cpus_per_node)
                )

        for node in env_ncpus:
            if node not in agent_cores:
                _logger.warning(
                        f'The environment suggests we should have node {node},'
                        ' but no agent reported running on it. We won''t be able'
                        ' to use this node.')
            else:
                resources.cores[node] = set(agent_cores[node])

                env_nncpus = env_ncpus[node]
                ag_nncores = len(agent_cores[node])
                ag_nnthreads = sum((len(ts) for ts in agent_cores[node]))

                if ag_nncores != ag_nnthreads and ag_nnthreads == env_nncpus:
                    if not already_logged_smt:
                        _logger.info(
                                'Detected SMT (hyperthreading) as available and'
                                ' enabled. Note that MUSCLE3 will assign whole cores to'
                                ' each thread or MPI process.')
                        already_logged_smt = True

                elif ag_nncores < env_nncpus:
                    _logger.warning(
                            f'Node {node} should have {env_nncpus} cores available,'
                            f' but the agent reports only {ag_nncores} available to it.'
                            f' We\'ll use the {ag_nncores} we seem to have.')

                    resources.cores[node] = set(agent_cores[node])

                elif env_nncpus < ag_nncores:
                    _logger.warning(
                            f'Node {node} should have {env_nncpus} cores available,'
                            f' but the agent reports {ag_nncores} available to it.'
                            ' Maybe the cluster does not constrain resources? We\'ll'
                            f' use the {env_nncpus} that we should have got.')
                    resources.cores[node] = set(agent_cores[node][:env_nncpus])

        for node in agent_cores:
            if node not in env_ncpus:
                _logger.warning(
                        f'An agent is running on node {node} but the environment'
                        ' does not list it as ours. It seems that the node\'s'
                        ' hostname does not match what SLURM calls it. We will not use'
                        ' this node, because we\'re not sure it\'s really ours.')

        self._resources_out.put(resources)

    def _instantiate(self, request: InstantiationRequest) -> None:
        """Instantiate an implementation according to the request."""
        name = str(request.instance)

        env = create_instance_env(request.instance, request.implementation.env)
        self._add_resources(env, request.res_req)

        rankfile = request.instance_dir / 'rankfile'

        if global_resources().on_cluster():
            rankfile_contents, resource_env = prep_resources(
                  request.implementation.execution_model, request.resources,
                  rankfile)

            if rankfile_contents:
                with rankfile.open('w') as f:
                    f.write(rankfile_contents)
                env['MUSCLE_RANKFILE'] = str(rankfile)

            env.update(resource_env)

        run_script_file = self._write_run_script(request, rankfile)
        args = [str(run_script_file)]

        self._processes[name] = Process(request.instance, request.resources)

        _logger.debug(f'Instantiating {name} on {request.resources}')
        try:
            self._agent_manager.start(
                    next(iter(request.resources.cores.keys())),
                    name, request.work_dir, args, env,
                    request.stdout_path, request.stderr_path)
            self._processes[name].status = ProcessStatus.RUNNING

        except Exception as e:
            _logger.warning(f'Instance {name} failed to start: {e}')
            self._processes[name].status = ProcessStatus.ERROR
            self._processes[name].error_msg = f'Instance failed to start: {e}'

    def _write_run_script(
            self, request: InstantiationRequest, rankfile: Optional[Path]) -> Path:
        """Create and write out the run script and return its location."""
        # TODO: Only write out once for each implementation
        if request.implementation.script:
            run_script = request.implementation.script
        else:
            run_script = make_script(
                    request.implementation, request.res_req,
                    not global_resources().on_cluster(), rankfile)

        run_script_file = request.instance_dir / 'run_script.sh'

        with run_script_file.open('w') as f:
            f.write(run_script)

        run_script_file.chmod(0o700)
        return run_script_file

    def _add_resources(
            self, env: Dict[str, str], res_req: ResourceRequirements) -> None:
        """Add resource env vars to the given env."""
        if isinstance(res_req, ThreadedResReq):
            num_threads = res_req.threads
        elif isinstance(res_req, (MPICoresResReq, MPINodesResReq)):
            num_threads = res_req.threads_per_mpi_process

        env['MUSCLE_THREADS'] = str(num_threads)
        env['OMP_NUM_THREADS'] = str(num_threads)

        num_mpi_processes: Optional[int] = None
        if isinstance(res_req, MPICoresResReq):
            num_mpi_processes = res_req.mpi_processes
        elif isinstance(res_req, MPINodesResReq):
            num_mpi_processes = res_req.nodes * res_req.mpi_processes_per_node

        if num_mpi_processes is not None:
            env['MUSCLE_MPI_PROCESSES'] = str(num_mpi_processes)

    def _report_failed_processes(self) -> None:
        """Get processes that failed to start and report their status."""
        failed_processes: List[str] = list()

        for name, process in self._processes.items():
            if process.status == ProcessStatus.ERROR:
                self._results_out.put(process)
                failed_processes.append(name)

        for name in failed_processes:
            del self._processes[name]

    def _report_finished_processes(self) -> None:
        """Get finished processes and report back their status."""
        for name, exit_code in self._agent_manager.get_finished():
            process = self._processes[name]
            if process.status == ProcessStatus.RUNNING:
                if exit_code == 0:
                    process.status = ProcessStatus.SUCCESS
                else:
                    process.status = ProcessStatus.ERROR
                    process.error_msg = 'Instance returned a non-zero exit code'
            process.exit_code = exit_code
            self._results_out.put(process)
            del self._processes[name]
