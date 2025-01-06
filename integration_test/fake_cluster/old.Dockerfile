FROM ghcr.io/naturalhpc/cerulean-fake-slurm-base-old:latest
# FROM naturalhpc/cerulean-fake-slurm-base-old:latest

RUN . /opt/spack/share/spack/setup-env.sh && \
    . $(spack location -i lmod)/lmod/lmod/init/bash && \
    spack install openmpi@2.0.0 +legacylaunchers +pmi schedulers=slurm \
    ^$(spack find --deps slurm@17-02 | grep pmix |  tr -d ' ') \
    ^$(spack find --format "slurm/{hash}" slurm@17-02)

RUN . /opt/spack/share/spack/setup-env.sh && \
    . $(spack location -i lmod)/lmod/lmod/init/bash && \
    spack install openmpi@2.0.0 +legacylaunchers +pmi schedulers=slurm \
    ^$(spack find --deps slurm@17-11 | grep pmix |  tr -d ' ') \
    ^$(spack find --format "slurm/{hash}" slurm@17-11)

RUN . /opt/spack/share/spack/setup-env.sh && \
    . $(spack location -i lmod)/lmod/lmod/init/bash && \
    spack install openmpi@2.0.0 +legacylaunchers +pmi schedulers=slurm \
    ^$(spack find --deps slurm@18-08 | grep pmix |  tr -d ' ') \
    ^$(spack find --format "slurm/{hash}" slurm@18-08)

RUN . /opt/spack/share/spack/setup-env.sh && \
    . $(spack location -i lmod)/lmod/lmod/init/bash && \
    spack install openmpi@2.1.6 +legacylaunchers +pmi schedulers=slurm \
    ^$(spack find --deps slurm@19-05 | grep pmix |  tr -d ' ') \
    ^$(spack find --format "slurm/{hash}" slurm@19-05)

RUN . /opt/spack/share/spack/setup-env.sh && \
    . $(spack location -i lmod)/lmod/lmod/init/bash && \
    spack install openmpi@2.1.6 +legacylaunchers +pmi schedulers=slurm \
    ^$(spack find --deps slurm@20-02 | grep pmix |  tr -d ' ') \
    ^$(spack find --format "slurm/{hash}" slurm@20-02)

RUN . /opt/spack/share/spack/setup-env.sh && \
    . $(spack location -i lmod)/lmod/lmod/init/bash && \
    spack install intel-oneapi-mpi@2021.14.0

# RUN . /opt/spack/share/spack/setup-env.sh && \
#     . $(spack location -i lmod)/lmod/lmod/init/bash && \
#     spack install mpich+slurm pmi=pmix ^pmix@3.2.3

# Disable ssh debug output
RUN sed -i -e 's/^LogLevel DEBUG3$//' /etc/ssh/sshd_config
RUN sed -i -e 's^Subsystem sftp /usr/lib/openssh/sftp-server -l DEBUG3^Subsystem sftp /usr/lib/openssh/sftp-server^' /etc/ssh/sshd_config


RUN apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /home/cerulean

