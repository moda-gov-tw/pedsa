#!/bin/bash


if [ -d "/var/lib/mysql/DeIDService" ]; then
        echo "/var/lib/mysql/mysql exixts..."
        #echo "using the last setting ..."
        echo "does not clear DB content ..."
else
        echo "/var/lib/mysql/mysql does not exixt..."
        echo "creating the new deIDService tables ..."
        #mysql_install_db --user=mysql --auth-root-authentication-method=socket --auth-root-socket-user=root
        mysql --default-character-set=utf8 -u root -pcitcw200 </key_db1.sql
        echo "ps -aux---"
        ps -aux
fi

