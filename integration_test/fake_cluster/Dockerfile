FROM ghcr.io/naturalhpc/cerulean-fake-slurm-base:latest
# FROM naturalhpc/cerulean-fake-slurm-base:latest

RUN . /opt/spack/share/spack/setup-env.sh && \
    . $(spack location -i lmod)/lmod/lmod/init/bash && \
    spack install openmpi@3.1.6 +legacylaunchers +pmi schedulers=slurm \
    ^$(spack find --deps slurm@20-11 | grep pmix |  tr -d ' ') \
    ^$(spack find --format "slurm/{hash}" slurm@20-11)

RUN . /opt/spack/share/spack/setup-env.sh && \
    . $(spack location -i lmod)/lmod/lmod/init/bash && \
    spack install openmpi@3.1.6 +legacylaunchers +pmi schedulers=slurm \
    ^$(spack find --deps slurm@21-08 | grep pmix |  tr -d ' ') \
    ^$(spack find --format "slurm/{hash}" slurm@21-08)

RUN . /opt/spack/share/spack/setup-env.sh && \
    . $(spack location -i lmod)/lmod/lmod/init/bash && \
    spack install openmpi@3.1.6 +legacylaunchers +pmi schedulers=slurm \
    ^$(spack find --deps slurm@22-05 | grep pmix |  tr -d ' ') \
    ^$(spack find --format "slurm/{hash}" slurm@22-05)

RUN . /opt/spack/share/spack/setup-env.sh && \
    . $(spack location -i lmod)/lmod/lmod/init/bash && \
    spack install openmpi@3.1.6 +legacylaunchers +pmi schedulers=slurm \
    ^$(spack find --deps slurm@23-02 | grep pmix |  tr -d ' ') \
    ^$(spack find --format "slurm/{hash}" slurm@23-02)

RUN . /opt/spack/share/spack/setup-env.sh && \
    . $(spack location -i lmod)/lmod/lmod/init/bash && \
    spack install openmpi@4.1.6 +legacylaunchers +pmi schedulers=slurm \
    ^$(spack find --deps slurm@23-11 | grep pmix |  tr -d ' ') \
    ^$(spack find --format "slurm/{hash}" slurm@23-11)

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

