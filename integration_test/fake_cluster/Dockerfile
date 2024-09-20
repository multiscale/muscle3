FROM ghcr.io/naturalhpc/cerulean-test-docker-images/cerulean-fake-slurm-23-11:latest

RUN apt-get update && \
    apt-get remove -y openmpi-bin && \
    apt-get install -y python3-venv gcc g++ gfortran git build-essential xz-utils \
        bzip2 cmake

RUN cd /opt && \
    git clone --depth=100 --branch=releases/v0.22 https://github.com/spack/spack.git

RUN . /opt/spack/share/spack/setup-env.sh && \
    spack config add "modules:default:enable:[tcl]" && \
    spack install lmod && \
    echo >>/etc/profile && \
    echo ". $(spack location -i lmod)/lmod/lmod/init/bash" >>/etc/profile && \
    echo ". /opt/spack/share/spack/setup-env.sh" >>/etc/profile

# OpenMPI uses libmunge from munge, which needs to look for the munge unix socket
# in /run because that's where the apt-get installed munge we're actually running
# puts it. Munge doesn't have a configuration file, but it does have a compiled-in
# constant that can be set when building. So that's what we do here.
RUN bash -l -c 'spack install munge localstatedir=/'
RUN bash -l -c 'spack install openmpi+legacylaunchers+pmi schedulers=slurm'
RUN bash -l -c 'spack install mpich+slurm'
RUN bash -l -c 'spack install intel-oneapi-mpi'

# Enable Spack when running ssh -c
RUN echo >>/etc/ssh/sshd_config && \
    echo 'SetEnv BASH_ENV=/etc/profile' >>/etc/ssh/sshd_config

# Point workers to muscle3-headnode
COPY integration_test/fake_cluster/slurm.conf /usr/local/etc/slurm/slurm.conf

# Replace start-up scripts so we can run nodes separately
COPY integration_test/fake_cluster/start-services.sh /etc/start-services.sh
RUN chmod +x /etc/start-services.sh

# Disable ssh debug output
RUN sed -i -e 's/^LogLevel DEBUG3$//' /etc/ssh/sshd_config
RUN sed -i -e 's^Subsystem sftp /usr/lib/openssh/sftp-server -l DEBUG3^Subsystem sftp /usr/lib/openssh/sftp-server^' /etc/ssh/sshd_config


RUN apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /home/cerulean

