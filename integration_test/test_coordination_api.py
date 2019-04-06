from libmuscle import Muscle3


def test_init_muscle(log_file_in_tmpdir, mmp_server_process, sys_argv_manager):
    Muscle3()
