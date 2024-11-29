#!/bin/bash



#citc, 20220226 mark, password in /run/secrets
#echo  -e "citcw200@ \n citcw200@" | bash update_nodemaster_secret.sh

#CITCHadoop_keyMysql_nrt.1.k2rsalt5s88te6dnjllanleo2
#sleep 5
val_service_MariaDB_nrt="CITCHadoop_MariaDB_nrt"

MariaDB_nrt=$(docker ps -qf name=$val_service_MariaDB_nrt)
MariaDB_nrt_ID=${MariaDB_nrt:0:12} 
val1L=${#MariaDB_nrt_ID}
if [ $val1L != 12 ]; then
    echo "get MariaDB_nrt_ID container ID error"
    exit -1
fi
###########citc (daemon response is not running)###############
str="MariaDB_nrt_ID container id is $MariaDB_nrt_ID"
echo $str
echo "---------------------update mysql table---------------------------"
#key_db < key_db1.sql
#docker exec -d $MariaDB_nrt_ID /bin/bash -c "mysql --default-character-set=utf8 -u root -pcitcw200 </key_db1.sql"
#docker exec -i $MariaDB_nrt_ID /bin/bash -c "source /initialDeIDServiceDBs_Tables.sh"
docker_result_str=$(docker exec -i $MariaDB_nrt_ID /bin/bash -c "source /initialDeIDServiceDBs_Tables.sh")
echo $docker_result_str
echo "leave --setting MariaDB_nrt-- "
sleep 5

#citc, 20220226 mark, password in /run/secrets
#echo  -e "citcw200@ \n citcw200 \n citcw200" | bash update_mariaDB_secret.sh

update_deidweb_pw(){

    local val_deidweb_service=$1 #"CITCWebservice_deidweb"
    local retV
    #local val_deidweb_service=$5
    # get hadoop_keyMsql_nrt container id

    echo '-enter update_deidweb_pw------------'

    #for changing deidweb password##########################################
    echo "-----start change  deidweb password ------------"
    # get deidweb container id
    deidweb=$(docker ps -qf name=$val_deidweb_service)
    val_deidweb_ID=${deidweb:0:12} 

    #str="docker cp ./appsettings.json $val_deidweb_ID:/app/appsettings.json"
    #echo $str
    #retV=$(docker cp ./appsettings.json $val_deidweb_ID:/app/appsettings.json)
    #echo $retV
    sleep 5
    retV=$(docker exec -i $val_deidweb_ID bash -c "python /app/process_appsettings.py")
    echo $retV
    echo '-leave update_deidweb_pw------------'
    #################################################################################


}
deidweb_service="CITCWebservice_deidweb"
update_deidweb_pw $deidweb_service

echo "leave --setting deidweb_-- "

