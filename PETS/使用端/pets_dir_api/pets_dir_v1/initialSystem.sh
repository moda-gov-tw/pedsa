#!/bin/bash

#######main #############################


#echo "enter old hadoop's passwd:"
#read -s hadoop_PWD

#echo "enter old mariaDB's passwd:"
#read -s DB_PWD
#echo $PWD


#20240319, icl 
#20220301, citc add
#docker stack rm PETSHadoopDir
#docker stack rm PETSWebserviceDir

# Read 安裝目錄
#/home/itri/AITMP/pets_dir_v1
#deploy_dir=/home/itri/AITMP/111111
echo "當客戶端安裝在 /home/itri-pedsa/pets_dir_v1則選/home/itri-pedsa"
echo -n 輸入PEDSA 使用端 安裝目錄 "(例如/home/itri-pedsa):"
read  deploy_dir1
deploy_dir_client=$deploy_dir1
echo "目前目錄 為 "$PWD
echo "使用端 安裝目錄(deploy_dir_client) 為 $deploy_dir_client"
sleep 1

echo -n 輸入PEDSA 服務端 安裝目錄 "(例如/home/itri-pedsa):"
read  deploy_dir2
deploy_dir_server=$deploy_dir2
echo "目前目錄 為 "$PWD
echo "服務端 安裝目錄(deploy_dir_server) 為 $deploy_dir_server"
sleep 1
#

# Read PEDSAS_USER
echo -n  輸入PEDSA服務端提供的使用者名稱  "(例如 itri-pedsa):"
read  PEDSAS_USER_
PEDSAS_USER=$PEDSAS_USER_

echo "PEDSA服務端提供的使用者名稱 為 $PEDSAS_USER"
sleep 3

##PEDSAS_USER=ailabuser

SFTP_FOLDER=$deploy_dir_server/pedsa_s/pets_service/sftp_upload_folder

echo "PEDSA服務端上傳目錄 為 $SFTP_FOLDER"
sleep 3

# Read 服務端外部IP
echo -n 服務端主機外部IP"(例如130.211.246.188):"
read  GCP_IP1
#GCP_IP=$GCP_IP1
echo "服務端主機IP 為 $GCP_IP1"
sleep 3



#PETS_K_HDFS_HOSTNAME=130.211.246.188
PETS_K_HDFS_HOSTNAME=$GCP_IP1
WORKINGDIR_HADOOP_HADOOP="$deploy_dir_client/pets_dir_v1/sourceCode/hadoop"
WORKINGDIR_HADOOP_WEB=$deploy_dir_client/pets_dir_v1/sourceCode/webService

#echo "-----$WORKINGDIR_HADOOP_HADOOP"
#echo "$WORKINGDIR_HADOOP_WEB1"

#MARIA_PORT=3306



echo "---docker secret create - maria"
val_maria=$(docker secret inspect --format='{{.Spec.Name}}' maria_file)
val_random_file_name="maria_file"
if [[ "$val_random_file_name" == "$val_maria" ]]; then
        echo "---maria secret existed"
else
        val_d="citcw200"
    retV=$(echo $val_d | docker secret create $val_random_file_name -)
    echo $retV
fi


echo "---docker secret create - hadoop"
val_hadoop=$(docker secret inspect --format='{{.Spec.Name}}' hadoop_file)
val_random_file_name="hadoop_file"
if [[ "$val_random_file_name" == "$val_hadoop" ]]; then
        echo "---hadoop secret existed"
else
    val_d="citcw200@"
    retV=$(echo $val_d | docker secret create $val_random_file_name -)
    echo $retV
fi


echo "---docker secret create - deidwebservice"
val_ahcitcww=$(docker secret inspect --format='{{.Spec.Name}}' ahcitcww)
val_random_file_name="ahcitcww"
if [[ "$val_random_file_name" == "$val_ahcitcww" ]]; then
        echo "---deidwebservice secret existed"
else
        val_d="citcw200"
    retV=$(echo $val_d | docker secret create $val_random_file_name -)
    echo $retV
fi



#echo $PWD


PETS_K_HDFS_PORT=7922

echo "hadoop 工作設定目錄 $WORKINGDIR_HADOOP_HADOOP"
echo "webservice 工作設定目錄 $WORKINGDIR_HADOOP_WEB"



##bash insert backslash for every slash in string
#string='/tmp/something'
#escapedstring="${string//\//\\\/}"
#printf '%s\n' "$escapedstring"     
#\/tmp\/something
SFTP_FOLDER_="${SFTP_FOLDER//\//\\\/}"

echo "sftp到服務端的目錄 $SFTP_FOLDER_"


sed -i "s/ip=.*/ip=$PETS_K_HDFS_HOSTNAME/g" "$WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/login_mysql.txt"
sed -i "s/port=.*/port=11100/g" "$WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/login_mysql.txt"

echo "----------$WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/login_mysql.txt"
cat "$WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/login_mysql.txt"




sed -i "s/ip=.*/ip=$PETS_K_HDFS_HOSTNAME/g" "$WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt"
sed -i "s/user_name=.*/user_name=$PEDSAS_USER/g" "$WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt"
sed -i "s/sftp_folder=.*/sftp_folder=$SFTP_FOLDER_/g" "$WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt"

echo "--------------------------------------------"
echo "s/sftp_folder=.*/sftp_folder=$SFTP_FOLDER_/g"


echo "請確認Hadoop_information.txt，內容為上傳服務端資訊------------------"
cat "$WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt"
echo "----------------------Hadoop_information.txt---內容結束------------------------------"

sleep 5


echo "PETS_K_HDFS_HOSTNAME is $PETS_K_HDFS_HOSTNAME"

sed -i "s/ip = .*/ip = $PETS_K_HDFS_HOSTNAME/g" "$WORKINGDIR_HADOOP_WEB/APP__/config/development.ini"

sed -i "s/port = .*/port = 11100/g" "$WORKINGDIR_HADOOP_WEB/APP__/config/development.ini"

#使用docker 內部IP (nodemasterS)
#sed -i "s/hdfs_hostname = .*/hdfs_hostname = "$PETS_K_HDFS_HOSTNAME/g" $WORKINGDIR_HADOOP_WEB/APP__/config/development.ini"
#sed -i "s/hdfs_port =.*/hdfs_port =$PETS_K_HDFS_PORT/g" "$WORKINGDIR_HADOOP_WEB/APP__/config/development.ini"

echo "請確認development.ini，內容為服務端資料庫資訊 --ip為須為服務端IP  --port須為11100--"
cat "$WORKINGDIR_HADOOP_WEB/APP__/config/development.ini"
echo "----------------------development.ini---內容結束------------------------------"
sleep 5
MARIA_IP=$PETS_K_HDFS_HOSTNAME
#MARIA_IP=35.194.150.235
MARIA_PORT=11100
sed -i "s/server=.*/server=$MARIA_IP;database=DeIdService;uid=deidadmin;pwd=citcw200;charset=utf8mb4;Port=$MARIA_PORT\"/g"  "$WORKINGDIR_HADOOP_WEB/appsettings.json"
sed -i "s/\"IP\": .*/\"IP\": \"$PETS_K_HDFS_HOSTNAME\"/g"  "$WORKINGDIR_HADOOP_WEB/appsettings.json"
echo "請確認appsettings.json --ConnIP為須為服務端IP"
cat "$WORKINGDIR_HADOOP_WEB/appsettings.json"
echo "-------------------appsettings.json------內容結束------------------------------"


sleep 5


cd ./sourceCode/webService

echo "start CITCWebservice: $PWD"

docker stack rm PETSWebserviceDir
docker stack deploy --with-registry-auth -c docker-compose.yml PETSWebserviceDir 
cd ../../
#echo $PWD
cd ./sourceCode/hadoop
echo "start CITCHadoop: $PWD"
#echo $PWD

docker stack rm PETSHadoopDir
docker stack deploy --with-registry-auth -c docker-compose.yml PETSHadoopDir
cd ../../

echo "working Dir: $PWD"

