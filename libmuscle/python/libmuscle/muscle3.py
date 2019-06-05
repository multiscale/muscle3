import multiprocessing as mp
from typing import Callable, Dict

from ymmsl import Reference

from libmuscle.mcp import pipe_multiplexer as mux


def run_instances(instances: Dict[str, Callable]) -> None:
    """Runs the given instances and waits for them to finish.

    The instances are described in a dictionary with their instance
    id (e.g. 'macro' or 'micro[12]' or 'my_mapper') as the key, and
    a function to run as the corresponding value. Each instance
    will be run in a separate process.

    Args:
        instances: A dictionary of instances to run.
    """
    instance_processes = list()
    for instance_id_str, implementation in instances.items():
        mux.add_instance(Reference(instance_id_str))

    for instance_id_str, implementation in instances.items():
        instance_id = Reference(instance_id_str)
        process = mp.Process(target=implementation,
                             args=(instance_id_str,),
                             name='Instance-{}'.format(instance_id))
        process.start()
        mux.close_instance_ends(instance_id)
        instance_processes.append(process)

    mux_process = mp.Process(target=mux.run, name='PipeCommMultiplexer')
    mux_process.start()
    mux.close_all_pipes()

    failed_processes = list()
    for instance_process in instance_processes:
        instance_process.join()
        if instance_process.exitcode != 0:
            failed_processes.append(instance_process)
    mux_process.join()

    if len(failed_processes) > 0:
        failed_names = map(lambda x: x.name, failed_processes)
        raise RuntimeError('Instances {} failed to shut down cleanly, please'
                           ' check the logs to see what went wrong.'.format(
                               ', '.join(failed_names)))
