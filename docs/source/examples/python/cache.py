import logging
from functools import lru_cache

from libmuscle import Grid, Instance, InstanceFlags, Message
from ymmsl import Operator

def cache() -> None:
    """A simple exponential reaction model on a 1D grid.
    """
    instance = Instance({
            Operator.F_INIT: ['front_in'],
            Operator.O_F: ['front_out'],
            Operator.S: ['back_in'],
            Operator.O_I: ['back_out']},
            InstanceFlags.DONT_APPLY_OVERLAY,
            )         

    @lru_cache(maxsize=128)
    def cached_response(msg):
        instance.send('back_out', msg)
        return instance.receive_with_settings('back_in')

    while instance.reuse_instance():
        # F_INIT
        msg = instance.receive_with_settings('front_in')
        msg = cached_response(msg)
        instance.send('front_out', msg)
    
    logging.info(cached_response.cache_info())


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    cache()

