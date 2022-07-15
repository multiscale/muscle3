import sys
from typing import Sequence

import click
import ymmsl
from ymmsl import Identifier, PartialConfiguration


from libmuscle.planner.planner import Planner, Resources


_RESOURCES_INCOMPLETE_MODEL = """
A model, implementations and resources must be given to be able to calculate
resources for a model. Please ensure that you have specified all of them in
your yMMSL file(s).
"""


@click.group()
def muscle3():
    """MUSCLE3 command line interface

    In the future, this command will provide various functions for
    running coupled simulations using MUSCLE3. For now, it does only
    one thing, which is to calculate the number of cluster nodes
    needed for a given simulation to run without oversubscribing.

    Use muscle3 <command> --help for help with individual commands.
    """
    pass


@muscle3.command(short_help='Calculate resources needed for a simulation')
@click.argument(
        'ymmsl_files', nargs=-1, required=True, type=click.Path(
            exists=True, file_okay=True, dir_okay=False, readable=True,
            allow_dash=True, resolve_path=True))
@click.option(
        '-c', '--cores-per-node', nargs=1, type=int, required=True,
        help='Set number of cores per cluster node.')
@click.option(
        '-v', '--verbose', is_flag=True, help='Show instance allocations.')
def resources(
        ymmsl_files: Sequence[str],
        cores_per_node: int, verbose: bool
        ) -> None:
    """Calculate the number of nodes needed to run the simulation.

    In order to run a MUSCLE3 simulation on a cluster, a batch job has
    to be submitted specifying the resources needed. This command
    calculates the number of nodes needed to run a given simulation
    without oversubscribing, given the number of cores available in
    each node.

    If multiple yMMSL files are given, then they will be combined left
    to right, i.e. if there are conflicting declarations, the one from
    the file last given is used.

    Result:

      With the -v option, the allocation of each instance will be printed
      to stdout. Without it, a single number will be printed, the number
      of nodes needed to run the simulation.

    Examples:

      muscle3 resources --cores-per-node 24 simulation.ymmsl

      muscle3 resources -c 16 model.ymmsl resources.ymmsl

      num_nodes=$(muscle3 resources -c 16 simulation.ymmsl)
      sbatch -N ${num_nodes} simulation.sh

    """
    partial_config = _load_ymmsl_files(ymmsl_files)
    try:
        config = partial_config.as_configuration()
    except ValueError:
        click.echo(_RESOURCES_INCOMPLETE_MODEL, err=True)
        sys.exit(1)

    resources = Resources({'node000001': set(range(cores_per_node))})
    planner = Planner(resources)
    try:
        allocations = planner.allocate_all(config, True)
    except InsufficientResourcesAvailable as e:
        click.echo(e)
        sys.exit(1)

    num_nodes = len(tuple(resources.nodes()))

    if verbose:
        click.echo()
        if num_nodes == 1:
            click.echo('A total of 1 node will be needed, as follows:')
        else:
            click.echo(
                    f'A total of {num_nodes} nodes will be needed,'
                    ' as follows:')

        click.echo()
        for instance in sorted(allocations):
            click.echo(f'{instance}: {str(allocations[instance])}')
    else:
        click.echo(f'{num_nodes}', nl=False)

    sys.exit(0)


def _load_ymmsl_files(ymmsl_files: Sequence[str]) -> PartialConfiguration:
    """Loads and merges yMMSL files."""
    configuration = PartialConfiguration()
    for path in ymmsl_files:
        with open(path, 'r') as f:
            configuration.update(ymmsl.load(f))
    return configuration


if __name__ == '__main__':
    muscle3()
