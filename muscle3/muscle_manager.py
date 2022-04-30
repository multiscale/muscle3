from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Optional, Sequence

import click
import ymmsl
from ymmsl import Identifier, PartialConfiguration

from libmuscle.manager.manager import Manager
from libmuscle.manager.run_dir import RunDir


@click.command()
@click.argument(
        'ymmsl_files', nargs=-1, required=True, type=click.Path(
            exists=True, file_okay=True, dir_okay=False, readable=True,
            allow_dash=True, resolve_path=True))
@click.option('--log-level', nargs=1, type=str)
@click.option('--run-dir', nargs=1, type=click.Path(
    exists=True, file_okay=False, dir_okay=True, readable=True, writable=True,
    allow_dash=False, resolve_path=True))
@click.option('--start-all', is_flag=True)
def manage_simulation(
        ymmsl_files: Sequence[str],
        start_all: bool,
        run_dir: Optional[str],
        log_level: Optional[str]
        ) -> None:
    configuration = PartialConfiguration()
    for path in ymmsl_files:
        with open(path, 'r') as f:
            configuration.update(ymmsl.load(f))

    if run_dir is None:
        if configuration.model is not None:
            model_name = configuration.model.name
        else:
            model_name = Identifier('model')
        timestamp = datetime.now(timezone.utc)
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
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    manage_simulation()
