#!/bin/bash



### val_digestF = digestF od random_file
addService_digestF_Maria(){
    local val_worker_service=$1 #"CITCWebservice_worker"
    local val_nodemaster_service=$2 #"CITCHadoop_nodemaster"
    local val_deidweb_service=$3 #"CITCWebservice_deidweb"

    local val_digestF=$4 #digestF_Maria or random_file name
    local val_DB_PWD=$5
    local retV

    echo 'enter addService_digestF_Maria --- '
    #str="val_digestF is $val_digestF"
    #echo $str

    retV=$(docker service update --secret-add $val_digestF $val_worker_service 2>&1)
    if [[ $retV == *"Error "* ]]; then
        echo "addService_digestF_Maria $val_worker_service error"
        echo $retV
        exit 2       
    fi         



    retV=$(docker service update --secret-add $val_digestF $val_nodemaster_service 2>&1)
    if [[ $retV == *"Error "* ]]; then
        echo "addService_digestF_Maria $val_nodemaster_service err"
        echo $retV
        exit 2
    fi

    val1L=${#val_digestF}
    str="----------------#####$val_digestF len is $val1L####--------------"
    echo $str
    if [ $val1L != 8 ]; then
        retV=$(docker service update --secret-add $val_digestF $val_deidweb_service 2>&1)
        if [[ $retV == *"Error "* ]]; then
            echo "addService_digestF_Maria $val_web_service err"
            echo $retV
            exit 2
        fi  
    fi
               
    if [ $val1L == 8 ] && [[ $val_DB_PWD != *"test123"* ]]; then

        fixedFile="ahcitcww"
        docker service update --secret-rm $fixedFile $val_deidweb_service #&> /dev/null
        docker secret rm $fixedFile #&> /dev/null
        retV=$(echo $val_DB_PWD | docker secret create $fixedFile - 2>&1)
        
        str="fixedFile is $fixedFile"
        echo $str
        str="--------------------------------------val_DB_PWD is $val_DB_PWD-------------"
        echo $str
        str="docker service update --secret-add $fixedFile $val_deidweb_service"
        echo $str
        retV=$(docker service update --secret-add $fixedFile $val_deidweb_service 2>&1)
        #echo $retV
        if [[ $retV == *"Error "* ]]; then
            echo "addService_digestF_Maria $val_web_service err"
            echo $retV
            exit 2
        fi 
    fi    
    #docker service update --secret-add $fixedFile $val_deidweb_service
    echo 'leave addService_digestF_Maria --- '

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


    docker service update $val_nodemaster_service --publish-add 9180:8088  &> /dev/null
    docker service update $val_nodemaster_service --publish-add 9970:50070 &> /dev/null


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


checkHDFSPWD(){
#update_deidadmin_pw1(){

    local val_worker_service=$1 #"CITCWebservice_worker"
    local PWD1=$2

    
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

    retV=$(docker exec -it $val_worker_ID1 bash -c "python /app/app/devp/config/ssh_hdfs.py 2 $PWD1" 2>&1)
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


#####20200611 (end)#####################
#####20200611 (end)#####################

echo "enter old hadoop's passwd:"
read -s PWD0


###########################################################################
# Setting hdfs password to CITCWebservice_worker and CITCHadoop_nodemaster#
###########################################################################
#web_service="CITCWebservice_web"
worker_service="CITCWebservice_worker"

nodemaster_service="CITCHadoop_nodemaster"

#update_hadoop_pw "w001citc" $nodemaster_service
#echo "-----check HDFS password-----------"
checkHDFSPWD $worker_service $PWD0

update_hadoop_pw $PWD0 $nodemaster_service

echo "passwd is $PWD0"

#echo "file_name is $file_name"


