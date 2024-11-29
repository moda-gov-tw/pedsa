#!/bin/bash

#########################################
#source ./makeCliCert.sh privacy3 ./tmp1#
#########################################

echo "Total argument: $#"
echo "Script name: $0"
echo "Argument 1: $1"
echo "Argument 2: $2"

CliUserName=$1

outDir=$2

if [ -d $outDir ]; then
    # 檔案 /path/to/dir/filename 存在
    echo "File $outDir exists."
else
    # 檔案 /path/to/dir/filename 不存在
    echo "File $outDir does not exists."
    mkdir $outDir
fi


openssl genrsa -out $outDir/key.pem 4096

echo $CliUserName
echo $outDir


openssl req -subj "/CN=$CliUserName" -new -key $outDir/key.pem -out $outDir/client.csr
echo extendedKeyUsage = clientAuth > $outDir/extfile-client.cnf
openssl x509 -req -days 2650 -sha256 -in $outDir/client.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out $outDir/cert.pem -extfile $outDir/extfile-client.cnf

openssl x509 -in $outDir/cert.pem -text

echo "mkdir -pv ~/.docker"
echo "cp -v {ca,cert,key}.pem ~/.docker"

echo "export DOCKER_HOST=tcp://HOST_IP:2376 DOCKER_TLS_VERIFY=1"