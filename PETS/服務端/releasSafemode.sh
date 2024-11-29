#!/bin/bash



#PET_join_Hadoop_nodemaster
PET_join_Hadoop_nodemaster_id=$(docker ps -aqf "name=PET_join_Hadoop_nodemaster")

IFS=', ' read -r -a array <<< "$PET_join_Hadoop_nodemaster_id"

for element in "${array[@]}"
do
    echo "$element"
    PET_join_Hadoop_nodemaster_id="$element"
    break
done




val1L=${#PET_join_Hadoop_nodemaster_id} #len=12
echo "-"$val1L"-"
if [ $val1L == 12 ]; then
    echo "-------------------PET_join_Hadoop_nodemaste------------------get safemode--- "
    mode_result=$(docker exec $PET_join_Hadoop_nodemaster_id hdfs dfsadmin -safemode get)
    if [ "$mode_result" = "Safe mode is ON" ]; then
    	echo "Safe mode is ON--"
       docker exec $PET_join_Hadoop_nodemaster_id hdfs dfsadmin -safemode leave
       sleep 5
       docker exec $PET_join_Hadoop_nodemaster_id hdfs dfsadmin -safemode get
    else
       echo "Safe mode is OFF--"   
    fi
else
	echo "get PET_join_Hadoop_nodemaster_id error"
    #echo "----#######-----------起始--rm MariaDB 失敗，注意MariaDB狀態--------######----------- "
    echo "-"$PET_join_Hadoop_nodemaster_id"-"
    sleep 20
    return
fi

#PETSHadoop_nodemaster
PETSHadoop_nodemaster_id=$(docker ps -aqf "name=PETSHadoop_nodemaster")
val1L=${#PETSHadoop_nodemaster_id} #len=12
if [ $val1L == 12 ]; then
    echo "----------------PETSHadoop_nodemaster (pets_k)---------------------get safemode--- "
    mode_result=$(docker exec $PETSHadoop_nodemaster_id hdfs dfsadmin -safemode get)
    if [ "$mode_result" = "Safe mode is ON" ]; then
    	echo "Safe mode is ON--" 
       docker exec $PETSHadoop_nodemaster_id hdfs dfsadmin -safemode leave
       sleep 5
       docker exec $PETSHadoop_nodemaster_id hdfs dfsadmin -safemode get
    else
       echo "Safe mode is OFF--"   
    fi
else
	echo "get PET_join_Hadoop_nodemaster_id error"
    #echo "----#######-----------起始--rm MariaDB 失敗，注意MariaDB狀態--------######----------- "
    sleep 20
    return
fi

