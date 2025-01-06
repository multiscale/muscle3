#!/bin/bash

set -e

env

source /home/cerulean/shared/venv/bin/activate

CT=/home/cerulean/shared/cluster_test

muscle_manager --log-level=DEBUG --start-all $CT/double.ymmsl $CT/settings.ymmsl $CT/implementations_srunmpi.ymmsl

