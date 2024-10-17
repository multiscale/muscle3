from pathlib import Path
from typing import Dict, List, Optional, Tuple

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


def srun_prep_resources(resources: Resources) -> Tuple[str, Dict[str, str]]:
    """Create resource description for srun

    Args:
        resources: The resources to describe

    Return:
        The contents of the hostfile, and a set of environment variables
    """
    # SLURM_HOSTFILE to point to the rankfile
    # CPU_BIND=verbose,mask_cpu=0x01,0x02,0x04,0x01 to specify cores 0,1,2,0 for ranks
    # 0-3
    raise NotImplementedError()


def prep_resources(
        model: ExecutionModel, resources: Resources
        ) -> Tuple[str, Dict[str, str]]:
    """Create resource description for the given execution model.

    Args:
        model: The execution model to generate a description for
        resources: The resources to describe

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
        return srun_prep_resources(resources)
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
        fstr = 'srun -n $MUSCLE_MPI_PROCESSES -m arbitrary {command} {args}'
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
                ' --bind-to core --display-map --display-allocation {command} {args}'
                )
    elif implementation.execution_model == ExecutionModel.INTELMPI:
        fstr = (
                'mpirun -n $MUSCLE_MPI_PROCESSES -machinefile $MUSCLE_RANKFILE'
                ' {command} {args}')
    elif implementation.execution_model == ExecutionModel.SRUNMPI:
        fstr = 'srun -n $MUSCLE_MPI_PROCESSES -m arbitrary {command} {args}'
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
