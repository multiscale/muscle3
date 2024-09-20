#!/bin/bash

#SBATCH --time=0:1:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1

set -e

source /home/cerulean/shared/venv/bin/activate

CT=/home/cerulean/shared/cluster_test

muscle_manager --log-level=DEBUG --start-all $CT/single.ymmsl $CT/settings.ymmsl $CT/implementations.ymmsl

