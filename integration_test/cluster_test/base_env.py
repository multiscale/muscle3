import os

from libmuscle import Instance


def component() -> None:
    """A component that checks whether the environment is correct.

    This prints the values of the BASHRC_LOADED and MANAGER_SHELL
    variables so that the test can see whether they're set correctly.

    It also checks if slurm is on the path, which it only is if the
    default modules are still loaded, at least in this particular
    test setup, and whether we have VIRTUAL_ENV set.

    """
    instance = Instance()

    print(os.environ.get('PROFILE_LOADED', '0'))
    print(os.environ.get('BASHRC_LOADED', '0'))
    print(os.environ.get('MANAGER_SHELL', '0'))
    print('1' if 'slurm' in os.environ['PATH'] else '0')
    print(os.environ.get('VIRTUAL_ENV', ''))

    while instance.reuse_instance():
        pass


if __name__ == '__main__':
    component()
