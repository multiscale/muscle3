#!/bin/bash

muscle_manager reaction_diffusion.ymmsl &

manager_pid=$!

export LD_LIBRARY_PATH=$MUSCLE3_HOME/lib:$LD_LIBRARY_PATH

mpirun -n 2 ./reaction_mpi --muscle-instance=micro >'micro.log' 2>&1 &
./diffusion --muscle-instance=macro >'macro.log' 2>&1 &

touch muscle3_manager.log
tail -f muscle3_manager.log --pid=${manager_pid}

wait

