from datetime import datetime
from pathlib import Path
import sys
import textwrap
from time import sleep
import traceback
from typing import cast, List, Optional, Sequence
from warnings import catch_warnings, filterwarnings

import click
from yaml.scanner import ScannerError
from yatiml import RecognitionError
from ymmsl import Document
import ymmsl
import ymmsl.v0_1 as v0_1
import ymmsl.v0_2 as v0_2

from libmuscle.manager.hammer import flatten
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
            'Start all submodel instances listed in the configuration file(s).')
        )
@click.option(
        '-m', '--model', nargs=1, type=str, help=(
            'Start the specified model, which must be present in the ymmsl files')
        )
def manage_simulation(
        ymmsl_files: Sequence[str],
        start_all: bool,
        model: Optional[str],
        run_dir: Optional[str],
        log_level: Optional[str],
        location_file: Optional[str]
        ) -> None:
    """Run the MUSCLE3 Manager.

    This is a thin wrapper so that we can call the implementation directly for testing
    purposes. The decorators above change the signature so that this function can't be
    called from Python anymore.
    """
    _manage_simulation(ymmsl_files, start_all, model, run_dir, log_level, location_file)


def _manage_simulation(
        ymmsl_files: Sequence[str],
        start_all: bool,
        model: Optional[str],
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
    try:
        configuration = load_configuration(ymmsl_files)
        v0_2.resolve(v0_2.Reference([]), configuration)
    except RuntimeError as e:
        print(f'An error occurred while loading the ymmsl files:\n{e}')
        sys.exit(1)

    try:
        configuration.check_consistent(start_all)
    except Exception as exc:
        print('Failed to start the simulation, found a configuration error:\n' +
              textwrap.indent(str(exc), 4*' '), file=sys.stderr)
        sys.exit(1)

    # find root models, error if multiple
    model_ref: Optional[v0_2.Reference] = None
    if model:
        try:
            model_ref = v0_2.Reference(model)
        except RuntimeError as e:
            raise RuntimeError('An invalid model name was given: {e}') from None

    try:
        root_model = configuration.root_model(model_ref)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        print(
                'Please add or remove models, or select one using the -m option.',
                file=sys.stderr)
        sys.exit(1)

    run_dir_obj = create_run_dir(run_dir, root_model)

    configuration = flatten(configuration, model_ref)
    manager = Manager(configuration, run_dir_obj, log_level)

    if start_all:
        try:
            manager.start_instances()
        except Exception as exc:
            manager.stop()
            print('Failed to start the simulation:', file=sys.stderr)
            print(textwrap.indent(str(exc), 4*' '), file=sys.stderr)
            print(file=sys.stderr)
            print('Check the manager log for more details:', file=sys.stderr)
            print('   ', run_dir_obj.path / 'muscle3_manager.log', file=sys.stderr)
            sys.exit(1)

    else:
        server_location = manager.get_server_location()
        if location_file is None:
            print(server_location, flush=True)
        else:
            Path(location_file).write_text(server_location)

    success = manager.wait()

    if not success:
        log_file = run_dir_obj.path / 'muscle3_manager.log'

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
            rel_run_dir = run_dir_obj.path.relative_to(Path.cwd())
            print(f'Output may be found in {rel_run_dir}')
        except ValueError:
            print(f'Output may be found in {run_dir_obj.path}')

    sys.exit(0 if success else 1)


def load_configuration(paths: Sequence[str]) -> v0_2.Configuration:
    """Load, combine a series of configuration files

    This loads the given files and combines them together into a single ymmsl v0.2
    Configuration object. If all files are v0.1, then merging will be done in the v0.1
    way for backwards compatibility, if any v0.2 file is given then the new rules apply.
    """
    docs = load_files(paths)
    if all([isinstance(d, v0_1.PartialConfiguration) for d in docs]):
        # merge v0.1 style, then convert to v0.2
        config_v1 = cast(v0_1.PartialConfiguration, docs[0])
        for d in docs[1:]:
            config_v1.update(cast(v0_1.PartialConfiguration, d))

        with catch_warnings():
            filterwarnings('ignore', 'In yMMSL v0.2.*')
            filterwarnings('ignore', 'Comments can unfortunately.*')
            return ymmsl.convert_to(v0_2.Configuration, config_v1)
    else:
        # convert to v0.2 if needed and merge v0.2 style
        with catch_warnings():
            filterwarnings('ignore', 'In yMMSL v0.2.*')
            filterwarnings('ignore', 'Comments can unfortunately.*')
            config_v2 = ymmsl.convert_to(v0_2.Configuration, docs[0])

            for d in docs[1:]:
                config_v2.update(ymmsl.convert_to(v0_2.Configuration, d))
        return config_v2


def load_files(paths: Sequence[str]) -> List[Document]:
    """Load the given files and return a list of documents.

    This doesn't convert or merge anything, it just loads the files as they are. If an
    error occurs, it will print the error and exit.
    """
    docs = list()
    for path in paths:
        try:
            docs.append(ymmsl.load(Path(path)))
        except RecognitionError as exc:
            # capture yatiml errors:
            # - ymmsl syntax errors, like mapping instead of lists, misspelled keys, ...
            # - value errors thrown by constructors (e.g. specifying duplicate port
            #   names)
            print(
                    f"Recognition error while loading configuration file '{path}':",
                    file=sys.stderr)
            print(textwrap.indent(str(exc), 4*' '), file=sys.stderr)
            sys.exit(1)
        except Exception:
            # Any other error is not anticipated
            print(f"Error while loading configuration file '{path}':", file=sys.stderr)
            traceback.print_exc()
            print(file=sys.stderr)
            print(
                    'This error could indicate a bug in libmuscle, please make an issue'
                    ' on GitHub.', file=sys.stderr)
            sys.exit(1)

    return docs


def create_run_dir(run_dir: Optional[str], model: v0_2.Model) -> RunDir:
    """Create the run directory

    Args:
        run_dir: User-specified path to the run dir, if any
        model: The (top-level) model we're going to run

    Returns:
        A RunDir object pointing to the created directory
    """
    if run_dir is None:
        for i in range(10):
            timestamp = datetime.now()
            timestr = timestamp.strftime('%Y%m%d_%H%M%S')
            run_dir_path = Path.cwd() / f'run_{model.name}_{timestr}'
            if not run_dir_path.exists():
                break
            sleep(1.0)
        else:
            raise RuntimeError(
                    f'Tried to create run dir at {run_dir_path} but it already exists')
    else:
        run_dir_path = Path(run_dir).resolve()

    return RunDir(run_dir_path)


if __name__ == '__main__':
    manage_simulation()
