import click
import ymmsl

from libmuscle.manager.manager import start_server


@click.command()
@click.argument('ymmsl_file')
def manage_simulation(ymmsl_file: str) -> None:
    with open(ymmsl_file) as f:
        configuration = ymmsl.load(f)

    server = start_server(configuration)
    print(server.get_location())
    server.wait()


if __name__ == '__main__':
    manage_simulation()
