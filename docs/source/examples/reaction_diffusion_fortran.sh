#!/bin/bash

if [ -z "$MUSCLE3_HOME" ] ; then
    echo 'Error: MUSCLE3_HOME is not set.'
    echo "Use 'MUSCLE3_HOME=/path/to/muscle3 $0' to run the example"
    exit 1
fi

echo 'Running reaction-diffusion in Fortran'

. python/build/venv/bin/activate
muscle_manager reaction_diffusion.ymmsl &

manager_pid=$!

export LD_LIBRARY_PATH=$MUSCLE3_HOME/lib:$LD_LIBRARY_PATH
BINDIR=fortran/build

$BINDIR/reaction --muscle-instance=micro >'micro.log' 2>&1 &
$BINDIR/diffusion --muscle-instance=macro >'macro.log' 2>&1 &

touch muscle3_manager.log
tail -f muscle3_manager.log --pid=${manager_pid}

wait

