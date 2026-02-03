import logging
from functools import lru_cache

from libmuscle import Grid, Instance, InstanceFlags, Message
from ymmsl.v0_1 import Operator

def cache() -> None:
    """A simple cache

       WARNING: does not use timestamp(s) or settings for determining cached response

       only msg.data is used to determine if a response is cached.
    """
    instance = Instance({
            Operator.F_INIT: ['front_in'],
            Operator.O_F: ['front_out'],
            Operator.S: ['back_in'],
            Operator.O_I: ['back_out']},
            InstanceFlags.DONT_APPLY_OVERLAY,
            )         
    
    cachesize=128
    try:
        cachesize = instance.get_setting('size', 'int')
    except KeyError:
        pass


    @lru_cache(maxsize=cachesize)
    def cached_response(data):
        instance.send('back_out', msg) # use python magic to pass msg from outside this function
        return instance.receive_with_settings('back_in')

    while instance.reuse_instance():
        msg = instance.receive_with_settings('front_in')
        msg = cached_response(tuple(msg.data.array))
        instance.send('front_out', msg)
    
    logging.info(cached_response.cache_info())


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    cache()

