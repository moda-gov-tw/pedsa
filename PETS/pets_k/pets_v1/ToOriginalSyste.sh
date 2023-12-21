#!/bin/bash

#######main #############################


#echo "enter old hadoop's passwd:"
#read -s hadoop_PWD

#echo "enter old mariaDB's passwd:"
#read -s DB_PWD
#echo $PWD
cd ./sourceCode/webService

echo "start CITCWebservice: $PWD"

#echo $PWD

docker stack rm CITCWebservice
docker stack deploy -c docker-compose.yml CITCWebservice 
cd ../../
#echo $PWD
cd ./sourceCode/hadoop
echo "start CITCHadoop: $PWD"
#echo $PWD

docker stack rm CITCHadoop
docker stack deploy --with-registry-auth -c docker-compose.yml CITCHadoop
cd ../../

echo "working Dir: $PWD"


echo  -e "citcw200@ \n citcw200@" | bash update_nodemaster_secret.sh

#CITCHadoop_keyMysql_nrt.1.k2rsalt5s88te6dnjllanleo2

val_service_keyMysq_nrt="CITCHadoop_keyMysql_nrt"

keyMysq_nrt=$(docker ps -qf name=$val_service_keyMysq_nrt)
keyMysq_nrt_ID=${keyMysq_nrt:0:12} 
val1L=${#keyMysq_nrt_ID}
if [ $val1L != 12 ]; then
    echo "get keyMysq_nrt_ID container ID error"
    exit -1
fi

str="keyMysq_nrt_ID container id is $keyMysq_nrt_ID"
echo $str

#key_db < key_db1.sql
docker exec -d $keyMysq_nrt_ID /bin/bash -c "mysql --default-character-set=utf8 -u root -pcitcw200 </key_db1.sql"


echo  -e "citcw200@ \n citcw200 \n citcw200" | bash update_mariaDB_secret.sh
