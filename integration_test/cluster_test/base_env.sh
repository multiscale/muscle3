#!/bin/bash

set -e

source /home/cerulean/shared/venv/bin/activate

CT=/home/cerulean/shared/cluster_test

unset PROFILE_LOADED
unset BASHRC_LOADED
export MANAGER_SHELL=1

muscle_manager --log-level=DEBUG --start-all $CT/base_env.ymmsl $CT/settings.ymmsl $CT/implementations.ymmsl

