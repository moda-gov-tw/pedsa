#!/bin/bash

read -p "input mysql root new password: " naa
echo "before $naa"
#sed -i 's/mariaDB_passwd/$naa/g' key_db1.sql
sed -i "s/mariaDB_passwd/$naa/g" key_db1.sql

#docker-compose exec keyMysql_nrt /bin/bash -c "mysql --default-character-set=utf8 -u root -p$naa </key_db1.sql"

echo "after $naa"
sed -i "s/$naa/mariaDB_passwd1/g" key_db1.sql
