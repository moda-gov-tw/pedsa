#!/bin/bash


#service  ssh  stop
#service  ssh  start
echo "in start_ssh1. for running mysqld..."
/usr/sbin/sshd  -D&
echo "strating marisdb..."


#citc, mark 20220121###################################
#/var/lib/mysql
if [ -d "/var/lib/mysql" ]; then
    #檔案 /path/to/dir/filename存在
    echo "/var/lib/mysql exists."
    chown -R 999:999 /var/lib/mysql
else
    #檔案 /path/to/dir/filename 不存在
    echo "/var/lib/mysql does not exists."
    exit 15
fi
#citc, mark 20220121###################################
#/key_db1.sql
if [ -f "/key_db1.sql" ]; then
    #檔案 /path/to/dir/filename存在
    echo "/key_db1.sql exists."
    chown -R hadoop:cdpg /var/lib/mysql
else
    #檔案 /path/to/dir/filename 不存在
    echo "/key_db1.sql does not exists."
    exit 16
fi 

#citc, mark 20220121###################################
#/initialDeIDServiceDBs_Tables.sh
#./initialSecrets.sh:25 #docker exec -d $MariaDB_nrt_ID /bin/bash -c "source /initialDeIDServiceDBs_Tables.sh"
if [ -f "/initialDeIDServiceDBs_Tables.sh" ]; then
    #檔案 /path/to/dir/filename存在
    echo "/initialDeIDServiceDBs_Tables.sh exists."
    chown -R hadoop:cdpg /initialDeIDServiceDBs_Tables.sh
else
    #檔案 /path/to/dir/filename 不存在
    echo "/initialDeIDServiceDBs_Tables.sh does not exists."
    exit 18
fi 













echo "ps -aux---"
ps -aux

echo "(1) ls -al /var/run/mysqld/---"
ls -al /var/run/mysqld/

rm /var/run/mysqld/mysqld.sock
   

# /var/run/mariadb/mariadb.pid
echo "(1) ls -al /var/run/mariadb/---"
ls -al /var/run/mariadb/

echo "test -1 (default user mysql id is:)---"
id mysql

echo "test -2 (whoami is:)---"
whoami


echo "test -3 (/var/lib/mysql:)---"
ls -al /var/lib/mysql

echo "test -4 (/var/lib/mysql:)---"
chown -R mysql:mysql /var/lib/mysql


echo "test -5 (mysql_install_db --user=mysql)---"
if [ -d "/var/lib/mysql/mysql" ]; then
	echo "/var/lib/mysql/mysql exixts..."
	echo "mysqld is already running (user = mysql, the system table mysql.user is created )"
else
	echo "/var/lib/mysql/mysql does not exixt..."
	echo "creating the new mysql.user table ..."
        mysql_install_db --user=mysql --auth-root-authentication-method=socket --auth-root-socket-user=root
        echo "ps -aux---"
        ps -aux
fi


echo "test 0---------------------------------"
sleep 15
mysqld --user=mysql --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci --innodb-flush-method=fsync

echo "test 1--------"
#echo "strating initial db table..."
#mysqld < /key_db1.sql
#mysql --default-character-set=utf8 </key_db1.sql
echo "test 2---"
echo "ps -aux---"
ps -aux


#run source settingDB_passwdAndSchema.sh, after all docker container running


