import sys
from collections import OrderedDict
from pathlib import Path
from typing import Sequence, Union

import click
import ymmsl
from ymmsl import PartialConfiguration

import pydot
import subprocess


from libmuscle.planner.planner import Planner, Resources, InsufficientResourcesAvailable
from libmuscle.snapshot_manager import SnapshotManager

from .model_graph_pydot import plot_model_graph


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


@muscle3.command(short_help="Calculate resources needed for a simulation")
@click.argument(
    "ymmsl_files",
    nargs=-1,
    required=True,
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        allow_dash=True,
        resolve_path=True,
    ),
)
@click.option(
    "-c",
    "--cores-per-node",
    nargs=1,
    type=int,
    required=True,
    help="Set number of cores per cluster node.",
)
@click.option("-v", "--verbose", is_flag=True, help="Show instance allocations.")
def resources(ymmsl_files: Sequence[str], cores_per_node: int, verbose: bool) -> None:
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

    resources = Resources({"node000001": set(range(cores_per_node))})
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
            click.echo("A total of 1 node will be needed, as follows:")
        else:
            click.echo(f"A total of {num_nodes} nodes will be needed," " as follows:")

        click.echo()
        for instance in sorted(allocations):
            click.echo(f"{instance}: {str(allocations[instance])}")
    else:
        click.echo(f"{num_nodes}", nl=False)

    sys.exit(0)


@muscle3.command(short_help="Display details of a stored snapshot")
@click.argument(
    "snapshot_files",
    nargs=-1,
    required=True,
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        allow_dash=True,
        resolve_path=True,
        path_type=Path,
    ),
)
@click.option(
    "-d",
    "--data",
    is_flag=True,
    help="Display stored data. Note this may result in a lot of output!",
)
@click.option("-v", "--verbose", is_flag=True, help="Display more metadata.")
def snapshot(snapshot_files: Sequence[Path], data: bool, verbose: bool) -> None:
    """Display information about stored snapshots.

    Per provided snapshot, display metadata. Stored data can also be output by
    supplying the '-d' or '--data' flags. Note that this may result in a lot of
    data displayed.
    """
    for file in snapshot_files:
        snapshot = SnapshotManager.load_snapshot_from_file(file)
        click.echo(f"Snapshot at {file}:")
        typ = "Final" if snapshot.is_final_snapshot else "Intermediate"
        properties = OrderedDict(
            [
                ("Snapshot type", typ),
                (
                    "Snapshot timestamp",
                    snapshot.message.timestamp if snapshot.message else float("-inf"),
                ),
                ("Snapshot wallclock time", snapshot.wallclock_time),
                ("Snapshot triggers", snapshot.triggers),
            ]
        )
        if verbose:
            properties.update(
                [
                    ("Internal: Port message counts", snapshot.port_message_counts),
                ]
            )
        for prop_name, prop_value in properties.items():
            click.secho(f"{prop_name}: ", nl=False, bold=True)
            click.echo(prop_value)
        if data:
            click.secho("Snapshot data:", bold=True)
            if snapshot.message is not None:
                click.echo(snapshot.message.data)
            else:
                click.secho("No data available", italic=True)
        click.echo()


@muscle3.command(short_help="Print a graphical representation of this workflow")
@click.argument(
    "ymmsl_files",
    nargs=-1,
    required=True,
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        allow_dash=True,
        resolve_path=True,
    ),
)
@click.option(
    "-o",
    "--out",
    nargs=1,
    required=False,
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
        readable=False,
        allow_dash=True,
        resolve_path=True,
    ),
    help="Output file (default ./output.format)",
)
@click.option(
    "-f",
    "--fmt",
    type=click.Choice(pydot.Dot().formats, case_sensitive=False),
    required=False,
    help="Set output format (default svg).",
)
@click.option(
    "-w",
    "--viewer",
    nargs=1,
    required=False,
    type=str,
    help="Open with specified viewer (try xdg-open)",
)
@click.option("-v", "--verbose", is_flag=True, help="Include more information.")
def graph(
    ymmsl_files: Sequence[str],
    out: Union[Path, None],
    fmt: str,
    viewer: str,
    verbose: bool,
) -> None:
    """Plot a graphical representation of the passed yMMSL files.

    To help develop or understand about a coupled simulation it may
    be useful to view a graphical representation.

    If multiple yMMSL files are given, then they will be combined left
    to right, i.e. if there are conflicting declarations, the one from
    the file last given is used.

    Result:

      A graph is displayed or saved to disk, containing all the defined
    components and the connections between them.

    Examples:

      muscle3 graph simulation.ymmsl

    """
    partial_config = _load_ymmsl_files(ymmsl_files)

    graph = plot_model_graph(partial_config, simplify_edge_labels=not verbose)

    if fmt is None:
        fmt = "svg"
    if out is None:
        out = "output." + fmt

    if out == '-' and fmt == 'dot':
        print(graph)
    elif out == '-':
        print(graph.create(format=fmt))
    else:
        graph.write(out, format=fmt)

    if viewer is not None and out != '-':
        subprocess.run([viewer, out])


def _load_ymmsl_files(ymmsl_files: Sequence[str]) -> PartialConfiguration:
    """Loads and merges yMMSL files."""
    configuration = PartialConfiguration()
    for path in ymmsl_files:
        with open(path, "r") as f:
            configuration.update(ymmsl.load(f))
    return configuration


if __name__ == "__main__":
    muscle3()
