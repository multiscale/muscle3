from libmuscle.mmp_client import MMPClient
from libmuscle import Muscle3


def test_init_muscle(mmp_server, replaced_sys_argv):
    Muscle3()


def test_init_muscle_no_manager():
    Muscle3()
