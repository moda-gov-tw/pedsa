#!/bin/bash

#function for erroring handling------, trap 'get_error_line_number $LINENO' ERR
set +e
function get_error_line_number(){

    if [ $? -ne 0 ]
    then 
        echo "in initialSystem.sh 執行失敗"
        echo "error at $1"
    fi
    
}
trap 'get_error_line_number $LINENO' ERR


function get_exit_line_number(){

    echo "exit at $1"
    if [ $? -ne 0 ]
    then 
        echo "in initialSystem.sh 執行exit "
        echo "error at $1"
    fi
    
}
trap 'get_exit_line_number $LINENO' EXIT


#########main##############
#############install PATH參數########################################
WORKINGDIR=/home/ubuntu/PETS
export WORKINGDIR
WORKINGDIR_K_WEB=$WORKINGDIR/pets_k/pets_v1/sourceCode/webService
WORKINGDIR_K_HADOOP=$WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop
export WORKINGDIR_K_WEB
export WORKINGDIR_K_HADOOP
#/home/ubuntu/PETS/pets_syn/citc_syn/sourceCode/webService
WORKINGDIR_SYN_WEB=$WORKINGDIR/pets_syn/pets_syn/sourceCode/webService
export WORKINGDIR_SYN_WEB

#pets_dp/
WORKINGDIR_DP_WEB=$WORKINGDIR/pets_dp/pets_dp/sourceCode/DP_webService
export WORKINGDIR_DP_WEB

#/home/ubuntu/PETS/pets_hadoop/pets_v1
WORKINGDIR_HADOOP_HADOOP=$WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop
export WORKINGDIR_HADOOP_HADOOP
#/home/ubuntu/PETS/pets_service
WORKINGDIR_PETS_SERVICES=$WORKINGDIR/pets_service
export WORKINGDIR_PETS_SERVICES

#/home/ubuntu/PETS/pets_web
WORKINGDIR_PETS_WEB=$WORKINGDIR/pets_web
export WORKINGDIR_PETS_WEB
#####################################################


#######要改的 此文件所在的主機IP##############
CURRENT_IP=34.81.71.21
CURRENT_USER=ubuntu
CURRENT_PASS=petspass@
####################################### test

#########要改的 pets_syn 參數#########
#指向合成 IP and port
#sed -i 's#"DeIdWebAPI": .*#"DeIdWebAPI": {"URL": "http://34.81.71.21:5088"}#g' $WORKINGDIR_SYN_WEB/appsettings.json
#sed -i 's#"Gan_WebAPI": .*#"Gan_WebAPI": {"URL": "http://34.81.71.21:11055"}#g' $WORKINGDIR_SYN_WEB/appsettings.json
######################



#########要改的 pets_k 參數#########
#指向deid IP and port
#sed -i 's#"K_WebAPI": .*#"K_WebAPI": {"URL": "https://34.81.71.21:11000"}#g'  $WORKINGDIR_K_WEB/appsettings.json
######################



#########pets_hadoop (hadoop) 參數#########
PETS_HADOOP_IP=$CURRENT_IP
PETS_HADOOP_PORT=6922
##############################
#########pets_k (hadoop) 參數#########
PETS_K_HDFS_HOSTNAME=$CURRENT_IP
PETS_K_HDFS_PORT=5922
PETS_K_HADOOP_PORT=5997
PETS_K_WEBAPI_PORT=11000
##############################
#########pets_syn 參數#########
PETS_SYN_HOSTNAME=$CURRENT_IP
PETS_SYN_DEIDWEBAPI_PORT=5088
PETS_SYN_WEBAPI_PORT=11055
##############################

#########pets_dp 參數#########
PETS_DP_HDFS_HOSTNAME=$CURRENT_IP
PETS_DP_DEIDWEBAPI_PORT=5090
PETS_DP_WEBAPI_PORT=11065
PETS_DP_API_PORT=8081
##############################

#########Maria DB參數#############
MARIA_IP=$CURRENT_IP
export MARIA_IP
MARIA_PORT=11100
export MARIA_PORT
SSH_PORT=22
export SSH_PORT
#######################
#########FastAPI參數#############
FASTAPI_HOSTNAME=$CURRENT_IP
FASTAPI_PORT=11016
FASTAPI_PORT_INNER=8800
#######################


#########pets_web 參數################
#pets_web 參數
#/home/ubuntu/PETS/pets_web
WEB_OUTER_PORT=80
WEB_INNER_PORT=3000
PERMISSION_SERVICE=$FASTAPI_HOSTNAME
PERMISSION_SERVICE_PORT=$FASTAPI_PORT
SUBSERVICE_K_HOST=$PETS_K_HDFS_HOSTNAME
SUBSERVICE_K_PORT=$PETS_K_WEBAPI_PORT
SUBSERVICE_SYN_HOST=$PETS_SYN_HOSTNAME
SUBSERVICE_SYN_PORT=$PETS_SYN_WEBAPI_PORT
SUBSERVICE_DP_HOST=$PETS_DP_HDFS_HOSTNAME
SUBSERVICE_DP_PORT=$PETS_DP_WEBAPI_PORT
export WEB_OUTER_PORT
export WEB_INNER_PORT
export PERMISSION_SERVICE
export PERMISSION_SERVICE_PORT
export SUBSERVICE_K_HOST
export SUBSERVICE_K_PORT
export SUBSERVICE_GAN_HOST
export SUBSERVICE_GAN_PORT
export SUBSERVICE_DP_HOST
export SUBSERVICE_DP_PORT
############################
####################monitor docker container#################################
#設定 要monitor docker container狀況的主機 IP :\/\/MARIA_IP\'/g################
MONITOR_IP=$CURRENT_IP
#####################################################################


############pets_k###########
sed -i "s/server=.*/server=$MARIA_IP;database=DeIdService;uid=deidadmin;pwd=citcw200;charset=utf8mb4;Port=$MARIA_PORT\"/g" $WORKINGDIR_K_WEB/appsettings.json
sed -i "s/ip = .*/ip = $MARIA_IP/g" $WORKINGDIR_K_WEB/APP__/config/development.ini
sed -i "s/port = .*/port = $MARIA_PORT/g" $WORKINGDIR_K_WEB/APP__/config/development.ini
sed -i "s/ip=.*/ip=$MARIA_IP/g" $WORKINGDIR_K_HADOOP/masterCodeDir/longTaskDir/login_mysql.txt
sed -i "s/port=.*/port=$MARIA_PORT/g" $WORKINGDIR_K_HADOOP/masterCodeDir/longTaskDir/login_mysql.txt
#20231221 add-------------------------------
#/home/ubuntu/PETS/pets_k/pets_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/Hadoop_information.txt*
sed -i "s/ip=.*/ip=$PETS_HADOOP_IP/g" $WORKINGDIR_K_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt
sed -i "s/port=.*/port=$PETS_HADOOP_PORT/g" $WORKINGDIR_K_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt
sed -i "s/web_ip=.*/web_ip=$SUBSERVICE_K_HOST/g" $WORKINGDIR_K_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt
sed -i "s/web_port=.*/web_port=$SUBSERVICE_K_PORT/g" $WORKINGDIR_K_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt
#--------------------------------------------------------------

#20231212 #HDFS_HOSTNAME=$CURRENT_IP HDFS_PORT=5922 
sed -i "s/hdfs_hostname = .*/hdfs_hostname = $PETS_K_HDFS_HOSTNAME/g" $WORKINGDIR_K_WEB/APP__/config/development.ini
sed -i "s/hdfs_port = .*/hdfs_port = $PETS_K_HDFS_PORT/g" $WORKINGDIR_K_WEB/APP__/config/development.ini
#for appsetting.json (1215) PETS_K_HADOOP_PORT=5997
sed -i "s/https:.*:$SUBSERVICE_K_PORT/https:\/\/$SUBSERVICE_K_HOST:$SUBSERVICE_K_PORT/g" $WORKINGDIR_K_WEB/appsettings.json
sed -i "s/https:.*:$PETS_K_HADOOP_PORT/http:\/\/flask5997_compose:5088/g" $WORKINGDIR_K_WEB/appsettings.json
sed -i "s/https:.*:5088/http:\/\/flask5997_compose:5088/g" $WORKINGDIR_K_WEB/appsettings.json

############pets_syn###########
sed -i "s/server=.*/server=$MARIA_IP;database=SynService;uid=deidadmin;pwd=citcw200;charset=utf8mb4;Port=$MARIA_PORT\"/g" $WORKINGDIR_SYN_WEB/appsettings.json
sed -i "s/ip = .*/ip = $MARIA_IP/g" $WORKINGDIR_SYN_WEB/APP__/config/development.ini
sed -i "s/port = .*/port = $MARIA_PORT/g" $WORKINGDIR_SYN_WEB/APP__/config/development.ini
#20231212 #HDFS_HOSTNAME=$CURRENT_IP HDFS_PORT=5922 (not use)
sed -i "s/hdfs_hostname = .*/hdfs_hostname = $PETS_K_HDFS_HOSTNAME/g" $WORKINGDIR_SYN_WEB/APP__/config/development.ini
sed -i "s/hdfs_port = .*/hdfs_port = $PETS_K_HDFS_PORT/g" $WORKINGDIR_SYN_WEB/APP__/config/development.ini
#20231212
#for joint，用在scp, port=6922
#/home/ubuntu/PETS/pets_syn/pets_syn/sourceCode/webService/APP__/config/Hadoop_information.txt 
sed -i "s/ip=.*/ip=$PETS_HADOOP_IP/g" $WORKINGDIR_SYN_WEB/APP__/config/Hadoop_information.txt
sed -i "s/hdfs_port =.*/hdfs_port = $PETS_HADOOP_PORT/g" $WORKINGDIR_SYN_WEB/APP__/config/Hadoop_information.txt
#for appsetting.json
sed -i "s/http:.*:$PETS_SYN_DEIDWEBAPI_PORT/http:\/\/flask_syn_compose:$PETS_SYN_DEIDWEBAPI_PORT/g" $WORKINGDIR_SYN_WEB/appsettings.json
sed -i "s/http:.*:$SUBSERVICE_SYN_PORT/https:\/\/$SUBSERVICE_SYN_HOST:$SUBSERVICE_SYN_PORT/g" $WORKINGDIR_SYN_WEB/appsettings.json
sed -i "s/https:.*:$SUBSERVICE_SYN_PORT/https:\/\/$SUBSERVICE_SYN_HOST:$SUBSERVICE_SYN_PORT/g" $WORKINGDIR_SYN_WEB/appsettings.json
#SUBSERVICE_SYN_HOST=$CURRENT_IP
#SUBSERVICE_SYN_PORT=11055


############pets_dp###########
sed -i "s/server=.*/server=$MARIA_IP;database=DpService;uid=deidadmin;pwd=citcw200;charset=utf8mb4;Port=$MARIA_PORT\"/g" $WORKINGDIR_DP_WEB/appsettings.json
sed -i "s/ip = .*/ip = $MARIA_IP/g" $WORKINGDIR_DP_WEB/APP__/config/development.ini
sed -i "s/port = .*/port = $MARIA_PORT/g" $WORKINGDIR_DP_WEB/APP__/config/development.ini
#20231212 #HDFS_HOSTNAME=$CURRENT_IP HDFS_PORT=5922 (not use)
sed -i "s/hdfs_hostname = .*/hdfs_hostname = $PETS_K_HDFS_HOSTNAME/g" $WORKINGDIR_DP_WEB/APP__/config/development.ini
sed -i "s/hdfs_port = .*/hdfs_port = $PETS_K_HDFS_PORT/g" $WORKINGDIR_DP_WEB/APP__/config/development.ini
#20231212
#for joint，用在scp, port=6922
#/home/ubuntu/PETS/pets_syn/pets_syn/sourceCode/webService/APP__/config/Hadoop_information.txt 
sed -i "s/ip=.*/ip=$PETS_HADOOP_IP/g" $WORKINGDIR_DP_WEB/APP__/config/Hadoop_information.txt
sed -i "s/hdfs_port =.*/hdfs_port = $PETS_HADOOP_PORT/g" $WORKINGDIR_DP_WEB/APP__/config/Hadoop_information.txt
#appsettings.json###########
sed -i "s/http:.*:$PETS_DP_DEIDWEBAPI_PORT/http:\/\/flaskdp_compose:5088/g" $WORKINGDIR_DP_WEB/appsettings.json
sed -i "s/http:.*:$PETS_DP_WEBAPI_PORT/https:\/\/$PETS_DP_HDFS_HOSTNAME:$PETS_DP_WEBAPI_PORT/g" $WORKINGDIR_DP_WEB/appsettings.json
sed -i "s/http:.*:$PETS_DP_API_PORT/https:\/\/$PETS_DP_HDFS_HOSTNAME:$PETS_DP_API_PORT/g" $WORKINGDIR_DP_WEB/appsettings.json
sed -i "s/https:.*:$PETS_DP_WEBAPI_PORT/https:\/\/$PETS_DP_HDFS_HOSTNAME:$PETS_DP_WEBAPI_PORT/g" $WORKINGDIR_DP_WEB/appsettings.json
sed -i "s/https:.*:$PETS_DP_API_PORT/https:\/\/$PETS_DP_HDFS_HOSTNAME:$PETS_DP_API_PORT/g" $WORKINGDIR_DP_WEB/appsettings.json
#PETS_DP_API_PORT=8081




############pets_hadoop for join###########
sed -i "s/ip=.*/ip=$MARIA_IP/g" $WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/login_mysql.txt
sed -i "s/port=.*/port=$MARIA_PORT/g" $WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/login_mysql.txt




############pets_service###########
#WORKINGDIR_PETS_SERVICES=$WORKINGDIR/pets_service
#/home/ubuntu/PETS/pets_service/petsservice/config/development.ini 呼叫 pets_hadoop join 程式 (tony新增), 所以port=6922
sed -i "s/ip = .*/ip = $MARIA_IP/g" $WORKINGDIR_PETS_SERVICES/petsservice/config/development.ini
sed -i "s/port = .*/port = $MARIA_PORT/g" $WORKINGDIR_PETS_SERVICES/petsservice/config/development.ini
sed -i "s/hdfs_hostname = .*/hdfs_hostname = $PETS_HADOOP_IP/g" $WORKINGDIR_PETS_SERVICES/petsservice/config/development.ini
sed -i "s/hdfs_port = .*/hdfs_port = $PETS_HADOOP_PORT/g" $WORKINGDIR_PETS_SERVICES/petsservice/config/development.ini
#20231212
#for joint，用在scp, port=6922
#/home/ubuntu/PETS/pets_service/petsservice/config/Hadoop_information.txt
sed -i "s/ip=.*/ip=$PETS_HADOOP_IP/g" $WORKINGDIR_PETS_SERVICES/petsservice/config/Hadoop_information.txt
sed -i "s/port=.*/port=$PETS_HADOOP_PORT/g" $WORKINGDIR_PETS_SERVICES/petsservice/config/Hadoop_information.txt
sed -i "s/k_port=.*/k_port=$PETS_K_HDFS_PORT/g" $WORKINGDIR_PETS_SERVICES/petsservice/config/Hadoop_information.txt
sed -i "s/web_ip=.*/web_ip=$SUBSERVICE_K_HOST/g" $WORKINGDIR_PETS_SERVICES/petsservice/config/Hadoop_information.txt
sed -i "s/web_port=.*/web_port=$SUBSERVICE_K_PORT/g" $WORKINGDIR_PETS_SERVICES/petsservice/config/Hadoop_information.txt
sed -i "s/gan_ip=.*/gan_ip=$SUBSERVICE_SYN_HOST/g" $WORKINGDIR_PETS_SERVICES/petsservice/config/Hadoop_information.txt
sed -i "s/gan_port=.*/gan_port=$SUBSERVICE_SYN_PORT/g" $WORKINGDIR_PETS_SERVICES/petsservice/config/Hadoop_information.txt
sed -i "s/join_ip=.*/join_ip=$PETS_HADOOP_IP/g" $WORKINGDIR_PETS_SERVICES/petsservice/config/Hadoop_information.txt
sed -i "s/join_port=.*/join_port=$PETS_HADOOP_PORT/g" $WORKINGDIR_PETS_SERVICES/petsservice/config/Hadoop_information.txt
sed -i "s/host_ip=.*/host_ip=$CURRENT_IP/g" $WORKINGDIR_PETS_SERVICES/petsservice/config/Hadoop_information.txt
#pets service 環境變數
sed -i "s/DB_SERVER=.*/DB_SERVER=$MARIA_IP/g" $WORKINGDIR_PETS_SERVICES/petsservice/.env
sed -i "s/DB_PORT=.*/DB_PORT=$MARIA_PORT/g" $WORKINGDIR_PETS_SERVICES/petsservice/.env
#設定 要monitor docker container狀況的主機 IP :\/\/MARIA_IP\'/g
#MONITOR_IP=34.81.71.21，改程式
sed -i "s/tcp:.*/tcp:\/\/$MONITOR_IP:2376\', tls=tls_config)/g" $WORKINGDIR_PETS_SERVICES/petsservice/config/getContainersStatus.py

#20231214 for delete ip/prot
sed -i "s/ip=.*/ip=$CURRENT_IP/g" $WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt
sed -i "s/port = .*/port = $SSH_PORT/g" $WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt
sed -i "s/user=.*/user=$CURRENT_USER/g" $WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt
sed -i "s/passwd=.*/passwd=$CURRENT_PASS/g" $WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt
sed -i "s/k_web_ip = .*/k_web_ip = $SUBSERVICE_K_HOST/g" $WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt
sed -i "s/k_web_port = .*/k_web_port = $SUBSERVICE_K_PORT/g" $WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt
sed -i "s/syn_web_ip = .*/syn_web_ip = $SUBSERVICE_SYN_HOST/g" $WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt
sed -i "s/syn_web_port = .*/syn_web_port = $SUBSERVICE_SYN_PORT/g" $WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt
#####for delete path
sed -i "s/pets_hadoop_in = .*/pets_hadoop_in = \'\/home\/$CURRENT_USER\/PETS\/pets_hadoop\/pets_v1\/sourceCode\/hadoop\/data\/input\/\'/g" $WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt
sed -i "s/pets_hadoop_out = .*/pets_hadoop_out = \'\/home\/$CURRENT_USER\/PETS\/pets_hadoop\/pets_v1\/sourceCode\/hadoop\/data\/output\/\'/g" $WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt
sed -i "s/pets_final_k_in = .*/pets_final_k_in = \'\/home\/$CURRENT_USER\/PETS\/pets_hadoop\/pets_v1\/sourceCode\/hadoop\/final_project\/k\/input\/\'/g" $WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt
sed -i "s/pets_final_k_out = .*/pets_final_k_out = \'\/home\/$CURRENT_USER\/PETS\/pets_hadoop\/pets_v1\/sourceCode\/hadoop\/final_project\/k\/output\/\'/g" $WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt
sed -i "s/pets_final_syn_in = .*/pets_final_syn_in = \'\/home\/$CURRENT_USER\/PETS\/pets_hadoop\/pets_v1\/sourceCode\/hadoop\/final_project\/syn\/input\/\'/g" $WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt
sed -i "s/pets_final_syn_out = .*/pets_final_syn_out = \'\/home\/$CURRENT_USER\/PETS\/pets_hadoop\/pets_v1\/sourceCode\/hadoop\/final_project\/syn\/output\/\'/g" $WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt
sed -i "s/pets_download_enc = .*/pets_download_enc = \'\/home\/$CURRENT_USER\/PETS\/pets_web\/download_folder\/enc\/k\/\'/g" $WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt
sed -i "s/pets_upload =.*/pets_upload =\'\/home\/$CURRENT_USER\/PETS\/pets_service\/sftp_upload_folder\/\'/g" $WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt
sed -i "s/user_upload_folder = .*/user_upload_folder = \'\/home\/$CURRENT_USER\/PETS\/pets_syn\/pets_syn\/sourceCode\/webService\/APP__\/user_upload_folder\/'/g" $WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt
sed -i "s/folderForSynthetic = .*/folderForSynthetic = \'\/home\/$CURRENT_USER\/PETS\/pets_syn\/pets_syn\/sourceCode\/webService\/APP__\/folderForSynthetic\/'/g" $WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt



###########pets_web###########
sed -i "s/DOCKER_WEB_OUTER_PORT=.*/DOCKER_WEB_OUTER_PORT=\'$WEB_OUTER_PORT\'/g" $WORKINGDIR_PETS_WEB/pets_web/.env
sed -i "s/DOCKER_WEB_INNER_PORT=.*/DOCKER_WEB_INNER_PORT=\'$WEB_INNER_PORT\'/g" $WORKINGDIR_PETS_WEB/pets_web/.env

sed -i "s/PERMISSION_SERVICE=.*/PERMISSION_SERVICE=\'http:\/\/fastapi_service_compose\'/g" $WORKINGDIR_PETS_WEB/pets_web/.env
sed -i "s/PERMISSION_SERVICE_PORT=.*/PERMISSION_SERVICE_PORT=\'$FASTAPI_PORT_INNER\'/g" $WORKINGDIR_PETS_WEB/pets_web/.env

sed -i "s/SUBSERVICE_K_HOST=.*/SUBSERVICE_K_HOST=\'https:\/\/$SUBSERVICE_K_HOST\'/g" $WORKINGDIR_PETS_WEB/pets_web/.env
sed -i "s/SUBSERVICE_K_PORT=.*/SUBSERVICE_K_PORT=\'$SUBSERVICE_K_PORT\'/g" $WORKINGDIR_PETS_WEB/pets_web/.env

sed -i "s/SUBSERVICE_SYN_HOST=.*/SUBSERVICE_SYN_HOST=\'https:\/\/$SUBSERVICE_SYN_HOST\'/g" $WORKINGDIR_PETS_WEB/pets_web/.env
sed -i "s/SUBSERVICE_SYN_PORT=.*/SUBSERVICE_SYN_PORT=\'$SUBSERVICE_SYN_PORT\'/g" $WORKINGDIR_PETS_WEB/pets_web/.env

sed -i "s/SUBSERVICE_DP_HOST=.*/SUBSERVICE_DP_HOST=\'https:\/\/$SUBSERVICE_DP_HOST\'/g" $WORKINGDIR_PETS_WEB/pets_web/.env
sed -i "s/SUBSERVICE_DP_PORT=.*/SUBSERVICE_DP_PORT=\'$SUBSERVICE_DP_PORT\'/g" $WORKINGDIR_PETS_WEB/pets_web/.env


## mount --bind <source_data_owner> <target_mnt_point>
# mount --bind "/home/$CURRENT_USER/PETS/pets_hadoop/pets_v1/sourceCode/hadoop/final_project/k/input" "/home/$CURRENT_USER/PETS/pets_web/download_folder/enc/k"
# mount --bind "/home/$CURRENT_USER/PETS/pets_hadoop/pets_v1/sourceCode/hadoop/final_project/k/output" "/home/$CURRENT_USER/PETS/pets_web/download_folder/dec/k"
# mount --bind "/home/$CURRENT_USER/PETS/pets_hadoop/pets_v1/sourceCode/hadoop/final_project/syn/output" "/home/$CURRENT_USER/PETS/pets_web/download_folder/enc/syn"
# mount --bind "/home/$CURRENT_USER/PETS/pets_hadoop/pets_v1/sourceCode/hadoop/final_project/dp/output" "/home/$CURRENT_USER/PETS/pets_web/download_folder/enc/dp"








#/home/ubuntu/PETS/pets_k
if [ -d "$WORKINGDIR/pets_k/" ]; then
    #檔案 /path/to/dir/filename存在
    echo "$WORKINGDIR/pets_k/ exists................"
    cd $WORKINGDIR/pets_k/pets_v1
    echo "current path is $PWD...."
    echo "run ./initialSystem.sh...."
    
    source ./initialSystem.sh 

    #sleep 5
    #chown -R 999:999 /var/lib/mysql
    cd $WORKINGDIR/
else
    #檔案 /path/to/dir/filename 不存在
    echo "/home/ubuntu/PETS/pets_k/ does not exists."
    # exit bash script, but not quiting the terminal
    cd $WORKINGDIR/
    return
fi

echo "finish deid_k service  in $PWD/pets_k/pets_v1...."

#/home/ubuntu/PETS/pets_hadoop
if [ -d "$WORKINGDIR/pets_hadoop/" ]; then
    #檔案 /path/to/dir/filename存在
    echo "$WORKINGDIR/pets_hadoop/ exists................"
    cd $WORKINGDIR/pets_hadoop/pets_v1
    echo "current path is $PWD...."
    echo "run ./initialSystem.sh...."
    
    source ./initialSystem.sh 

    #sleep 5
    #chown -R 999:999 /var/lib/mysql
    cd $WORKINGDIR/
else
    #檔案 /path/to/dir/filename 不存在
    echo "/home/ubuntu/PETS/pets_hadoop/ does not exists."
    # exit bash script, but not quiting the terminal
    cd $WORKINGDIR/
    return
fi

echo "finish deid_k service  in $PWD/pets_hadoop/pets_v1...."
sleep 5



##pets_dp/ 20231221 add
#WORKINGDIR_DP_WEB=$WORKINGDIR/pets_dp/pets_dp/sourceCode/DP_webService
#export WORKINGDIR_DP_WEB
if [ -d "$WORKINGDIR/pets_dp/" ]; then
    #檔案 /path/to/dir/filename存在
    echo "$WORKINGDIR/pets_syn/ exists................"
    cd $WORKINGDIR/pets_dp/pets_dp/sourceCode/DP_webService
    echo "current path is $PWD...."
    echo "run docker-compose down...."
    
    docker-compose down
    sleep 5
    echo "run docker-compose up -d...."
    docker-compose up -d


    #sleep 5
    #chown -R 999:999 /var/lib/mysql
    cd $WORKINGDIR/
else
    #檔案 /path/to/dir/filename 不存在
    echo "/home/ubuntu/PETS/pets_syn/ does not exists."
    # exit bash script, but not quiting the terminal
    cd $WORKINGDIR/
    return
fi


echo "finish deid_k service  in $PWD/pets_syn/pets_syn...."

sleep 5

#/home/ubuntu/PETS/pets_service
if [ -d "$WORKINGDIR/pets_service/" ]; then
    #檔案 /path/to/dir/filename存在
    echo "$WORKINGDIR/pets_service/ exists................"
    cd $WORKINGDIR/pets_service/petsservice
    echo "current path is $PWD...."
    echo "run docker-compose down...."
    
    docker-compose down
    sleep 5
    echo "run docker-compose up -d...."
    docker-compose up -d


    #sleep 5
    #chown -R 999:999 /var/lib/mysql
    cd $WORKINGDIR/
else
    #檔案 /path/to/dir/filename 不存在
    echo "/home/ubuntu/PETS/pets_service/ does not exists."
    # exit bash script, but not quiting the terminal
    cd $WORKINGDIR/
    return
fi

echo "finish deid_k service  in $PWD/pets_service/petsservice...."

sleep 5
#WORKINGDIR_PETS_WEB=$WORKINGDIR/pets_web
#/home/ubuntu/PETS/pets_web
if [ -d "$WORKINGDIR/pets_web/" ]; then
    #檔案 /path/to/dir/filename存在
    echo "$WORKINGDIR/pets_web/ exists................"
    cd $WORKINGDIR/pets_web/pets_web
    echo "current path is $PWD...."
    echo "run docker-compose down...."
    
    docker-compose down
    sleep 5
    echo "run docker-compose up -d...."
    docker-compose up -d


    #sleep 5
    #chown -R 999:999 /var/lib/mysql
    cd $WORKINGDIR/
else
    #檔案 /path/to/dir/filename 不存在
    echo "/home/ubuntu/PETS/pets_web/ does not exists."
    # exit bash script, but not quiting the terminal
    cd $WORKINGDIR/
    return
fi


#/home/ubuntu/PETS/pets_syn
if [ -d "$WORKINGDIR/pets_syn/" ]; then
    #檔案 /path/to/dir/filename存在
    echo "$WORKINGDIR/pets_syn/ exists................"
    cd $WORKINGDIR/pets_syn/pets_syn/sourceCode/webService
    echo "current path is $PWD...."
    echo "run docker-compose down...."
    
    docker-compose down
    sleep 5
    echo "run docker-compose up -d...."
    docker-compose up -d


    #sleep 5
    #chown -R 999:999 /var/lib/mysql
    cd $WORKINGDIR/
else
    #檔案 /path/to/dir/filename 不存在
    echo "/home/ubuntu/PETS/pets_syn/ does not exists."
    # exit bash script, but not quiting the terminal
    cd $WORKINGDIR/
    return
fi



echo "finish deid_k service  in $PWD/pets_web/pets_web...."
