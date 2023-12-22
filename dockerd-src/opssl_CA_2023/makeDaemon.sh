#!/bin/bash

#############################################
#source ./makeDaemon.sh 140.96.111.117 ./tmp#
#############################################

echo "Total argument: $#"
echo "Script name: $0"
echo "Argument 1: $1"
echo "Argument 2: $2"


CNStr=$1

outDir=$2

if [ -d $outDir ]; then
    # 檔案 /path/to/dir/filename 存在
    echo "File $outDir exists."
else
    # 檔案 /path/to/dir/filename 不存在
    echo "File $outDir does not exists."
    mkdir $outDir
fi

openssl genrsa -out $outDir/server-key.pem 4096

openssl req -subj "/CN=$CNStr" -sha256 -new -key $outDir/server-key.pem -out $outDir/server.csr

echo subjectAltName = DNS:localhost,IP:$CNStr,IP:127.0.0.1 >> $outDir/extfile.cnf
echo extendedKeyUsage = serverAuth >> $outDir/extfile.cnf

openssl x509 -req -days 2650 -sha256 -in $outDir/server.csr -CA ./ca.pem -CAkey ./ca-key.pem  -CAcreateserial -out $outDir/server-cert.pem -extfile $outDir/extfile.cnf

openssl x509 -in $outDir/server-cert.pem -text

echo "mkdir /etc/docker/ssl"
echo "cp -v {ca,server-cert,server-key}.pem /etc/docker/ssl"

echo "cp damon.json /etc/docker/"

echo "edit /lib/systemd/system/docker.service as follows"

echo "ExecStart=/usr/bin/dockerd -H tcp://HOST_IP:2376 --data-root /home --authorization-plugin img-authz-plugin"