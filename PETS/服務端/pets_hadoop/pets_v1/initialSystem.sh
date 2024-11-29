#!/bin/bash

#######main #############################


#echo "enter old hadoop's passwd:"
#read -s hadoop_PWD

#echo "enter old mariaDB's passwd:"
#read -s DB_PWD
#echo $PWD

#20240123, citc add

echo "---docker secret create - maria"
val_maria=$(docker secret inspect --format='{{.Spec.Name}}' maria_file)
val_random_file_name="maria_file"
if [[ "$val_random_file_name" == "$val_maria" ]]; then
	echo "---maria secret existed"
else
	val_d="citcw200"
    retV=$(echo $val_d | docker secret create $val_random_file_name -)
    echo $retV
fi	

#val_d="citcw200"
#retV=$(echo $val_d | docker secret create $val_random_file_name - 2>&1)
#echo $retv

echo "---docker secret create - hadoop"
val_hadoop=$(docker secret inspect --format='{{.Spec.Name}}' hadoop_file)
val_random_file_name="hadoop_file"
if [[ "$val_random_file_name" == "$val_hadoop" ]]; then
	echo "---hadoop secret existed"
else
	val_d="citcw200@"
    retV=$(echo $val_d | docker secret create $val_random_file_name -)
    echo $retV
fi	

echo "---docker secret create - deidwebservice"
val_ahcitcww=$(docker secret inspect --format='{{.Spec.Name}}' ahcitcww)
val_random_file_name="ahcitcww"
if [[ "$val_random_file_name" == "$val_ahcitcww" ]]; then
	echo "---deidwebservice secret existed"
else
	val_d="citcw200"
    retV=$(echo $val_d | docker secret create $val_random_file_name -)
    echo $retV
fi

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

