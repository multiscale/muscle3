from typing import Sequence

import click
import ymmsl
from ymmsl import PartialConfiguration

from libmuscle.manager.manager import start_server


@click.command()
@click.argument(
        'ymmsl_files', nargs=-1, required=True, type=click.Path(
            exists=True, file_okay=True, dir_okay=False, readable=True,
            allow_dash=True, resolve_path=True))
def manage_simulation(ymmsl_files: Sequence[str]) -> None:
    configuration = PartialConfiguration()
    for path in ymmsl_files:
        with open(path, 'r') as f:
            configuration.update(ymmsl.load(f))
    # temporary dummy data to satisfy type
    configuration.update(PartialConfiguration(
        None, None, {'dummy': None}, {'dummy': None}))

    server = start_server(configuration.as_configuration())
    print(server.get_location())
    server.wait()


if __name__ == '__main__':
    manage_simulation()
