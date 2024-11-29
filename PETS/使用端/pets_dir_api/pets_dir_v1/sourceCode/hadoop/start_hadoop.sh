#!/bin/bash

echo "in start_hadoop.sh"
echo "whoami"
whoami
echo "pwd"
pwd
cd ~
echo "current dir(~)"
pwd
echo "ps -ef"
ps -ef | grep sshd

#ENV PATH $JAVA_HOME/bin:$PATH
#ENV PATH $HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH

PATH=$JAVA_HOME/bin:$PATH
PATH=$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH
PATH=$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH
PATH=$HIVE_HOME/bin:$PATH
#echo "echo PATH"
#echo $PATH
#echo "ls -al .ssh"
#ls -al /home/hadoop/.ssh
echo "echo JAVA_HOME"
echo $JAVA_HOME
#ls -al /home/hadoop/hadoop/sbin/start-dfs.sh
echo ">> Formatting hdfs ..."
if [ -f "/home/hadoop/data/nameNode/current/VERSION" ]; then
	echo "/home/hadoop/data/nameNode/current/VERSION exixts..."
	echo 'N'|hdfs namenode -format
else
	echo "/home/hadoop/data/nameNode/current/VERSION does not exixt..."
	echo 'Y'|hdfs namenode -format
fi


#echo 'Y'|hdfs namenode -format
sleep 5
echo ">> Starting hdfs ..."
echo "hostname"
hostname

start-dfs.sh

sleep 10
echo ">> Starting yarn ..."
stop-yarn.sh
start-yarn.sh
#start-yarn.sh

sleep 10
echo ">> Starting MR-JobHistory Server ..."
mr-jobhistory-daemon.sh start historyserver
sleep 5
echo ">> Starting Spark History Server ..."
start-history-server.sh
sleep 5
echo ">> Preparing hdfs for hive ..."
hdfs dfs -mkdir -p /tmp
hdfs dfs -mkdir -p /user/hive/warehouse
hdfs dfs -chmod g+w /tmp
hdfs dfs -chmod g+w /user/hive/warehouse
sleep 5
echo ">> Starting Hive Metastore ..."
hive --service metastore

whoami
echo "leave start_hadoop.sh"
