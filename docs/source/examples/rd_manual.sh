#!/usr/bin/env bash
source python/build/venv/bin/activate

rm -f manager_location.txt

# Start muscle_manager in the background, which starts the micro instance
muscle_manager --start-all \
    --location-file manager_location.txt \
    rd_manual.ymmsl \
    rd_settings.ymmsl \
    rd_resources.ymmsl &

MUSCLE_MANAGER_PID=$!

# Wait until the manager has written its network location
while [ ! -s manager_location.txt ]; do
    sleep 0.1
done

# Manually start the macro instance
python python/diffusion.py \
        --muscle-manager="$(cat manager_location.txt)" \
        --muscle-instance=macro

# Wait for the manager process to complete
wait "$MUSCLE_MANAGER_PID"
