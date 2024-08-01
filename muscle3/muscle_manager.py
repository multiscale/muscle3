from datetime import datetime
from pathlib import Path
import sys
import textwrap
import traceback
from typing import Optional, Sequence

import click
from yaml.scanner import ScannerError
from yatiml import RecognitionError
import ymmsl
from ymmsl import Identifier, PartialConfiguration

from libmuscle.manager.logger import last_lines
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
        '--location-file', nargs=1, type=click.Path(
            exists=False, file_okay=True, dir_okay=True, readable=False,
            allow_dash=True),
        help=(
            'File to write the network location of the manager to if'
            ' --start-all is not specified. If a relative path is given,'
            ' then it will be resolved relative to the directory in which'
            ' the manager was started.'
            '\b\n\n'
            ' The manager will write to this file a single line of text,'
            ' which should be passed to the instances via the'
            ' MUSCLE_MANAGER environment variable or on their command line'
            ' using the --muscle-manager=<contents> option.'
            '\b\n\n'
            ' If --start-all is not specified and --location-file is also'
            ' not given, then the location will be printed on standard'
            ' output.')
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
        log_level: Optional[str],
        location_file: Optional[str]
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
        configuration.update(load_configuration(path))

    try:
        if start_all:  # Do a full consistency check
            configuration.as_configuration().check_consistent()
        else:  # Only require that a Model exists and is consistent
            if configuration.model is None:
                raise ValueError('Model section is missing from the configuration.')
            if not isinstance(configuration.model, ymmsl.Model):
                raise ValueError('Model section from the configuration is incomplete.')
            configuration.model.check_consistent()
    except Exception as exc:
        print('Failed to start the simulation, found a configuration error:\n' +
              textwrap.indent(str(exc), 4*' '), file=sys.stderr)
        sys.exit(1)

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

    run_dir_obj = RunDir(run_dir_path)
    if start_all:
        manager = Manager(configuration, run_dir_obj, log_level)
        try:
            manager.start_instances()
        except Exception as exc:
            manager.stop()
            print('Failed to start the simulation:', file=sys.stderr)
            print(textwrap.indent(str(exc), 4*' '), file=sys.stderr)
            print(file=sys.stderr)
            print('Check the manager log for more details:', file=sys.stderr)
            print('   ', run_dir_path / 'muscle3_manager.log', file=sys.stderr)
            sys.exit(1)

    else:
        if run_dir is None:
            manager = Manager(configuration, None, log_level)
        else:
            manager = Manager(configuration, run_dir_obj, log_level)

        server_location = manager.get_server_location()
        if location_file is None:
            print(server_location, flush=True)
        else:
            Path(location_file).write_text(server_location)

    success = manager.wait()

    if not success:
        log_file = run_dir_path / 'muscle3_manager.log'

        print()
        print('An error occurred during execution, and the simulation was')
        print('shut down. The manager log should tell you what happened.')
        print('Here are the final lines of the manager log:')
        print()
        print('-' * 80)
        print(last_lines(log_file, 50), '    ')
        print('-' * 80)
        print()
        print('You can find the full log at')
        print(str(log_file))
        print()
    else:
        print('Simulation completed successfully.')
        try:
            rel_run_dir = run_dir_path.relative_to(Path.cwd())
            print(f'Output may be found in {rel_run_dir}')
        except ValueError:
            print(f'Output may be found in {run_dir_path}')

    sys.exit(0 if success else 1)


def load_configuration(path: str) -> PartialConfiguration:
    """Load and parse a configuration file.

    Annotates error messages for easier debugging by users.
    """
    with open(path, 'r') as f:
        try:
            return ymmsl.load(f)
        except ScannerError as exc:  # capture yaml errors
            # PyYAML error messages are not very user friendly, but there is not
            # too much we can do about it
            print(f"Syntax error while loading configuration file '{path}':",
                  file=sys.stderr)
            print(textwrap.indent(str(exc), 4*' '), file=sys.stderr)
            sys.exit(1)
        except RecognitionError as exc:
            # capture yatiml errors:
            # - ymmsl syntax errors, like mapping instead of lists, misspelled keys, ...
            # - value errors thrown by constructors (e.g. specifying duplicate port
            #   names)
            print(f"Recognition error while loading configuration file '{path}':",
                  file=sys.stderr)
            print(textwrap.indent(str(exc), 4*' '), file=sys.stderr)
            sys.exit(1)
        except Exception:
            # Any other error is not anticipated
            print(f"Error while loading configuration file '{path}':",
                  file=sys.stderr)
            traceback.print_exc()
            print(file=sys.stderr)
            print('This error could indicate a bug in libmuscle,'
                  ' please make an issue on GitHub.', file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    manage_simulation()
