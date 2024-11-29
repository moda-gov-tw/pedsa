#!/bin/bash

rm ./ssh_conf/config

echo "Host localhost" >> ./ssh_conf/config
echo "  StrictHostKeyChecking no" >> ./ssh_conf/config

echo "Host 0.0.0.0" >> ./config
echo "  StrictHostKeyChecking no" >> ./ssh_conf/config

echo "Host nodemasterSJOIN" >> ./ssh_conf/config
echo "   StrictHostKeyChecking no" >> ./ssh_conf/config
echo "   UserKnownHostsFile=/dev/null" >> ./ssh_conf/config

echo "Host *" >> ./ssh_conf/config
echo "   StrictHostKeyChecking no" >> ./ssh_conf/config
echo "   UserKnownHostsFile=/dev/null" >> ./ssh_conf/config

cd ./ssh_conf

if [ -f "id_rsa" ]; then
   rm id_rsa
fi

if [ -f "id_rsa.pub" ]; then
   rm id_rsa.pub
fi
ssh-keygen -t rsa -b 1024 -f id_rsa -N ''

cat ./id_rsa.pub >> ./authorized_keys
chmod 644 authorized_keys
chmod 644 config
chmod 600 id_rsa
chmod 644 id_rsa.pub

cd ..
