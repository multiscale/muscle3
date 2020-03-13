#!/bin/bash

if [ -z "$MUSCLE3_HOME" ] ; then
    echo 'Error: MUSCLE3_HOME is not set.'
    echo "Use 'MUSCLE3_HOME=/path/to/muscle3 $0' to run the example"
    exit 1
fi

. python/build/venv/bin/activate
muscle_manager reaction_diffusion_mc.ymmsl &

export LD_LIBRARY_PATH=$MUSCLE3_HOME/lib:$LD_LIBRARY_PATH

BINDIR=fortran/build

$BINDIR/reaction --muscle-instance=micro[0] >'micro[0].log' 2>&1 &
$BINDIR/reaction --muscle-instance=micro[1] >'micro[1].log' 2>&1 &
$BINDIR/diffusion --muscle-instance=macro[0] >'macro[0].log' 2>&1 &
$BINDIR/diffusion --muscle-instance=macro[1] >'macro[1].log' 2>&1 &
$BINDIR/load_balancer --muscle-instance=rr >rr.log 2>&1 &
$BINDIR/mc_driver --muscle-instance=mc >mc.log 2>&1 &

wait

