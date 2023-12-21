#!/bin/bash

# mac id

echo $1
echo $2
echo $3
echo $4
echo $5
echo $6

workDir= $(/home/hadoop/proj_/longTaskDir)

command_ = $(spark-submit --jars $workDir/udfEncrypt_7.jar,$workDir/myLogging_1.jar,$workDir/mysql-connector-java-8.0.13.jar $workDir\udfMacUID.py)
para_ = $1 $2 $3 $4 $5 $6
echo $command_
echo para_
docker exec -it  -u hadoop -it nodemaster /bin/bash -c $command_  $para_
