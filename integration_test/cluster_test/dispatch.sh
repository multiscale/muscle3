#!/bin/bash

#SBATCH --time=0:1:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2

set -e

source /home/cerulean/venv/bin/activate

muscle_manager --log-level=DEBUG --start-all /home/cerulean/cluster_test/dispatch.ymmsl /home/cerulean/cluster_test/settings.ymmsl /home/cerulean/cluster_test/implementations.ymmsl

