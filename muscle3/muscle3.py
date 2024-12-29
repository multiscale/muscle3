import sys
from collections import OrderedDict
from pathlib import Path
from typing import Sequence

import click
import ymmsl
from ymmsl import PartialConfiguration


from libmuscle.planner.planner import Planner, InsufficientResourcesAvailable
from libmuscle.planner.resources import Core, CoreSet, OnNodeResources, Resources
from libmuscle.snapshot_manager import SnapshotManager
from muscle3.profiling import (
        plot_instances, plot_resources, plot_timeline, show_plots)


_RESOURCES_INCOMPLETE_MODEL = """
A model, implementations and resources must be given to be able to calculate
resources for a model. Please ensure that you have specified all of them in
your yMMSL file(s).
"""


@click.group()
def muscle3() -> None:
    """MUSCLE3 command line interface

    This command provides various functions for running coupled simulations
    using MUSCLE3.

    Use muscle3 <command> --help for help with individual commands.
    """
    pass


@muscle3.command(short_help='Visualise profiling information')
@click.argument(
        'performance_file', nargs=1, type=click.Path(
            exists=True, file_okay=True, dir_okay=False, readable=True,
            allow_dash=True, resolve_path=True))
@click.option('-i', '--instances', is_flag=True, help='Show per-instance statistics')
@click.option('-r', '--resources', is_flag=True, help='Show per-resource statistics')
@click.option('-t', '--timeline', is_flag=True, help='Show a timeline of events')
def profile(
        performance_file: str, instances: bool, resources: bool, timeline: bool
        ) -> None:
    """Visualise profiling information.

    Takes data from a performance.sqlite file written by the manager,
    and produces one or more plots on the screen.

    Profiling functionality is still somewhat experimental, so this
    command may be changed and extended in the coming releases. Please
    let us know if there are any changes or additional features you
    would like to have by making an issue on GitHub, or through your
    usual support channel.

    Result:
        With -i, shows a chart depicting for each instance how much time
        it spend running, waiting and communicating.

        With -r, shows a chart depicting for each resource (CPU core)
        which instances ran on it for how long.

        With -t, shows a timeline of the different instances, depicting
        when they were sending, waiting, receiving and running.
    """
    if instances:
        plot_instances(Path(performance_file))

    if resources:
        plot_resources(Path(performance_file))

    if timeline:
        plot_timeline(Path(performance_file))
        click.echo(
                'Hint: To inspect the timeline in more detail, use the'
                ' pan and zoom buttons at the bottom of the window.')

    if instances or resources or timeline:
        show_plots()
    else:
        click.echo(
                'Please specify -i, -r or -t to choose which data'
                ' you would like to see.')
        sys.exit(1)

    sys.exit(0)


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

    resources = Resources([
        OnNodeResources(
            'node000001', CoreSet([Core(i, {i}) for i in range(cores_per_node)]))])

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


@muscle3.command(short_help='Display details of a stored snapshot')
@click.argument(
        'snapshot_files', nargs=-1, required=True, type=click.Path(
            exists=True, file_okay=True, dir_okay=False, readable=True,
            allow_dash=True, resolve_path=True, path_type=Path))
@click.option(
        '-d', '--data', is_flag=True,
        help='Display stored data. Note this may result in a lot of output!')
@click.option(
        '-v', '--verbose', is_flag=True, help='Display more metadata.')
def snapshot(
        snapshot_files: Sequence[Path], data: bool, verbose: bool) -> None:
    """Display information about stored snapshots.

    Per provided snapshot, display metadata. Stored data can also be output by
    supplying the '-d' or '--data' flags. Note that this may result in a lot of
    data displayed.
    """
    for file in snapshot_files:
        snapshot = SnapshotManager.load_snapshot_from_file(file)
        click.echo(f'Snapshot at {file}:')
        typ = 'Final' if snapshot.is_final_snapshot else 'Intermediate'
        properties = OrderedDict([
            ('Snapshot type', typ),
            ('Snapshot timestamp',
             snapshot.message.timestamp if snapshot.message else float('-inf')),
            ('Snapshot wallclock time', snapshot.wallclock_time),
            ('Snapshot triggers', snapshot.triggers),
        ])
        if verbose:
            properties.update([
                ('Internal: Port message counts', snapshot.port_message_counts),
            ])
        for prop_name, prop_value in properties.items():
            click.secho(f'{prop_name}: ', nl=False, bold=True)
            click.echo(prop_value)
        if data:
            click.secho('Snapshot data:', bold=True)
            if snapshot.message is not None:
                click.echo(snapshot.message.data)
            else:
                click.secho("No data available", italic=True)
        click.echo()


def _load_ymmsl_files(ymmsl_files: Sequence[str]) -> PartialConfiguration:
    """Loads and merges yMMSL files."""
    configuration = PartialConfiguration()
    for path in ymmsl_files:
        with open(path, 'r') as f:
            configuration.update(ymmsl.load(f))
    return configuration


if __name__ == '__main__':
    muscle3()
