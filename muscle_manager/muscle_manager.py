from typing import Sequence

import click
import ymmsl
from ymmsl import Configuration

from libmuscle.manager.manager import start_server


@click.command()
@click.argument(
        'ymmsl_files', nargs=-1, required=True, type=click.Path(
            exists=True, file_okay=True, dir_okay=False, readable=True,
            allow_dash=True, resolve_path=True))
def manage_simulation(ymmsl_files: Sequence[str]) -> None:
    configuration = Configuration()
    for path in ymmsl_files:
        with open(path, 'r') as f:
            configuration.update(ymmsl.load(f))

    server = start_server(configuration)
    print(server.get_location())
    server.wait()


if __name__ == '__main__':
    manage_simulation()
