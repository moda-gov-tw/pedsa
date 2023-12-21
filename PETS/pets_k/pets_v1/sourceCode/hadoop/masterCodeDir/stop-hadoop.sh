#!/bin/bash

# stop HDFS services
$HADOOP_INSTALL/sbin/stop-yarn.sh
echo -e "\n"
$HADOOP_INSTALL/sbin/stop-dfs.sh


echo -e "\n"
rm -rf /tmp

echo -e "\n"
# format HDFS meta data
hadoop namenode -format
