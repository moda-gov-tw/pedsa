#!/bin/bash

######20200611##########################

rmService_digestF_Maria(){
    local val_worker_service=$1 #"CITCWebservice_worker"
    local val_nodemaster_service=$2 #"CITCHadoop_nodemaster"
    local val_deidweb_service=$3 #"CITCWebservice_deidweb"

    local val_digestF=$4 #digestF_Maria or 
    local retV

    echo 'enter rmService_digestF_Maria --- '

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

    if [[ $val_digestF != *"ahcitcww"* ]]; then
        retV=$(docker service update --secret-add $val_digestF $val_worker_service 2>&1)
        if [[ $retV == *"Error "* ]]; then
            echo "addService_digestF_Hdfs $val_worker_service err"
            echo $retV
            exit 2
        fi
        retV=$(docker service update --secret-add $val_digestF $val_web_service 2>&1)
        if [[ $retV == *"Error "* ]]; then
            echo "addService_digestF_Hdfs $val_worker_service error"
            echo $retV
            exit 2       
        fi
    fi   



    echo 'leave addService_digestF_Hdfs --- '

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


#####20200611 (end)#####################

##########202006112######################################
recover_MariaDB(){
    local DB_PWD=$1

    local val_worker_service=$2 #"CITCWebservice_worker"

    #echo '-enter recover_MariaDB------------'

    worer1=$(docker ps -qf name=$val_worker_service)
    val_worker_ID1=${worer1:0:12}
    val1L=${#val_worker_ID1}
    if [ $val1L != 12 ]; then
        echo "get webservice_worker service id error"
        exit -1
    fi
    #str="webservice_worker container ID is $val_worker_ID1"
    #echo $str

    #for webservice_worker service#########################################

    digestF123="digestF_Maria"
    #echo '-----start host password------------'
    #str='docker exec -it $val_worker_ID1 -c "python /app/app/devp/config/getInUSeRandomFiles.py $digestF123 $DB_PWD"'
    #echo $str
    retV=$(docker exec -it $val_worker_ID1 bash -c "python /app/app/devp/config/getInUSeRandomFiles.py $digestF123 $DB_PWD" 2>&1)
    val1L=${#retV}
    
    #echo $val1L
    if [ $val1L != 9 ]; then
        echo $retV
        exit 5
    fi

    #echo $retV
    randomFile=${retV:0:8}
    echo $randomFile


}



recover_Hdfs(){
    local Hdfs_PWD=$1

    local val_worker_service=$2 #"CITCWebservice_worker"
    
    #echo '-enter recover_Hdfs------------'
    #echo $val_worker_service
    worer1=$(docker ps -qf name=$val_worker_service)
    val_worker_ID1=${worer1:0:12}
    val1L=${#val_worker_ID1}
    if [ $val1L != 12 ]; then
        echo "get webservice_worker service id error"
        exit -1
    fi
    #str="webservice_worker container ID is $val_worker_ID1"
    #echo $str

    #for webservice_worker service#########################################

    digestF123="digestF_Hdfs"
    #echo '-----start host password------------'
    #str='docker exec -it $val_worker_ID1 -c "python /app/app/devp/config/getInUSeRandomFiles.py $digestF123 $Hdfs_PWD"'
    #echo $str
    retV=$(docker exec -it $val_worker_ID1 bash -c "python /app/app/devp/config/getInUSeRandomFiles.py $digestF123 $Hdfs_PWD" 2>&1)
    val1L=${#retV}
    #echo $val1L
    if [ $val1L != 9 ]; then
        echo "err"
        echo $retV
        exit 5
    fi

    #echo $retV
    randomFile=${retV:0:8}
    echo $randomFile
   

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

parse_result(){

    local notDel_file1=$1
    local notDel_file2=$2

    while read line; do    

      sec_time=$(echo $line | cut -d" " -f 4)
      echo "${sec_time}"
     
       sec_name=$(echo $line | cut -d" " -f 2)
       echo "${sec_name}"
       val1L=${#sec_name}
       echo "${val1L}"
                                           
       if [ $val1L == 8 ] && [[ $sec_name != $notDel_file2 ]] && [[ $sec_name != $notDel_file1 ]] && [[ $sec_name != *"ahcitcww"* ]]; then
          docker secret rm $sec_name
          echo "-----${sec_name}----"

        

       fi

    done
}






worker_service="CITCWebservice_worker"
nodemaster_service="CITCHadoop_nodemaster"
deidweb_service="CITCWebservice_deidweb"
web_service="CITCWebservice_web"
DB_PWD="citcw004"
hadoop_PWD="w004citc"




retV=$(recover_MariaDB $DB_PWD $worker_service)
val1L=${#retV}
    
echo $val1L
if [ $val1L != 8 ]; then
    echo $retV
    exit 5
fi

random_fileMaria=$retV

echo $random_fileMaria


echo "hadoop_PWD is $hadoop_PWD"

echo "val_worker_service is $val_worker_service"

#recover_Hdfs $hadoop_PWD $worker_service 
retV=$(recover_Hdfs $hadoop_PWD $worker_service )
val1L=${#retV}
    
echo $val1L
if [ $val1L != 8 ]; then
    echo $retV
    exit 5
fi
random_fileHdfs=$retV
echo $random_fileHdfs

docker stack rm CITCWebservice
docker stack rm CITCHadoop



parse_result $random_fileHdfs $random_fileMaria < <(docker secret ls)

bash recoverSystemPwd.sh




#update_hadoop_pw $hadoop_PWD

