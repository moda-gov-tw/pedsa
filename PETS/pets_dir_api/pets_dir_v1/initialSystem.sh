#!/bin/bash

#######main #############################


#echo "enter old hadoop's passwd:"
#read -s hadoop_PWD

#echo "enter old mariaDB's passwd:"
#read -s DB_PWD
#echo $PWD

#20220301, citc add
docker stack rm PETSHadoopDir
docker stack rm PETSWebserviceDir
echo "---docker secret create - maria"
docker secret rm maria_file
val_random_file_name="maria_file"
val_d="citcw200"
retV=$(echo $val_d | docker secret create $val_random_file_name - 2>&1)
echo $retv

echo "---docker secret create - hadoop"
docker secret rm hadoop_file
val_random_file_name="hadoop_file"
val_d="citcw200@"
retV=$(echo $val_d | docker secret create $val_random_file_name - 2>&1)

echo "---docker secret create - deidwebservice"
docker secret rm ahcitcww
val_random_file_name="ahcitcww"
val_d="citcw200"
retV=$(echo $val_d | docker secret create $val_random_file_name -)
echo $retV

cd ./sourceCode/webService

echo "start CITCWebservice: $PWD"

#echo $PWD



#docker stack rm PETSWebserviceDir
docker stack deploy --with-registry-auth -c docker-compose.yml PETSWebserviceDir 
cd ../../
#echo $PWD
cd ./sourceCode/hadoop
echo "start CITCHadoop: $PWD"
#echo $PWD

#docker stack rm PETSHadoopDir
docker stack deploy --with-registry-auth -c docker-compose.yml PETSHadoopDir
cd ../../

echo "working Dir: $PWD"

