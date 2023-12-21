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
  docker network create --subnet=172.28.1.0/16 hadoopnet # create custom network

  # Starting Postresql Hive metastore
  echo ">> Starting postgresql hive metastore ..."
  docker run -d -v /etc/localtime:/etc/localtime:ro \
                -v $(pwd)/hiveMetaDB_postgre:/var/lib/postgresql/data \
              --net hadoopnet --ip 172.28.1.16 --hostname psqlhms --name psqlhms -it postgresql-hms:0.1

  
  docker run -d -v /etc/localtime:/etc/localtime:ro --net hadoopnet --ip 172.28.1.5 --hostname keyMysql_nrt --name keyMysql_nrt \
                              -e MYSQL_ROOT_PASSWORD=citcw200 -p 11099:3306 -p 3323:22\
                              -v $(pwd)/keyMysqlData:/var/lib/mysqli \
                              -d  mysql_ssh:5.7 
  
  sleep 5
  
  # 1 nodes
  echo ">> Starting nodes master and worker nodes ..."
  docker run -d -v $(pwd)/hive_conf:/home/hadoop/hive/conf \
                -v $(pwd)/spark_conf:/home/hadoop/spark/conf \
                -v $(pwd)/hadoop_conf:/home/hadoop/hadoop/etc/hadoop \
                -v $(pwd)/masterCodeDir:/home/hadoop/proj_ \
                -v $(pwd)/data:/home/hadoop/proj_/data \
                -v $(pwd)/dataMac:/home/hadoop/proj_/dataMac \
                -v $(pwd)/masterDir:/home/hadoop/data/nameNode \
                -v $(pwd)/ssh_conf:/home/hadoop/.ssh \
                -v /etc/localtime:/etc/localtime:ro \
                -p 5888:8888 -p 5922:22 -p 5188:8088 -p 5975:50075 -p 5970:50070 \
             --net hadoopnet --ip 172.28.1.15 --hostname nodemaster \
             --name nodemaster -it hive_nonroot:pyarrow01
  #docker run -d -v $(pwd)/spark_conf:/home/hadoop/spark/conf \
  #              -v $(pwd)/hadoop_conf:/home/hadoop/hadoop/etc/hadoop \
  #              -v /etc/localtime:/etc/localtime:ro \
  #           --net hadoopnet --ip 172.28.1.17 --hostname node2 --add-host nodemaster:172.28.1.15 --add-host node3:172.28.1.18 \
  #           --name node2 -it spark_nonroot:0.1
  #docker run -d -v $(pwd)/spark_conf:/home/hadoop/spark/conf \
  #              -v $(pwd)/hadoop_conf:/home/hadoop/hadoop/etc/hadoop \
  #              -v /etc/localtime:/etc/localtime:ro \
  #             --net hadoopnet --ip 172.28.1.18 --hostname node3 --add-host nodemaster:172.28.1.15 --add-host node2:172.28.1.17 \
  #             --name node3 -it spark_nonroot:0.1

  # Format nodemaster
  echo ">> Formatting hdfs ..."
  docker exec -u hadoop -it nodemaster hdfs namenode -format
  startServices
  #exit
fi


if [[ $1 = "stop" ]]; then
  stopServices
  docker rm nodemaster psqlhms keyMysql_nrt
  docker network rm hadoopnet
  #exit
fi


if [[ $1 = "uninstall" ]]; then
  stopServices
  docker rmi hadoop spark hive postgresql-hms -f
  docker network rm hadoopnet
  docker system prune -f
  #exit
fi

echo "Usage: cluster.sh start|stop|uninstall"
echo "                 start  - start existing containers"
echo "                 stop   - stop running processes"
echo "                 uninstall - remove all docker images"
