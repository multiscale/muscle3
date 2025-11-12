import logging
import os

import numpy as np

from libmuscle import Grid, Instance, Message
from ymmsl import Operator


def new_state(rule, old_state):
    """
    old state is treated as a 3 bit number
    """
    return (rule>>old_state)%2

def elemental_ca_micro() -> None:
    """A simple elementary cellular automata on a 1d grid.

    This model calculates the next step of an elemental ca    """
    logger = logging.getLogger()
    instance = Instance({
            Operator.F_INIT: ['initial_state'],     # 1D Grid
            Operator.O_F: ['final_state']})         # 1D Grid

    while instance.reuse_instance():
        # F_INIT
        rule = instance.get_setting('rule', 'int')
        msg = instance.receive('initial_state')
        U = msg.data.array.copy()
        U_new = U.copy()

        for i in range(U.size):
            a = 0 if i == 1 else U[i-1]
            b = U[i]
            c = 0 if i == U.size -1 else U[i+1]
        
            old_state = a<<2 + b<<1 + c

            U_new[i] = new_state(rule, old_state)
        

        # O_F
        final_state_msg = Message(msg.timestamp, data=Grid(U_new, ['x']))
        instance.send('final_state', final_state_msg)

if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    elemental_ca_micro()
