FROM ghcr.io/naturalhpc/cerulean-test-docker-images/cerulean-fake-slurm-23-11:latest

RUN apt-get update && \
    apt-get install -y python3-venv libopenmpi-dev

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /home/cerulean

