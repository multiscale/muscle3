FROM ghcr.io/naturalhpc/cerulean-fake-slurm-23-11:latest
# FROM naturalhpc/cerulean-fake-slurm-23-11:latest

RUN . /opt/spack/share/spack/setup-env.sh && \
    . $(spack location -i lmod)/lmod/lmod/init/bash && \
    spack install openmpi+legacylaunchers+pmi schedulers=slurm ^pmix@3.2.3 ^slurm/dckfty

# RUN . /opt/spack/share/spack/setup-env.sh && \
#     . $(spack location -i lmod)/lmod/lmod/init/bash && \
#     spack install mpich+slurm pmi=pmix ^pmix@3.2.3

# RUN . /opt/spack/share/spack/setup-env.sh && \
#     . $(spack location -i lmod)/lmod/lmod/init/bash && \
#     spack install intel-oneapi-mpi ^pmix@3.2.3

COPY integration_test/fake_cluster/cgroup.conf /etc/slurm/cgroup.conf

# Disable ssh debug output
RUN sed -i -e 's/^LogLevel DEBUG3$//' /etc/ssh/sshd_config
RUN sed -i -e 's^Subsystem sftp /usr/lib/openssh/sftp-server -l DEBUG3^Subsystem sftp /usr/lib/openssh/sftp-server^' /etc/ssh/sshd_config


RUN apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /home/cerulean

