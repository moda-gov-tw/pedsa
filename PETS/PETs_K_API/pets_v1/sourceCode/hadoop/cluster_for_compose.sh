#!/bin/bash

# Bring the services up
function startServices {
  docker start nodemaster #node2 node3
  sleep 5
  echo ">> Starting hdfs ..."
  docker exec -u hadoop -it nodemaster start-dfs.sh
  sleep 5
  echo ">> Starting yarn ..."
  docker exec -u hadoop -d nodemaster start-yarn.sh
  sleep 5
  echo ">> Starting MR-JobHistory Server ..."
  docker exec -u hadoop -d nodemaster mr-jobhistory-daemon.sh start historyserver
  sleep 5
  echo ">> Starting Spark ..."
  #docker exec -u hadoop -d nodemaster start-master.sh
  #docker exec -u hadoop -d node2 start-slave.sh nodemaster:7077
  #docker exec -u hadoop -d node3 start-slave.sh nodemaster:7077
  sleep 5
  echo ">> Starting Spark History Server ..."
  docker exec -u hadoop nodemaster start-history-server.sh
  sleep 5
  echo ">> Preparing hdfs for hive ..."
  docker exec -u hadoop -it nodemaster hdfs dfs -mkdir -p /tmp
  docker exec -u hadoop -it nodemaster hdfs dfs -mkdir -p /user/hive/warehouse
  docker exec -u hadoop -it nodemaster hdfs dfs -chmod g+w /tmp
  docker exec -u hadoop -it nodemaster hdfs dfs -chmod g+w /user/hive/warehouse
  sleep 5
  echo ">> Starting Hive Metastore ..."
  docker exec -u hadoop -d nodemaster hive --service metastore

  sleep 6
  echo ">> citc, Starting keyMysql ..."
  docker exec -d keyMysql_nrt /start_ssh.sh
  docker exec -d keyMysql_nrt /bin/bash -c "mysql --default-character-set=utf8 -u root -pcitcw200 </key_db.sql"

  echo "Hadoop info @ nodemaster: http://172.28.1.15:8088/cluster"
  echo "DFS Health @ nodemaster : http://172.28.1.15:50070/dfshealth"
  #echo "MR-JobHistory Server @ nodemaster : http://172.28.1.1:19888"
  echo "Spark info @ nodemaster  : http://172.28.1.15:8080"
  echo "Spark History Server @ nodemaster : http://172.28.1.15:18080"
}

function stopServices {
  echo ">> Stopping Spark Master and slaves ..."
  docker exec -u hadoop -d nodemaster stop-master.sh
  #docker exec -u hadoop -d node2 stop-slave.sh
  #docker exec -u hadoop -d node3 stop-slave.sh
  echo ">> Stopping containers ..."
  docker stop nodemaster psqlhms keyMysql_nrt
}

if [[ $1 = "start" ]]; then
  echo ">> Formatting hdfs ..."
  docker exec -u hadoop -it hadoop_nodemaster_1 hdfs namenode -format
  startServices
  exit
fi


if [[ $1 = "stop" ]]; then
  stopServices
  docker rm nodemaster psqlhms keyMysql_nrt
  docker network rm hadoopnet
  exit
fi


if [[ $1 = "uninstall" ]]; then
  stopServices
  docker rmi hadoop spark hive postgresql-hms -f
  docker network rm hadoopnet
  docker system prune -f
  exit
fi

echo "Usage: cluster.sh start|stop|uninstall"
echo "                 start  - start existing containers"
echo "                 stop   - stop running processes"
echo "                 uninstall - remove all docker images"
