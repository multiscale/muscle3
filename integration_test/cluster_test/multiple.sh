#!/bin/bash

set -e

source /home/cerulean/shared/venv/bin/activate

CT=/home/cerulean/shared/cluster_test

muscle_manager --log-level=DEBUG --start-all $CT/multiple.ymmsl $CT/settings.ymmsl $CT/implementations.ymmsl

