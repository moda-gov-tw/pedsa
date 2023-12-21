#!/bin/bash


docker exec -d hadoop_keyMysql_nrt_1 /bin/bash -c "mysql --default-character-set=utf8 -u root -pcitcw200 </key_db1.sql"
#docker exec -d hadoop_keyMysql_nrt_1 /bin/bash -c "rm /key_db1.sql"
echo "start maria db ..."
sleep 30
echo "rm passwd file ..."
cat /dev/null > ./key_db1.sql

