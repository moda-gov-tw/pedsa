#!/bin/bash

######20200611##########################

##############################################
# parse_result: copy swarm secret to services#
##############################################
parse_result_Maria(){

  local val_service=$1

  while read line; do    
     
    sec_name=$(echo $line | cut -d" " -f 2)
    echo "${sec_name}"
    val1L=${#sec_name}
    echo "${val1L}"

    if [[ $val_service != *"deidweb"* ]]; then
        if [ $val1L == 8 ] && [[ $sec_name != *"ahcitcww"* ]]; then
            retV=$(docker service update --secret-add $sec_name $val_service 2>&1)
            retPID=$!
            #wait retPID
            echo "---------$retPID is complete--------"
             
            if [[ $retV == *"InvalidArgument"* ]]; then
                echo $retV
                continue
            fi
        fi
    fi

    if [[ $val_service == *"deidweb"* ]]; then
        if [ $val1L == 8 ]; then
            retV=$(docker service update --secret-add $sec_name $val_service 2>&1)
            retPID=$!
            #wait retPID
            echo "---------$retPID is complete--------"
             
            if [[ $retV == *"InvalidArgument"* ]]; then
                echo $retV
                continue
            fi
        fi
    fi    

  done
  digestF="digestF_Maria"

  retV=$(docker service update --secret-add $digestF $val_service 2>&1)
  retPID=$!
  #wait retPID

  echo "---------leave parse_result_Maria--------"
}


parse_result_Hdfs(){


    local val_service=$1

    if [[ $val_service != *"worker"* ]]; then
        while read line; do         
            sec_name=$(echo $line | cut -d" " -f 2)
            echo "${sec_name}"
            val1L=${#sec_name}
            echo "${val1L}"

             
                                                   
            if [ $val1L == 8 ] && [[ $sec_name != *"ahcitcww"* ]]; then
                retV=$(docker service update --secret-add $sec_name $val_service 2>&1)
                #retPID=$!
                #wait retPID
                #echo "---------$retPID is complete--------"
                 
                if [[ $retV == *"InvalidArgument"* ]]; then
                    echo $retV
                    continue
                fi
             fi
        done
    fi

    digestF="digestF_Hdfs"

    retV=$(docker service update --secret-add $digestF $val_service 2>&1)
    retPID=$!
    #wait retPID
    echo "---------leave parse_result_Hdfs--------"
}


update_hadoop_pw(){
    local PWD0=$1

    #local val_worker_service=$2 #"CITCWebservice_worker"
    local val_nodemaster_service=$2 #"CITCHadoop_nodemaster"
    local retV
    #local val_deidweb_service=$5
    # get hadoop_keyMsql_nrt container id

    echo '-enter update_hadoop_pw------------'

    #for changing hadoop_nodemaster password##########################################
    echo "-----start change  hadoop_nodemaster password ------------"
    # get nodemaster container id
    nodemaster=$(docker ps -qf name=$val_nodemaster_service)
    val_nodemaster_ID=${nodemaster:0:12} 
    str="docker exec -it $val_nodemaster_ID bash -c echo hadoop:$PWD0 |chpasswd"
    echo $str

    retV=$(docker exec -it $val_nodemaster_ID bash -c "echo hadoop:$PWD0 |chpasswd")
    echo $retV

    echo '-leave update_hadoop_pw------------'
    #################################################################################


}




update_deidweb_pw(){

    local val_deidweb_service=$1 #"CITCWebservice_deidweb"
    local retV
    #local val_deidweb_service=$5
    # get hadoop_keyMsql_nrt container id

    echo '-enter update_deidweb_pw------------'

    #for changing deidweb password##########################################
    echo "-----start change  deidweb password ------------"
    # get deidweb container id
    deidweb=$(docker ps -qf name=$val_deidweb_service)
    val_deidweb_ID=${deidweb:0:12} 

    #str="docker cp ./appsettings.json $val_deidweb_ID:/app/appsettings.json"
    #echo $str
    #retV=$(docker cp ./appsettings.json $val_deidweb_ID:/app/appsettings.json)
    #echo $retV
    sleep 5
    retV=$(docker exec -it $val_deidweb_ID bash -c "python /app/process_appsettings.py")
    echo $retV
    echo '-leave update_deidweb_pw------------'
    #################################################################################


}

checkMariaDBPWD(){
#update_deidadmin_pw1(){
    local PWD1=$1

    local val_worker_service=$2 #"CITCWebservice_worker"

    #local val_old_pwd=$3 #"maria DD's old pwd"
    local retV
    #local val_nodemaster_service=$4 #"CITCHadoop_nodemaster"
    #local val_deidweb_service=$5
    # get hadoop_keyMsql_nrt container id

    echo '-enter checkMariaDBPWD------------'

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
    echo '-----start update hadoop_keyMsql_nrt DB (deidadmin) password------------'
    str='docker exec -it $val_worker_ID1 -c "python /app/app/devp/config/connect_sql.py $PWD1 $PWD1"'
    echo $str
    retV=$(docker exec -it $val_worker_ID1 bash -c "python /app/app/devp/config/connect_sql.py $PWD1 $val_old_pwd" 2>&1)

    if [[ $retV == *"connectToMysql fail"* ]]; then
        echo "!!!! $val_old_pwd error!!!!!"
        echo $retV
        exit 6  
    fi 
    #retV=$(docker exec -it $val_node_ID1 bash -c "mysql -uroot -p$PWD < ")
    ########################################################################
    echo '-leave update_deidadmin_pw------------'


}


checkHDFSPWD(){
#update_deidadmin_pw1(){
    #local PWD1=$1

    local val_worker_service=$1 #"CITCWebservice_worker"

    
    local retV
    #local val_nodemaster_service=$4 #"CITCHadoop_nodemaster"
    #local val_deidweb_service=$5
    # get hadoop_keyMsql_nrt container id

    echo '-enter checkHDFSPWD------------'

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



    retV=$(docker exec -it $val_worker_ID1 bash -c "python /app/app/devp/config/ssh_hdfs.py 1" 2>&1)
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




#######main #############################


echo "enter old hadoop's passwd:"
read -s hadoop_PWD

echo "enter old mariaDB's passwd:"
read -s DB_PWD
echo $PWD
cd ./sourceCode/webService
echo "start CITCWebservice: $PWD"

#echo $PWD

docker stack rm CITCWebservice
docker stack deploy -c docker-compose.yml CITCWebservice 
cd ../../
#echo $PWD
cd ./sourceCode/hadoop
echo "start CITCHadoop: $PWD"
#echo $PWD

docker stack rm CITCHadoop
docker stack deploy --with-registry-auth -c docker-compose.yml CITCHadoop
cd ../../

echo "working Dir: $PWD"



###########################################################################
# Setting hdfs password to CITCWebservice_worker and CITCHadoop_nodemaster#
###########################################################################
#web_service="CITCWebservice_web"
worker_service="CITCWebservice_worker"
nodemaster_service="CITCHadoop_nodemaster"
deidweb_service="CITCWebservice_deidweb"
web_service="CITCWebservice_web"


echo "start recove DB PWD-------------"
parse_result_Maria $worker_service < <(docker secret ls)
parse_result_Maria $nodemaster_service < <(docker secret ls)
parse_result_Maria $deidweb_service < <(docker secret ls)



echo "start recove HDFS PWD-------------"
parse_result_Hdfs $worker_service < <(docker secret ls)
parse_result_Hdfs $web_service < <(docker secret ls)

echo "-----check DB password-----------"
checkMariaDBPWD $DB_PWD $worker_service




echo "-----recover password-----------"
update_deidweb_pw $deidweb_service
update_hadoop_pw $hadoop_PWD $nodemaster_service

echo "-----check HDFS password-----------"
checkHDFSPWD $worker_service

echo "hadoop_PWD is $hadoop_PWD"
echo "DB_PWD is $DB_PWD"

#echo "file_name is $file_name"


