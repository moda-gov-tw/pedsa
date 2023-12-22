#!/bin/bash

#######main #############################


#echo "enter old hadoop's passwd:"
#read -s hadoop_PWD

#echo "enter old mariaDB's passwd:"
#read -s DB_PWD
#echo $PWD

#20220301, citc add

echo "---docker secret create - maria"
#val_random_file_name="maria_file"
#val_d="citcw200"
#retV=$(echo $val_d | docker secret create $val_random_file_name - 2>&1)
#echo $retv

echo "---docker secret create - hadoop"
#val_random_file_name="hadoop_file"
#val_d="citcw200@"
#retV=$(echo $val_d | docker secret create $val_random_file_name - 2>&1)

echo "---docker secret create - deidwebservice"
#val_random_file_name="ahcitcww"
#val_d="citcw200"
#retV=$(echo $val_d | docker secret create $val_random_file_name -)
#echo $retV

#cd ./sourceCode/webService

#echo "start PETWebservice: $PWD"

#echo $PWD

#docker stack rm PETWebservice
#docker stack deploy --with-registry-auth -c docker-compose.yml PETWebservice 
#cd ../../
#echo $PWD
cd ./sourceCode/hadoop
echo "start PETHadoop: $PWD"
echo $PWD

docker stack rm PET_join_Hadoop
docker stack deploy --with-registry-auth -c docker-compose.yml PET_join_Hadoop
cd ../../

echo "working Dir: $PWD"

