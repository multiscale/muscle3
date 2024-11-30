from pathlib import Path
from typing import Dict, FrozenSet, List, Optional, Tuple

from libmuscle.errors import ConfigurationError
from libmuscle.planner.planner import Resources
from ymmsl import (
        ExecutionModel, Implementation, MPICoresResReq, MPINodesResReq,
        ResourceRequirements, ThreadedResReq)


def direct_prep_resources(resources: Resources) -> Tuple[str, Dict[str, str]]:
    """Create resources for a non-MPI program with taskset.

    Taskset expects a set of cores on the command line, which we put into a
    MUSCLE_CORES environment variable here.

    Args:
        resources: The resources to describe

    Return:
        No rank file, and a set of environment variables.
    """
    env: Dict[str, str] = dict()
    only_node_hwthreads_list = [
            hwthread
            for core in next(iter(resources.cores.values()))
            for hwthread in core]

    env['MUSCLE_BIND_LIST'] = ','.join(map(str, only_node_hwthreads_list))

    mask_int = sum((1 << c for c in only_node_hwthreads_list))
    env['MUSCLE_BIND_MASK'] = format(mask_int, 'X')

    return '', env


def openmpi_prep_resources(resources: Resources) -> Tuple[str, Dict[str, str]]:
    """Create resource description for OpenMPI mpirun

    Args:
        resources: The resources to describe

    Return:
        The contents of the rankfile, and a set of environment variables
    """
    ranklines: List[str] = list()
    all_cores = (
            (node, ','.join(sorted(map(str, hwthreads))))
            for node, cores in resources.cores.items()
            for hwthreads in cores)

    for i, (node, hwthreads) in enumerate(all_cores):
        ranklines.append(f'rank {i}={node} slot={hwthreads}')

    rankfile = '\n'.join(ranklines) + '\n'

    return rankfile, dict()


def impi_prep_resources(resources: Resources) -> Tuple[str, Dict[str, str]]:
    """Create resource description for Intel MPI mpirun

    Args:
        resources: The resources to describe

    Return:
        The contents of the machinefile, and a set of environment variables
    """
    # I_MPI_PIN_PROCESSOR_LIST=0,1,5,6
    # pins rank 0 to core 0, rank 1 to core 1, rank 2 to core 5, rank 3 to core 6
    raise NotImplementedError()


def mpich_prep_resources(resources: Resources) -> Tuple[str, Dict[str, str]]:
    """Create resource description for MPICH mpirun

    Args:
        resources: The resources to describe

    Return:
        The contents of the machinefile, and a set of environment variables
    """
    # No env vars, but rankfile
    raise NotImplementedError()


def srun_prep_resources(
        resources: Resources, rankfile_location: Path) -> Tuple[str, Dict[str, str]]:
    """Create resource description for srun

    Args:
        resources: The resources to describe
        rankfile_location: Location where the rankfile will be written

    Return:
        The contents of the hostfile, and a set of environment variables
    """
    hostfile = '\n'.join((
        node for node, cores in resources.cores.items() for _ in cores))

    env = {'SLURM_HOSTFILE': str(rankfile_location)}

    bind_list = [
            core for _, cores in resources.cores.items() for core in cores]

    def core_mask(core: FrozenSet[int]) -> str:
        mask = sum((1 << hwthread) for hwthread in core)
        return format(mask, '#x')

    bind_str = ','.join(map(core_mask, bind_list))

    env['SLURM_CPU_BIND'] = f'verbose,mask_cpu:{bind_str}'

    return hostfile, env


def prep_resources(
        model: ExecutionModel, resources: Resources, rankfile_location: Path
        ) -> Tuple[str, Dict[str, str]]:
    """Create resource description for the given execution model.

    Args:
        model: The execution model to generate a description for
        resources: The resources to describe
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


def local_command(implementation: Implementation) -> str:
    """Make a format string for the command to run.

    This interprets the execution_model and produces an appropriate shell command to
    start the implementation. This function produces commands for running locally:
    pinning is disabled and there's only one node.

    Args:
        implementation: The implementation to start.

    Return:
        A format string with embedded {ntasks} and {rankfile}.
    """
    if implementation.execution_model == ExecutionModel.DIRECT:
        fstr = '{command} {args}'
    elif implementation.execution_model == ExecutionModel.OPENMPI:
        # Native name is orterun for older and prterun for newer OpenMPI.
        # So we go with mpirun, which works for either.
        fstr = 'mpirun -np $MUSCLE_MPI_PROCESSES --oversubscribe {command} {args}'
    elif implementation.execution_model == ExecutionModel.INTELMPI:
        fstr = 'mpirun -n $MUSCLE_MPI_PROCESSES {command} {args}'
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


def cluster_command(implementation: Implementation) -> str:
    """Make a format string for the command to run.

    This interprets the execution_model and produces an appropriate shell command to
    start the implementation. This function produces commands for running on a cluster,
    with processes distributed across nodes and CPU pinning enabled.

    Args:
        implementation: The implementation to start.

    Return:
        A string with the command to use to start the implementation.
    """
    # TODO: enable debug options iff the manager log level is set to DEBUG
    # TODO: don't use taskset if it's not available
    if implementation.execution_model == ExecutionModel.DIRECT:
        fstr = 'taskset $MUSCLE_BIND_MASK {command} {args}'
    elif implementation.execution_model == ExecutionModel.OPENMPI:
        # Native name is orterun for older and prterun for newer OpenMPI.
        # So we go with mpirun, which works for either.
        fstr = (
                'mpirun -v -np $MUSCLE_MPI_PROCESSES'
                ' -d --debug-daemons'
                ' --rankfile $MUSCLE_RANKFILE --use-hwthread-cpus --oversubscribe'
                # ' --map-by rankfile:file=$MUSCLE_RANKFILE:oversubscribe'
                # ' --display-map --display-allocation {command} {args}'

                # This adds the given option to the srun command used by mpirun to
                # launch its daemons. mpirun specifies --exclusive, which on SLURM <=
                # 21-08 causes SLURM to wait for our agents to quit, as it considers
                # them to be occupying the cores, causing a deadlock. Fortunately, it
                # seems that adding --overlap overrides the --exclusive and it works.
                ' -mca plm_slurm_args "--overlap"'
                ' --bind-to core --display-map --display-allocation {command} {args}'
                )
    elif implementation.execution_model == ExecutionModel.INTELMPI:
        fstr = (
                'mpirun -n $MUSCLE_MPI_PROCESSES -machinefile $MUSCLE_RANKFILE'
                ' {command} {args}')
    elif implementation.execution_model == ExecutionModel.SRUNMPI:
        # TODO: set SLURM_CPU_BIND_VERBOSE for verbose output
        fstr = (
                'srun -n $MUSCLE_MPI_PROCESSES -m arbitrary --overlap'
                ' --cpu-bind=$SLURM_CPU_BIND {command} {args}')
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
        local: bool, rankfile: Optional[Path] = None) -> str:
    """Make a run script for a given implementation.

    Args:
        implementation: The implementation to launch
        res_req: The job's resource requirements
        local: Whether this is to run locally (True) or on a cluster (False)
        rankfile: Location of the rankfile, if any

    Return:
        A string with embedded newlines containing the shell script.
    """
    lines: List[str] = list()

    lines.append('#!/bin/bash')
    lines.append('')

    # The environment is passed when starting the script, rather than as a set of
    # export statements here.

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

    if local:
        lines.append(local_command(implementation))
    else:
        lines.append(cluster_command(implementation))

    lines.append('')

    return '\n'.join(lines)
