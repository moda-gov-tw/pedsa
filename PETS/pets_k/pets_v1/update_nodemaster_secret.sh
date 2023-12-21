#!/bin/bash


######20200611##########################
rmService_digestF_Hdfs(){
    
    local val_nodemaster_service=$1 #"CITCHadoop_nodemaster"
    local val_web_service=$2 #"CITCWebservice_web"

    local val_digestF=$3 #digestF_Hdfs 
    local retV

    echo 'enter rmService_digestF_Hdfs --- '


    retV=$(docker service update --secret-rm $val_digestF $val_nodemaster_service 2>&1)
    if [[ $retV == *"Error "* ]]; then
        echo "rmService_digestF_Hdfs $val_nodemaster_service err"
        echo $retV
        exit 1
    fi         

    sleep 5
    retV=$(docker service update --secret-rm $val_digestF $val_web_service 2>&1)
    if [[ $retV == *"Error "* ]]; then
        echo "rmService_digestF_Hdfs $val_web_service err"
        echo $retV
        exit 1
    fi   

    sleep 5 
    echo '--------leave rmService_digestF_Hdfs --- '     

}

### val_digestF = digestF od random_file
addService_digestF_Hdfs(){
    
    local val_worker_service=$1 #"CITCHadoop_nodemaster"
    local val_web_service=$2 #"CITCWebservice_web" is flask

    local val_digestF=$3 #digestF_Hdfs or random_file name
    local val_Hdfs_PWD=$4 #not useing
    local retV

    echo 'enter addService_digestF_Hdfs --- '
    #str="val_digestF is $val_digestF"
    #echo $str      



    retV=$(docker service update --secret-add $val_digestF $val_worker_service 2>&1)
    if [[ $retV == *"Error "* ]]; then
        echo "addService_digestF_Hdfs $val_worker_service err"
        echo $retV
        exit 2
    fi

    sleep 5

    retV=$(docker service update --secret-add $val_digestF $val_web_service 2>&1)
    if [[ $retV == *"Error "* ]]; then
        echo "addService_digestF_Hdfs $val_worker_service error"
        echo $retV
        exit 2       
    fi   


    sleep 5
    
    echo 'leave addService_digestF_Hdfs --- '

}


######digestF containning a token (sha256), point to a random_file (with passwaord)
new_digesfF(){

    local val_random_file_name=$1
    local val_digestF=$2 #digestF_Hdfs
    local val_worker_service=$3 #"CITCHadoop_nodemaster"
    local val_web_service=$4

    local val_worker
    local file_name_hash
    local val_file_name_hash
    local retV

    echo 'enter new_digesfF --- 0. rmService_digestF_Hdfs  '

    #-----------------
    #######0. rm  service's digestF_Hdfs
    rmService_digestF_Hdfs $val_worker_service $val_web_service $val_digestF
    #---------- 



    #######1. computin the hash of  $val_random_file_name############################################################
    echo 'computin the hash of  $val_random_file_name ---'
    val_worker=$(docker ps -qf name="CITCWebservice_worker")
    str="workercontainer id is  $val_worker"
    echo $str
    #canot print something that we do not want in paswdMariaDB.py (def Sha256(self, toHash):)
    file_name_hash=$(docker exec -i $val_worker bash -c "python /app/app/devp/config/paswdMariaDB.py 1 $val_random_file_name" 2>&1)
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

    echo 'leave new_digesfF --- 3. addService_digestF_Hdfs  '
    #-----------------
    #######0. add service's digestF_Hdfs
    test="123"
    addService_digestF_Hdfs $val_worker_service $val_web_service $val_digestF $test
    #----------
    echo 'leave new_digesfF --- 0. rmService_digestF_Hdfs  '

}

new_password_random_file(){
    local val_pwd=$1
    local val_digestF=$2 #digestF_Hdfs    
    #local val_nodemaster_service=$3 #"CITCHadoop_nodemaster"
    local val_worker_service=$3 #"CITCWebservice_worker"

    local val_web_service=$4
    local val_old_pwd=$5

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
    local file_name=$(docker exec -i $val_worker bash -c "python /app/app/devp/config/paswdMariaDB.py 2 $val_pwd $val_old_pwd")
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
    str='4. add random_file ($val_random_file_name) to service ($val_worker_service $val_web_service), using addService_digestF_Hdfs ---'
    echo $str
    addService_digestF_Hdfs  $val_worker_service $val_web_service $val_random_file_name $val_pwd
    #----------

    #####5. new a digestF_HDfs, and add to services##############################################################
    str='5. new a digestF_Hdfs, and add to services ( $val_worker_service $val_web_service)'
    echo $str
    new_digesfF $val_random_file_name $val_digestF $val_worker_service $val_web_service 
    #################################################################################################################  
    echo 'leave new_password_random_file ---'
}


dummy_random_file(){

    local val_worker_service=$1 #"CITCHadoop_nodemaster"
    local val_web_service=$2
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
    addService_digestF_Hdfs $val_worker_service  $val_web_service $val_random_file_name $val_d
    #addService_digestF_Maria $val_deidweb_service $val_nodemaster_service $val_deidweb_service $val_random_file_name $val_d
    #addService_digestF_Maria $val_worker_service $val_nodemaster_service $val_deidweb_service $val_digestF
    #----------
}

update_hadoop_pw(){
    local PWD1=$1

    #local val_worker_service=$2 #"CITCWebservice_worker"
    local val_nodemaster_service=$2 #"CITCHadoop_nodemaster"
    #local val_deidweb_service=$5
    # get hadoop_keyMsql_nrt container id

    echo '-enter update_hadoop_pw------------'

    #for changing hadoop_nodemaster password##########################################
    echo "-----start change  hadoop_nodemaster password ------------"
    echo $val_nodemaster_service
    str="docker ps -qf name=$val_nodemaster_service"
    echo $str

    # get nodemaster container id
    nodemaster=$(docker ps -qf name=$val_nodemaster_service)
    val_nodemaster_ID=${nodemaster:0:12} 
    str="docker exec -i $val_nodemaster_ID bash -c echo hadoop:$PWD1 |chpasswd"

    retV=$(docker exec -i $val_nodemaster_ID bash -c "echo hadoop:$PWD1 |chpasswd")
    echo $retV
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



    retV=$(docker exec -i $val_worker_ID1 bash -c "python /app/app/devp/config/ssh_hdfs.py 2 $PWD1" 2>&1)
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


echo "enter old hadoop's passwd:"
read -s PWD0

echo "enter new hadoop's passwd:"
read -s PWD1

echo "========1======="
#echo "--$PWD0--"
#echo "--$PWD1--"
echo "========2======="

 




###########################################################################
# Setting hdfs password to CITCWebservice_worker and CITCHadoop_nodemaster#
###########################################################################
#web_service="CITCWebservice_web"
worker_service="CITCWebservice_worker"
nodemaster_service="CITCHadoop_nodemaster"
web_service="CITCWebservice_web"
val_digestF="digestF_Hdfs"


############check old password##########
#checkHdfsPaaaword $PWD0 $worker_service
########################################

sleep 5
######nnew password, and distribute to host ($val_digestF), service ($worker_service $web_service#
str='new password, and distribute to host ($val_digestF), service ($worker_service $web_service)'
echo $str
new_password_random_file $PWD1 $val_digestF $worker_service $web_service $PWD0

echo "-----check HDFS password-----------"
checkHDFSPWD $worker_service $PWD0

#update_deidadmin_pw $PWD1 $worker_service $val_old_pwd
echo "-----recover password-----------"
update_hadoop_pw $PWD1 $nodemaster_service
#dummy_random_file $worker_service $web_service






echo "passwd is $PWD1"



