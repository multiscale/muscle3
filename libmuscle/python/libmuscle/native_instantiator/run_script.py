import logging
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from libmuscle.errors import ConfigurationError
from libmuscle.native_instantiator.slurm import slurm
from libmuscle.planner.planner import ResourceAssignment
from ymmsl import (
        BaseEnv, ExecutionModel, Implementation, MPICoresResReq, MPINodesResReq,
        ResourceRequirements, ThreadedResReq)


def direct_prep_resources(resources: ResourceAssignment) -> Tuple[str, Dict[str, str]]:
    """Create resources for a non-MPI program with taskset.

    Taskset expects a set of hwthreads on the command line, either as a comma-separated
    list or as a hexadecimal mask. We generate both here and set two environment
    variables.

    Args:
        resources: The resource assignment to describe

    Return:
        No rank file, and a set of environment variables.
    """
    env: Dict[str, str] = dict()
    only_node_hwthreads_list = list(resources.by_rank[0].hwthreads())

    env['MUSCLE_BIND_LIST'] = ','.join(map(str, only_node_hwthreads_list))

    mask_int = sum((1 << c for c in only_node_hwthreads_list))
    env['MUSCLE_BIND_MASK'] = format(mask_int, 'X')

    return '', env


def openmpi_prep_resources(resources: ResourceAssignment) -> Tuple[str, Dict[str, str]]:
    """Create resource description for OpenMPI mpirun

    Args:
        resources: The resource assignment to describe

    Return:
        The contents of the rankfile, and a set of environment variables
    """
    ranklines: List[str] = list()
    all_cores = (
            (node_res, ','.join(map(str, sorted(node_res.hwthreads()))))
            for node_res in resources.by_rank)

    for i, (node_res, hwthreads) in enumerate(all_cores):
        ranklines.append(f'rank {i}={node_res.node_name} slot={hwthreads}')

    rankfile = '\n'.join(ranklines) + '\n'

    return rankfile, dict()


def impi_prep_resources(resources: ResourceAssignment) -> Tuple[str, Dict[str, str]]:
    """Create resource description for Intel MPI mpirun

    Args:
        resources: The resource assignment to describe

    Return:
        The contents of the machinefile, and a set of environment variables
    """
    env: Dict[str, str] = dict()
    machine_nodes: List[str] = list()
    pin_masks: List[int] = list()

    for rank, res in enumerate(resources.by_rank):
        machine_nodes.append(res.node_name)
        pin_masks.append(sum((1 << c for c in res.hwthreads())))

    # coalesce machine lines
    proc_counts = [1] * len(machine_nodes)
    i = 1
    while i < len(machine_nodes):
        if machine_nodes[i-1] == machine_nodes[i]:
            del machine_nodes[i]
            proc_counts[i-1] += proc_counts[i]
            del proc_counts[i]
        else:
            i += 1

    machinefile = '\n'.join(
            (f'{m}:{c}' for m, c in zip(machine_nodes, proc_counts))) + '\n'

    # disable pinning to SLURM-specified resources
    # env['I_MPI_PIN_RESPECT_CPUSET'] = '0'
    env['I_MPI_JOB_RESPECT_PROCESS_PLACEMENT'] = 'off'

    # which cores to bind each rank to
    pin_masks_str = ','.join(format(mask, '#x') for mask in pin_masks)
    env['I_MPI_PIN_DOMAIN'] = f'[{pin_masks_str}]'

    # I_MPI_PIN_DOMAIN=[55,aa]
    # pins the first rank to 0,2,16,18 and the second to 1,3,17,19
    # I_MPI_PIN_PROCESSOR_LIST=0,1,5,6
    # pins rank 0 to core 0, rank 1 to core 1, rank 2 to core 5, rank 3 to core 6
    # machinefile:
    # host1:2
    # host2:4
    # runs two processes on host1 and four on host2
    return machinefile, env


def mpich_prep_resources(resources: ResourceAssignment) -> Tuple[str, Dict[str, str]]:
    """Create resource description for MPICH mpirun

    Args:
        resources: The resource assignment to describe

    Return:
        The contents of the machinefile, and a set of environment variables
    """
    # No env vars, but rankfile
    raise NotImplementedError()


def srun_prep_resources(
        resources: ResourceAssignment, rankfile_location: Path
        ) -> Tuple[str, Dict[str, str]]:
    """Create resource description for srun

    Args:
        resources: The resources to describe
        rankfile_location: Location where the rankfile will be written

    Return:
        The contents of the hostfile, and a set of environment variables
    """
    hostfile = '\n'.join((
        node_res.node_name for node_res in resources.by_rank
        for _ in node_res.hwthreads()))

    env = {'SLURM_HOSTFILE': str(rankfile_location)}

    def core_mask(hwthreads: Iterable[int]) -> str:
        mask = sum((1 << hwthread) for hwthread in hwthreads)
        return format(mask, '#x')

    bind_str = ','.join([
        core_mask(node_res.hwthreads()) for node_res in resources.by_rank])

    env['SLURM_CPU_BIND'] = f'verbose,mask_cpu:{bind_str}'

    return hostfile, env


def prep_resources(
        model: ExecutionModel, resources: ResourceAssignment, rankfile_location: Path
        ) -> Tuple[str, Dict[str, str]]:
    """Create resource description for the given execution model.

    Args:
        model: The execution model to generate a description for
        resources: The resource assignment to describe
        rankfile_location: Path to where the rankfile will be written

    Return:
        The contents of the rank/machine/hostfile, and a set of environment variables.
    """
    if model == ExecutionModel.DIRECT:
        return direct_prep_resources(resources)
    elif model == ExecutionModel.OPENMPI:
        return openmpi_prep_resources(resources)
    elif model == ExecutionModel.INTELMPI:
        return impi_prep_resources(resources)
    elif model == ExecutionModel.SRUNMPI:
        return srun_prep_resources(resources, rankfile_location)
    # elif model == ExecutionModel.MPICH:
    #     return mpich_prep_resources(resources)
    raise RuntimeError(
            f'Impossible execution model {model}, please create an issue on GitHub')


def num_mpi_tasks(res_req: ResourceRequirements) -> int:
    """Determine the number of MPI tasks to be started.

    For non-MPI resource requirements, returns 1.

    Args:
        res_req: Resource requirements to analyse.
    """
    if isinstance(res_req, ThreadedResReq):
        return 1
    elif isinstance(res_req, MPICoresResReq):
        return res_req.mpi_processes
    elif isinstance(res_req, MPINodesResReq):
        return res_req.nodes * res_req.mpi_processes_per_node
    raise RuntimeError('Invalid ResourceRequirements')


def local_command(implementation: Implementation, enable_debug: bool) -> str:
    """Make a format string for the command to run.

    This interprets the execution_model and produces an appropriate shell command to
    start the implementation. This function produces commands for running locally:
    pinning is disabled and there's only one node.

    Args:
        implementation: The implementation to start.
        enable_debug: Whether to produce extra debug output.

    Return:
        A format string with embedded {ntasks} and {rankfile}.
    """
    if implementation.execution_model == ExecutionModel.DIRECT:
        fstr = 'exec {command} {args}'
    elif implementation.execution_model == ExecutionModel.OPENMPI:
        # Native name is orterun for older and prterun for newer OpenMPI.
        # So we go with mpirun, which works for either.
        fargs = [
                'exec mpirun -np $MUSCLE_MPI_PROCESSES',
                '--oversubscribe'
                ]

        if enable_debug:
            fargs.append('-v --debug-daemons --display-map --display-allocation')

        fargs.append('{command} {args}')

        fstr = ' '.join(fargs)

    elif implementation.execution_model == ExecutionModel.INTELMPI:
        fstr = 'exec mpirun -n $MUSCLE_MPI_PROCESSES {command} {args}'
    elif implementation.execution_model == ExecutionModel.SRUNMPI:
        raise ConfigurationError(
                f'Could not start {implementation.name} because the SRUNMPI execution'
                ' method only works in a SLURM allocation, and we are running locally.'
                ' Please switch this implementation to a different execution method'
                ' in the configuration file. You will probably want OPENMPI or'
                ' INTELMPI depending on which MPI implementation this code was'
                ' compiled with.')
    # elif implementation.execution_model == ExecutionModel.MPICH
    #    fstr = 'mpiexec -n {{ntasks}} {command} {args}'

    if implementation.args is None:
        args = ''
    elif isinstance(implementation.args, str):
        args = implementation.args
    elif isinstance(implementation.args, list):
        args = ' '.join(implementation.args)

    return fstr.format(
            command=implementation.executable,
            args=args
            )


def cluster_command(implementation: Implementation, enable_debug: bool) -> str:
    """Make a format string for the command to run.

    This interprets the execution_model and produces an appropriate shell command to
    start the implementation. This function produces commands for running on a cluster,
    with processes distributed across nodes and CPU pinning enabled.

    Args:
        implementation: The implementation to start.
        enable_debug: Whether to produce extra debug output.

    Return:
        A string with the command to use to start the implementation.
    """
    if implementation.execution_model == ExecutionModel.DIRECT:
        fargs = [
                'if ! taskset -V >/dev/null 2>&1 ; then',
                '    exec {command} {args}',
                'else',
                '    exec taskset $MUSCLE_BIND_MASK {command} {args}',
                'fi'
                ]
        fstr = '\n'.join(fargs)

    elif implementation.execution_model == ExecutionModel.OPENMPI:
        fargs = [
                # Native name is orterun for older and prterun for newer OpenMPI.
                # So we go with mpirun, which works for either.
                'exec mpirun -np $MUSCLE_MPI_PROCESSES',
                '--rankfile $MUSCLE_RANKFILE --use-hwthread-cpus --bind-to hwthread',
                '--oversubscribe'
                ]

        if enable_debug:
            fargs.append('-v --display-allocation --display-map --report-bindings')

        if slurm().quirks.overlap:
            # This adds the given option to the srun command used by mpirun to launch
            # its daemons. mpirun specifies --exclusive, which on SLURM <= 21-08 causes
            # SLURM to wait for our agents to quit, as it considers them to be occupying
            # the cores, causing a deadlock. Fortunately, it seems that adding --overlap
            # overrides the --exclusive and it works.
            fargs.append('-mca plm_slurm_args "--overlap"')

        fargs.append('{command} {args}')

        fstr = ' '.join(fargs)

    elif implementation.execution_model == ExecutionModel.INTELMPI:
        fargs = [
                'exec mpirun -n $MUSCLE_MPI_PROCESSES',
                '-machinefile $MUSCLE_RANKFILE']

        if enable_debug:
            fargs.append('-genv I_MPI_DEBUG=4')

        fargs.append('{command} {args}')

        fstr = ' '.join(fargs)

    elif implementation.execution_model == ExecutionModel.SRUNMPI:
        fargs = ['exec srun -n $MUSCLE_MPI_PROCESSES -m arbitrary']

        if slurm().quirks.overlap:
            fargs.append('--overlap')

        verbose = 'verbose,' if enable_debug else ''

        fargs.append(f'{slurm().quirks.cpu_bind}={verbose}$SLURM_CPU_BIND')
        fargs.append('{command} {args}')

        fstr = ' '.join(fargs)

    # elif implementation.execution_model == ExecutionModel.MPICH
    #    fstr = 'mpiexec -n $MUSCLE_MPI_PROCESSES -f $MUSCLE_RANKFILE {command} {args}'

    if implementation.args is None:
        args = ''
    elif isinstance(implementation.args, str):
        args = implementation.args
    elif isinstance(implementation.args, list):
        args = ' '.join(implementation.args)

    return fstr.format(
            command=implementation.executable,
            args=args
            )


def make_script(
        implementation: Implementation, res_req: ResourceRequirements,
        work_dir: Path, local: bool, rankfile: Optional[Path] = None) -> str:
    """Make a run script for a given implementation.

    Args:
        implementation: The implementation to launch
        res_req: The job's resource requirements
        work_dir: The directory to start the instance in
        local: Whether this is to run locally (True) or on a cluster (False)
        rankfile: Location of the rankfile, if any

    Return:
        A string with embedded newlines containing the shell script.
    """
    enable_debug = logging.getLogger('libmuscle').getEffectiveLevel() <= logging.DEBUG

    lines: List[str] = list()

    if implementation.base_env == BaseEnv.LOGIN:
        # We try to emulate an interactive login shell here by starting a
        # non-interactive login shell and manually loading the configuration files that
        # an interactive one would load. This avoids a confusing warning on stderr that
        # we get from /bin/bash -il because it can't find a controlling terminal.
        lines.append('#!/bin/bash --norc')
        lines.append('')
        lines.append('if [ -f /etc/environment ] ; then')
        lines.append('    . /etc/environment')
        lines.append('fi')
        lines.append('')
        lines.append('if [ -f /etc/profile ] ; then')
        lines.append('    . /etc/profile')
        lines.append('fi')
        lines.append('')
        lines.append('if [ -f ~/.bash_profile ] ; then')
        lines.append('    . ~/.bash_profile')
        lines.append('elif [ -f ~/.bash_login ] ; then')
        lines.append('    . ~/.bash_login')
        lines.append('elif [ -f ~/.profile ] ; then')
        lines.append('    . ~/.profile')
        lines.append('fi')
    else:
        lines.append('#!/bin/bash')

    lines.append('')

    # The environment is passed when starting the script, rather than as a set of
    # export statements here.

    if implementation.base_env == BaseEnv.CLEAN:
        lines.append('module purge')
        lines.append('')

    if implementation.modules:
        if isinstance(implementation.modules, str):
            lines.append(f'module load {implementation.modules}')
        else:
            for module in implementation.modules:
                lines.append(f'module load {module}')
        lines.append('')

    if implementation.virtual_env:
        lines.append(f'. {implementation.virtual_env}/bin/activate')
        lines.append('')

    if implementation.base_env == BaseEnv.LOGIN:
        # config files may change the work directory from what we set, so we add this to
        # ensure it's correct.
        lines.append(f'cd {work_dir}')

    if local:
        lines.append(local_command(implementation, enable_debug))
    else:
        lines.append(cluster_command(implementation, enable_debug))

    lines.append('')

    return '\n'.join(lines)
