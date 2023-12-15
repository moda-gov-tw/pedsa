#!/bin/bash
val_service_MariaDB_nrt="PET_join_Hadoop_MariaDB_nrt"

MariaDB_nrt=$(docker ps -qf name=$val_service_MariaDB_nrt)
MariaDB_nrt_ID=${MariaDB_nrt:0:12} 
val1L=${#MariaDB_nrt_ID}
if [ $val1L != 12 ]; then
    echo "get PET_join_Hadoop_MariaDB_nrt container ID error"
    return
fi

###########citc (daemon response is not running)###############
str="MariaDB_nrt_ID container id is $MariaDB_nrt_ID"
echo $str
echo "---------------------docker copy sql files---------------------------"

docker_result_str=$(docker cp ./syn_db.sql $MariaDB_nrt_ID":/)
echo $docker_result_str

docker_result_str=$(docker cp ./PetsService.sql $MariaDB_nrt_ID":/)

echo $docker_result_str

echo "leave --cleaning MariaDB_nrt-- "
# mysql --default-character-set=utf8 -u root -pcitcw200 </key_db1.sql

###########citc (daemon response is not running)###############

echo "---------------------cleaning mysql table---------------------------"
#key_db < key_db1.sql
#####docker exec -d $MariaDB_nrt_ID /bin/bash -c "mysql --default-character-set=utf8 -u root -pcitcw200 </syn_db.sql"
######docker exec -d $MariaDB_nrt_ID /bin/bash -c "mysql --default-character-set=utf8 -u root -pcitcw200 </PetsService.sql"
####docker exec -i $MariaDB_nrt_ID /bin/bash -c "source /initialDeIDServiceDBs_Tables.sh"

docker_result_str=$(docker exec -i $MariaDB_nrt_ID /bin/bash -c "mysql --default-character-set=utf8 -u root -pcitcw200 </key_db1.sql")
echo $docker_result_str
echo "leave --cleaning MariaDB_nrt-- "
# mysql --default-character-set=utf8 -u root -pcitcw200 </key_db1.sql
