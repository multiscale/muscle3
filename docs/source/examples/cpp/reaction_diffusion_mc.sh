#!/bin/bash

muscle_manager reaction_diffusion_mc.ymmsl &

export LD_LIBRARY_PATH=$MUSCLE3_HOME/lib:$LD_LIBRARY_PATH

./reaction --muscle-instance=micro[0] >'micro[0].log' 2>&1 &
./reaction --muscle-instance=micro[1] >'micro[1].log' 2>&1 &
./diffusion --muscle-instance=macro[0] >'macro[0].log' 2>&1 &
./diffusion --muscle-instance=macro[1] >'macro[1].log' 2>&1 &
./load_balancer --muscle-instance=rr >rr.log 2>&1 &
./mc_driver --muscle-instance=mc >mc.log 2>&1 &

wait

