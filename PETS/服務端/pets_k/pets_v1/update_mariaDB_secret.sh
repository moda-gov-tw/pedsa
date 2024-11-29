#!/bin/bash

checkHdfsPaaawordFromWorker(){

    local PWD=$1
    local workerContainerName=$2

    local retV
    #get nodemaster container ID
    worker_id=$(docker ps -qf name=$workerContainerName)
    val_worker1=${worker_id:0:12}
    val1L=${#val_worker1}
    if [ $val1L != 12 ]; then
        echo "get worker container ID error"
        exit -1
    fi
    #str="The worker is $val_worker1"
    #echo $str

    retV=$(docker exec -i $worker_id bash -c "python /app/app/devp/config/loginInfo.py")
    #str="The val1L is $retV"
    #echo $str
    val1L=${#retV}
    str="The val1L is $val1L"
    echo $str
    #val1L=val1L-2
    #retV=${retV:0:$val1L} 

    echo $retV
    #echo $PWD
    docker exec -i $worker_id bash -c "python /app/app/devp/config/loginInfo.py"

    #exit 2
    
    
    if [[ $PWD != *$retV* ]]; then
        echo "hdfs password error"
        exit 2
    fi

}


######20200611##########################
rmService_digestF_Maria(){
    local val_worker_service=$1 #"CITCWebservice_worker"
    local val_nodemaster_service=$2 #"CITCHadoop_nodemaster"
    local val_deidweb_service=$3 #"CITCWebservice_deidweb"

    local val_digestF=$4 #digestF_Maria or 
    local retV

    echo 'enter rmService_digestF_Maria --- '
    sleep 5
    retV=$(docker service update --secret-rm $val_digestF $val_worker_service 2>&1)
    if [[ $retV == *"Error "* ]]; then
        echo "rmService_digestF_Maria $val_worker_service error"
        echo $retV
        exit 1  
    fi         


    retV=$(docker service update --secret-rm $val_digestF $val_nodemaster_service 2>&1)
    if [[ $retV == *"Error "* ]]; then
        echo "rmService_digestF_Maria $val_nodemaster_service err"
        echo $retV
        exit 1
    fi         


    retV=$(docker service update --secret-rm $val_digestF $val_deidweb_service 2>&1)
    if [[ $retV == *"Error "* ]]; then
        echo "rmService_digestF_Maria $val_web_service err"
        echo $retV
        exit 1
    fi  

    sleep 5       

}
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
    #leep 5
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
    sleep 5
    echo 'leave addService_digestF_Maria --- '

}


######digestF containning a token (sha256), point to a random_file (with passwaord)
new_digesfF(){

    local val_random_file_name=$1
    local val_digestF=$2 #digestF_Maria
    local val_worker_service=$3 #"CITCWebservice_worker"
    local val_nodemaster_service=$4 #"CITCHadoop_nodemaster"
    local val_deidweb_service=$5

    local val_worker
    local file_name_hash
    local val_file_name_hash
    local retV

    echo 'enter new_digesfF --- 0. rmService_digestF_Maria  '

    #-----------------
    #######0. rm  service's digestF_Maria
    rmService_digestF_Maria $val_worker_service $val_nodemaster_service $val_deidweb_service $val_digestF
    #---------- 



    #######1. computin the hash of  $val_random_file_name############################################################
    echo 'computin the hash of  $val_random_file_name ---'
    val_worker=$(docker ps -qf name="CITCWebservice_worker")
    str="workercontainer id is  $val_worker"
    echo $str
    #canot print something that we do not want in paswdMariaDB.py (def Sha256(self, toHash):)
    file_name_hash=$(docker exec -i $val_worker bash -c "python /app/app/devp/config/paswdMariaDB.py 1 $val_random_file_name" 2>&1)
    #file_name_hash=$(docker exec -i $val_worker bash -c "python /app/app/devp/config/paswdMariaDB.py 1 $val_random_file_name")
    val1L=${#file_name_hash}
    if [ $val1L == 64 ]; then
        echo "---------in new_digesfF------------(file_name_hash OK)-----------------"
        #exit 1
    fi

    #################################################################################################################
    
    #######2. cleaning file_name_hash####################
    val_file_name_hash=${file_name_hash:0:64} 

    echo "-=====================---------------------"
    echo "+++${val_file_name_hash}+++"
    val_file_name_hashL=${#val_file_name_hash}
    echo ${val_file_name_hashL}
    echo "-----------------------------------------"  
    #####################################################  

    #######2. create a digestF in hose##########################################
    docker secret rm $val_digestF &> /dev/null
    retV=$(echo $val_file_name_hash | docker secret create $val_digestF - 2>&1)
    #echo $retV
    
    if [[ $retV == *"Error "* ]]; then
        echo "new_digesfF $val_file_name_hash to $val_digestF err"
        echo $retV
        exit 3
    fi         

    ########################################################################### 

    echo 'leave new_digesfF --- 3. addService_digestF_Maria  '
    #-----------------
    #######0. add service's digestF_Maria
    test="test123"
    addService_digestF_Maria $val_worker_service $val_nodemaster_service $val_deidweb_service $val_digestF $test
    #----------

}

new_password_random_file(){
    local val_pwd=$1
    local val_digestF=$2 #digestF_Maria
    local val_worker_service=$3 #"CITCWebservice_worker"
    local val_nodemaster_service=$4 #"CITCHadoop_nodemaster"
    local val_deidweb_service=$5
    local val_old_pwd=$6

    local val_random_file_name
    local retV

    echo 'enter new_password_random_file ---'

    #######1. get celery worker container id############################################################
    echo '1. get celery worker container id ---'
    val_worker=$(docker ps -qf name="CITCWebservice_worker")
    str="workercontainer id is  $val_worker"
    echo $str

    
    ##2. get a random file name, to store password
    echo '2. get a random file name, to store password ---'
    # 2>&1 stderr to stdout
    local file_name=$(docker exec -i $val_worker bash -c "python /app/app/devp/config/paswdMariaDB.py 2 $val_pwd $val_old_pwd" 2>&1)
    str="The random_file is $file_name"
    echo $str
    file_name=$(echo $file_name | cut -d" " -f 1)
    val_random_file_name=${file_name:0:8} 
    str="The file name is $val_random_file_name"
    echo $str

    val1L=${#val_random_file_name}
    if [ $val1L != 8 ]; then
        echo "random file name error"
        exit 4
    fi

    ##3. store password to the random_file
    echo '3. get a random file name, to store password ---'
    retV=$(echo $val_pwd | docker secret create $val_random_file_name - 2>&1)

    val1L=${#retV}
    str="docker secret (PWD) create return is $retV"
    echo $str
    #docker id length
    str="The val1L is $val1L"
    echo $str
    if [ $val1L != 25 ]; then
        echo "docker secret create error"
        exit 4
    fi



    #-----------------
    #######4. add service's digestF_Maria
    echo '4. add random_file ($val_random_file_name) to service ($val_worker_service $val_nodemaster_service $val_deidweb_service), using addService_digestF_Maria ---'
    addService_digestF_Maria $val_worker_service $val_nodemaster_service $val_deidweb_service $val_random_file_name $val_pwd
    #----------

    #####5. new a digestF_Maria, and add to services##############################################################
    echo '5. new a digestF_Maria, and add to services ($val_worker_service $val_nodemaster_service $val_deidweb_service)'
    new_digesfF $val_random_file_name $val_digestF $val_worker_service $val_nodemaster_service $val_deidweb_service 
    #################################################################################################################  
    echo 'leave new_password_random_file ---'


}

dummy_random_file(){

    local val_worker_service=$1 #"CITCWebservice_worker"
    local val_nodemaster_service=$2 #"CITCHadoop_nodemaster"
    local val_deidweb_service=$3
    #local val_deidweb_service=$4
    



    local val_old="12e"
    local val_d="123"
    local val_random_file_name
    local retV
    

    echo 'enter dummy_random_file ---'

    #######1. get celery worker container id############################################################
    echo '1. get celery worker container id ---'
    val_worker=$(docker ps -qf name="CITCWebservice_worker")
    str="workercontainer id is  $val_worker"
    echo $str

    
    ##2. get a random file name, to store password
    echo '2. get a random file name, to store password ---'
    # 2>&1 stderr to stdout
    local file_name=$(docker exec -i $val_worker bash -c "python /app/app/devp/config/paswdMariaDB.py 2 $val_d $val_old" 2>&1)
    str="The random_file is $file_name"
    echo $str
    file_name=$(echo $file_name | cut -d" " -f 1)
    val_random_file_name=${file_name:0:8} 
    str="The file name is $val_random_file_name"
    echo $str

    val1L=${#val_random_file_name}
    if [ $val1L != 8 ]; then
        echo "random file name error"
        exit 5
    fi

    ##simulate a pwd
    val_d=$(cat /dev/random | tr -dc "[:alpha:]" | head -c 9)
    str="docker secret (PWD) create return is $val_d"
    echo $str

    ##3. store password to the random_file
    echo '3. get a random file name, to store password ---'
    retV=$(echo $val_d | docker secret create $val_random_file_name - 2>&1)

    val1L=${#retV}
    str="docker secret (PWD) create return is $retV"
    echo $str
    #docker id length
    str="The val1L is $val1L"
    echo $str
    if [ $val1L != 25 ]; then
        echo "docker secret create error"
        exit 5
    fi



    #-----------------
    #######4. add service's digestF_Maria
    #str="22222222222222The file name is $val_random_file_name"
    #echo $str
    #str="4. add random_file ($val_random_file_name) to service ($val_worker_service $val_nodemaster_service $val_deidweb_service), using addService_digestF_Maria ---"
    #echo $str
    val_d="test123"
    addService_digestF_Maria $val_worker_service $val_nodemaster_service $val_deidweb_service $val_random_file_name $val_d
    #addService_digestF_Maria $val_deidweb_service $val_nodemaster_service $val_deidweb_service $val_random_file_name $val_d
    #addService_digestF_Maria $val_worker_service $val_nodemaster_service $val_deidweb_service $val_digestF
    #----------
}


update_deidadmin_pw(){
    local PWD1=$1

    local val_worker_service=$2 #"CITCWebservice_worker"

    local val_old_pwd=$3 #"maria DD's old pwd"
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
    echo '-----start update hadoop_keyMsql_nrt DB (deidadmin) password------------'
    str='docker exec -i $val_worker_ID1 -c "python /app/app/devp/config/connect_sql.py $PWD1 $val_old_pwd"'
    echo $str
    retV=$(docker exec -i $val_worker_ID1 bash -c "python /app/app/devp/config/connect_sql.py $PWD1 $val_old_pwd" 2>&1)

    if [[ $retV == *"connectToMysql fail"* ]]; then
        echo "update_deidadmin_pw $val_old_pwd error"
        echo $retV
        exit 6  
    fi 
    #retV=$(docker exec -i $val_node_ID1 bash -c "mysql -uroot -p$PWD < ")
    ########################################################################
    echo '-leave update_deidadmin_pw------------'


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
    str="docker exec -i $val_nodemaster_ID bash -c echo hadoop:$PWD0 |chpasswd"
    echo $str

    retV=$(docker exec -i $val_nodemaster_ID bash -c "echo hadoop:$PWD0 |chpasswd")
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
    retV=$(docker exec -i $val_deidweb_ID bash -c "python /app/process_appsettings.py")
    echo $retV
    echo '-leave update_deidweb_pw------------'
    #################################################################################


}
#####20200611 (end)#####################
#####20200611 (end)#####################

echo "enter old hadoop's passwd:"
read -s PWD0

echo "enter old mariaDB's passwd:"
read -s val_old_pwd

echo "enter new marria DB's passwd:"
read -s PWD1




###########################################################################
# Setting hdfs password to CITCWebservice_worker and CITCHadoop_nodemaster#
###########################################################################
#web_service="CITCWebservice_web"
worker_service="CITCWebservice_worker"
web_service="CITCWebservice_web"
nodemaster_service="CITCHadoop_nodemaster"
deidweb_service="CITCWebservice_deidweb"
val_digestF="digestF_Maria"


############check old password##########
#checkHdfsPaaaword $PWD0 $worker_service
########################################
fixedFile1="ahcitcww"
rmService_digestF_Maria $worker_service $nodemaster_service $web_service $fixedFile1
    
######new password, and distribute to host, service ($val_worker_service $val_nodemaster_service $val_deidweb_service)#
str='new password, and distribute to host ($val_digestF), service ($worker_service $nodemaster_service $deidweb_service)'
echo $str
new_password_random_file $PWD1 $val_digestF $worker_service $nodemaster_service $deidweb_service $PWD0


#dummy_random_file $worker_service $nodemaster_service $deidweb_service
update_deidadmin_pw $PWD1 $worker_service $val_old_pwd
#update_hadoop_pw $PWD0 $nodemaster_service

update_deidweb_pw $deidweb_service
update_hadoop_pw $PWD0 $nodemaster_service




#echo "passwd is $PWD1"

#echo "file_name is $file_name"


