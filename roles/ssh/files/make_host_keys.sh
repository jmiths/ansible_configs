#!/bin/bash
# This script generates a series of host keys for use on machines
#if [ $# -ne 1 ]
#then
#	echo "Please give me only one arg or modify script to iterate through dirs"
#	exit 1
#fi

#pushd $1

# Generate keys for ws's
#for i in {0..99}
#do
#	if [[ i -lt 10 ]]
#	then
#		i='0'$i
#	fi
#	ws='ws'$i
	
#	ws="shade"	

#	if ! [ -d $ws ]
#	then
#		mkdir $ws
#	fi
for ws in host_keys/*
do
	if ! [ -f "$ws/ssh_host_key" ]
	then
		ssh-keygen -f "$ws/ssh_host_key" -N '' -t rsa1 &> /dev/null
	fi

	if ! [ -f "$ws/ssh_host_rsa_key" ]
	then
		ssh-keygen -f "$ws/ssh_host_rsa_key" -N '' -t rsa &> /dev/null
	fi

	if ! [ -f "$ws/ssh_host_dsa_key" ]
	then
		ssh-keygen -f "$ws/ssh_host_dsa_key" -N '' -t dsa &> /dev/null
	fi

	if ! [ -f "$ws/ssh_host_ecdsa_key" ]
	then
		ssh-keygen -f "$ws/ssh_host_ecdsa_key" -N '' -t ecdsa &> /dev/null
	fi

	if ! [ -f "$ws/ssh_host_ed25519_key" ]
	then
		ssh-keygen -f "$ws/ssh_host_ed25519_key" -N '' -t ed25519 &> /dev/null
	fi

done

#popd
