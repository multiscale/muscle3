from libmuscle import Muscle3


def test_init_muscle(mmp_server, sys_argv_manager):
    Muscle3()


def test_init_muscle_no_manager():
    Muscle3()
