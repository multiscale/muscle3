#!/usr/bin/env bash
source python/build/venv/bin/activate

rm -f manager_location.txt

DONTPLOT=1 muscle_manager --start-all \
    --location-file manager_location.txt \
    rd_model.ymmsl \
    rd_settings.ymmsl \
    rd_manual_programs.ymmsl \
    rd_resources.ymmsl &

MUSCLE_MANAGER_PID=$!

while [ ! -s manager_location.txt ]; do
    sleep 0.1
done

python python/diffusion.py \
        --muscle-manager="$(cat manager_location.txt)" \
        --muscle-instance=macro

wait "$MUSCLE_MANAGER_PID"
