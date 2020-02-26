#!/bin/bash

. python/build/venv/bin/activate
muscle_manager reaction_diffusion.ymmsl &

manager_pid=$!

BINDIR=python

python $BINDIR/reaction.py --muscle-instance=micro >'micro.log' 2>&1 &
python $BINDIR/diffusion.py --muscle-instance=macro >'macro.log' 2>&1 &

touch muscle3_manager.log
tail -f muscle3_manager.log --pid=${manager_pid}

wait

