#!/bin/bash

# Script parameters from arguments
configfile=$1
HostIP=$(dig +short myip.opendns.com @resolver1.opendns.com)


apt-get update
apt-get install software-properties-common -y
apt-add-repository ppa:ansible/ansible -y
apt-get update
apt-get install ansible -y
apt-get install unzip -y

cd /home/

if [ -e ConfigFiles.* ];
then
  if [ -d /home/ConfigFiles ];
  then
        rm -rf ConfigFiles.*
	rm -rf /home/ConfigFiles
	echo "directory delete"
  fi
fi
wget $configfile
unzip ConfigFiles.zip -d /home/ConfigFiles/


HOME=/root ansible-playbook /home/ConfigFiles/ansible/docker_install.yml  --extra-vars "HostIP=$HostIP" -vvv


