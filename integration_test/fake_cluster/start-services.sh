#!/bin/bash
echo -e "\nstarting syslog-ng..."
syslog-ng


echo -e "\nstarting munged..."
setuser munge /usr/sbin/munged --foreground > /var/log/munged.out.log 2> /var/log/munged.err.log &

echo -n -e "\nwaiting for munged to start..."
while [ ! -e /run/munge/munge.socket.2 ] ; do
    sleep 1
    echo '.'
done
echo


NODENAME=$(hostname)

if [ "a${NODENAME}" == "amuscle3-headnode"  ] ; then
    # Run as a headnode
    echo -e "\nstarting mariadb..."
    setuser mysql /usr/bin/mariadbd-safe >/var/log/mariadb.out.log 2>/var/log/mariadb.err.log &

    echo -n -e "\nwaiting for mariadb to start..."
    while ! nc -z localhost 3306 ; do
        sleep 1
        echo '.'
    done
    echo


    echo -e "\nstarting slurmdbd..."
    /usr/local/sbin/slurmdbd -D >/var/log/slurmdbd.out.log 2>/var/log/slurmdbd.err.log &

    echo -n -e "\nwaiting for slurmdbd to start..."
    while ! nc -z localhost 6819 ; do
        sleep 1
        echo '.'
    done
    echo


    echo -e "\nstarting slurmctld..."
    /usr/local/sbin/slurmctld -D -c -vvvv > /var/log/slurmctld.out.log 2> /var/log/slurmctld.err.log &

    echo -n -e "\nwaiting for slurmctld to start..."
    while ! nc -z localhost 6817 ; do
        sleep 1
        echo '.'
    done
    echo


    echo -e "\nmaking accounting readable to users..."
    /bin/chmod -R og+rX /var/log/slurm

else
    # Run as a compute node

    echo -e "\nstarting compute node..."
    /usr/local/sbin/slurmd -D -N ${NODENAME} > /var/log/slurmd.out.log 2> /var/log/slurmd.err.log &
fi

echo -e "\nstarting sshd..."
/usr/sbin/sshd -De > /var/log/sshd.out.log 2> /var/log/sshd.err.log &

echo -e "\nStartup complete"

sleep infinity

