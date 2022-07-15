from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Optional, Sequence

import click
import ymmsl
from ymmsl import Identifier, PartialConfiguration

from libmuscle.manager.manager import Manager
from libmuscle.manager.run_dir import RunDir


@click.command(no_args_is_help=True)
@click.argument(
        'ymmsl_files', nargs=-1, required=True, type=click.Path(
            exists=True, file_okay=True, dir_okay=False, readable=True,
            allow_dash=True, resolve_path=True))
@click.option(
        '--log-level', nargs=1, type=str, default='INFO', show_default=True,
        help='Set the local log level. Try DEBUG for (much) more output.')
@click.option(
        '--run-dir', nargs=1, type=click.Path(
            exists=True, file_okay=False, dir_okay=True, readable=True,
            writable=True, allow_dash=False, resolve_path=True),
        help=(
            'Directory to write logs, run metadata and output to. By default,'
            ' a directory with the name run_<model>_<date>-<time> will be'
            ' created.')
        )
@click.option(
        '--start-all/--no-start-all', default=False, help=(
            'Start all submodel instances listed in the configuration file(s).'
            )
        )
def manage_simulation(
        ymmsl_files: Sequence[str],
        start_all: bool,
        run_dir: Optional[str],
        log_level: Optional[str]
        ) -> None:
    """Run the MUSCLE3 Manager.

    The MUSCLE manager manages a coupled simulation. It can start the
    various submodels, and it helps them to find and connect to each
    other to exchange messages. The manager also distributes settings
    from the configuration file(s) to the submodel instances.

    The muscle_manager command takes a list of configuration files in
    yMMSL format (see the online documentation). The files are combined
    in the order given, so if for example a setting is given multiple
    times, then the value in the last file in the list to mention it is
    used.
    """
    configuration = PartialConfiguration()
    for path in ymmsl_files:
        with open(path, 'r') as f:
            configuration.update(ymmsl.load(f))

    if run_dir is None:
        if configuration.model is not None:
            model_name = configuration.model.name
        else:
            model_name = Identifier('model')
        timestamp = datetime.now()
        timestr = timestamp.strftime('%Y%m%d_%H%M%S')
        run_dir_path = Path.cwd() / 'run_{}_{}'.format(model_name, timestr)
    else:
        run_dir_path = Path(run_dir).resolve()

    if start_all:
        run_dir_obj = RunDir(run_dir_path)
        manager = Manager(configuration, run_dir_obj, log_level)
        manager.start_instances()
    else:
        manager = Manager(configuration, None, log_level)
        print(manager.get_server_location())

    success = manager.wait()

    if not success:
        print('An error occurred during execution, and the simulation was')
        print('shut down. The manager log should tell you what happened.')
        print('You can find it at')
        print(run_dir_path / 'muscle3_manager.log')

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    manage_simulation()
