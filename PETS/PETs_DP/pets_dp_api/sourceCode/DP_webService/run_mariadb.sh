
# sleep 5
sudo docker restart webservice_keyMysql_nrt_1 #mariadb_nrt

echo ">> citc, Starting keyMysql ..."
# docker exec -d mariadb_nrt /start_ssh.sh

sleep 5
#docker exec -d mariadb_nrt /bin/bash -c "mysql --default-character-set=utf8 -u root -pcitcw200 </key_db.sql"


#docker exec -it webservice_keyMysql_nrt_1 /bin/bash -c "/usr/bin/mysqladmin -u root password citcw200"


# docker exec -d mariadb_nrt /bin/bash -c "mysql --default-character-set=utf8 -u root -pcitcw200 </key_db.sql"
sudo docker exec -it webservice_keyMysql_nrt_1 /bin/bash -c "mysql --default-character-set=utf8 -u root -pcitcw200 < var/lib/mysql/syn_db.sql"

# docker exec -it webservice_keyMysql_nrt_1 /bin/bash

