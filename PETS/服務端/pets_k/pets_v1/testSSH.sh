#!/bin/bash


checkHDFSPWD(){
#update_deidadmin_pw1(){
    #local PWD1=$1

    local val_worker_service=$1 #"CITCWebservice_worker"

    
    local retV
    #local val_nodemaster_service=$4 #"CITCHadoop_nodemaster"
    #local val_deidweb_service=$5
    # get hadoop_keyMsql_nrt container id

    echo '-enter update_deidadmin_pw------------'

    worer1=$(docker ps -qf name=$val_worker_service)
    val_worker_ID1=${worer1:0:12}
    val1L=${#val_worker_ID1}
    if [ $val1L != 12 ]; then
        echo "get webservice_worker service id error"
        exit -1
    fi
    str="webservice_worker container ID is $val_worker_ID1"
    echo $str

    #for webservice_worker service#########################################



    retV=$(docker exec -it $val_worker_ID1 bash -c "python /app/app/devp/config/ssh_hdfs.py" 2>&1)
    #echo "---------00000------------"
    #echo $retV
    #echo "---------11111------------"

    if [[ $retV == *"Authentication failed"* ]]; then
        echo "!!!! $PWD1 error!!!!!"
        echo $retV
        exit 6  
    fi 
    #retV=$(docker exec -it $val_node_ID1 bash -c "mysql -uroot -p$PWD < ")
    ########################################################################
    echo '-leave checkHDFSPWD------------'


}

worker_service="CITCWebservice_worker"

#echo "enter old hadoop's passwd:"
#read -s hadoop_PWD
#str="hadoop_PWD is $hadoop_PWD"
#echo $str
#hadoop_PWD="w900citc1"
echo "-----check check HDFS PWD-----------"
checkHDFSPWD $worker_service

e_xode=$?

echo $e_xode
echo "-----leave check check HDFS PWD-----------"




