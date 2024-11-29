#!/bin/bash



# Read 安裝目錄
echo "當pedsa_s的路徑為/home/ubuntu/mohw_188/pedsa_s 則安裝目錄取 /home/ubuntu/mohw_188"
echo -n 輸入PEDSA安裝目錄 "(例如/home/ubuntu/deploy_PEDSA_mohw ):"
read  deploy_dir1
deploy_dir=$deploy_dir1
echo "目前目錄 為 "$PWD
echo "PEDSA安裝目錄(deploy_dir) 為 "$deploy_dir
sleep 3

#return

#########main##############
#############install PATH參數########################################
#WORKINGDIR=/home/ubuntu/PETS
WORKINGDIR=$deploy_dir/pedsa_s
#WORKINGDIR=/home/$USER/PETS
#WORKINGDIR=/home/jeremyho/Pets_sourcecode
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

# Read GCP 外部IP
echo -n 主機IP"(例如 34.81.71.21):"
read  GCP_IP1
#GCP_IP=$GCP_IP1


# Read Password
echo "(當host user使用金鑰登入，直接按ENTER):"
echo -n Host User Password:
read -s password


#######要改的 此文件所在的主機IP##############
#CURRENT_IP=34.80.25.188
CURRENT_IP=$GCP_IP1
CURRENT_USER=$USER
CURRENT_PASS=$password
#docker network 內部IP
####################################### test
echo "CURRENT_IP 為 "$CURRENT_IP
echo "CURRENT_USER 為 "$CURRENT_USER


#########要改的 pets_syn 參數#########
#指向合成 IP and port
#sed -i 's#"DeIdWebAPI": .*#"DeIdWebAPI": {"URL": "http://35.201.239.123:5088"}#g' $WORKINGDIR_SYN_WEB/appsettings.json
#sed -i 's#"Gan_WebAPI": .*#"Gan_WebAPI": {"URL": "http://35.201.239.123:11055"}#g' $WORKINGDIR_SYN_WEB/appsettings.json
######################



#########要改的 pets_k 參數#########
#指向deid IP and port
#sed -i 's#"K_WebAPI": .*#"K_WebAPI": {"URL": "https://35.201.239.123:11000"}#g'  $WORKINGDIR_K_WEB/appsettings.json
######################



#########pets_hadoop (hadoop) 參數#########
PETS_HADOOP_IP=$CURRENT_IP
PETS_HADOOP_PORT=6922
##############################
#########pets_k (hadoop) 參數#########
#PETS_K_HDFS_HOSTNAME=deid.privacyprophet.com
PETS_K_HDFS_HOSTNAME=$CURRENT_IP
PETS_K_HDFS_PORT=5922
#5997
PETS_K_HADOOP_PORT=5088
PETS_K_WEBAPI_PORT=11000
##############################
#########pets_syn 參數#########
#PETS_SYN_HOSTNAME=deid.privacyprophet.com
PETS_SYN_HOSTNAME=$CURRENT_IP
PETS_SYN_DEIDWEBAPI_PORT=5088
PETS_SYN_WEBAPI_PORT=11055
##############################

#########pets_dp 參數#########
#PETS_DP_HDFS_HOSTNAME=deid.privacyprophet.com
PETS_DP_HDFS_HOSTNAME=$CURRENT_IP
PETS_DP_DEIDWEBAPI_PORT=5090
PETS_DP_WEBAPI_PORT=11065
PETS_DP_API_PORT=8081
##############################

#########Maria DB參數#############
#168.17.8.222 is fixed, see 
#docker network connect --ip 168.17.8.223 hadoopnet_overlay $MariaDB_nrt_id  >/dev/null 2>&1
MARIA_IP=168.17.8.253
#MARIA_IP=MariaDB_nrtSS
#MARIA_IP=$CURRENT_IP
export MARIA_IP
MARIA_PORT=3306
export MARIA_PORT
SSH_PORT=22
export SSH_PORT
#######################
#########FastAPI參數#############
#FASTAPI_HOSTNAME=deid.privacyprophet.com
#FASTAPI_HOSTNAME=$CURRENT_IP  http://pets_service_fastapi
FASTAPI_HOSTNAME=fastapi_service_compose
FASTAPI_PORT=11016
FASTAPI_PORT_INNER=8800
#######################


#########pets_web 參數################
#pets_web 參數
#/home/ubuntu/PETS/pets_web
#WEB_OUTER_PORT=80
NEXTAUTH_PORT=3000
PERMISSION_SERVICE=$FASTAPI_HOSTNAME
#PERMISSION_SERVICE_PORT=$FASTAPI_PORT
PERMISSION_SERVICE_PORT=$FASTAPI_PORT_INNER
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
echo "appsettings.json -- $WORKINGDIR_K_WEB/appsettings.json"
sed -i "s/server=.*/server=$MARIA_IP;database=DeIdService;uid=deidadmin;pwd=citcw200;charset=utf8mb4;Port=$MARIA_PORT\"/g" "$WORKINGDIR_K_WEB/appsettings.json"


#"URL": "https://34.81.71.21/kweb"
#sed -i "s/https:.*kweb/https:\/\/$PETS_K_HDFS_HOSTNAME\/kweb/g" "$WORKINGDIR_K_WEB/appsettings.json"
#sed -i "s/https:.*:$PETS_K_HADOOP_PORT/https:\/\/flask5997_compose:$PETS_K_HADOOP_PORT/g" $WORKINGDIR_K_WEB/appsettings.json
#sed -i "s/https:.*\/kweb/https:\/\/$PETS_K_HDFS_HOSTNAME\/kweb/g"  "$WORKINGDIR_K_WEB/appsettings.json"

#######appsettings.json (pets_k)  20240819 add for DNS####pedsas.moda.gov.tw##############################################################################1
HTTPS_DOMAIN_NMAE=IN_data-privacy.com.tw
CURRENT_DNS=pedsas.moda.gov.tw
#VARTOHTTPSDNS="IN_data-privacy.com.tw" 
VARTOHTTPSDNS="IN_data-privacy.com.tw" 
#VAR_K="IN_data-privacy.com.tw" 
if [ "$VARTOHTTPSDNS" = "$HTTPS_DOMAIN_NMAE" ]; then  
    echo "----------IN_pedsas.moda.gov.tw"  
    #CURRENT_DNS=data-privacy.com.tw
    sed -i "s/https:.*\/kweb/https:\/\/$CURRENT_DNS\/kweb/g"  "$WORKINGDIR_K_WEB/appsettings.json"
else     
    sed -i "s/https:.*\/kweb/https:\/\/$PETS_K_HDFS_HOSTNAME\/kweb/g"  "$WORKINGDIR_K_WEB/appsettings.json"
fi 

#https://35.194.150.235:11016
sed -i "s/https:.*:11016/https:\/\/$PETS_K_HDFS_HOSTNAME:11016/g" "$WORKINGDIR_K_WEB/appsettings.json"


cat "$WORKINGDIR_K_WEB/appsettings.json"


#cat "$WORKINGDIR_K_WEB/APP__/config/development.ini"
sed -i "s/ip = .*/ip = $MARIA_IP/g" "$WORKINGDIR_K_WEB/APP__/config/development.ini"
sed -i "s/port = .*/port = $MARIA_PORT/g" "$WORKINGDIR_K_WEB/APP__/config/development.ini"
sed -i "s/ip=.*/ip=$MARIA_IP/g" "$WORKINGDIR_K_HADOOP/masterCodeDir/longTaskDir/login_mysql.txt"
sed -i "s/port=.*/port=$MARIA_PORT/g" "$WORKINGDIR_K_HADOOP/masterCodeDir/longTaskDir/login_mysql.txt"

echo $CURRENT_PASS | sudo -S chown -R $CURRENT_USER "$WORKINGDIR_K_HADOOP/masterCodeDir/longTaskDir/"
sed -i "s/ip=.*/ip=$MARIA_IP/g" "$WORKINGDIR_K_HADOOP/masterCodeDir/longTaskDir/login_mysql.txt"
sed -i "s/port=.*/port=$MARIA_PORT/g" "$WORKINGDIR_K_HADOOP/masterCodeDir/longTaskDir/login_mysql.txt"
echo "pets_k ----- login_mysql.txt --$WORKINGDIR_K_HADOOP/masterCodeDir/longTaskDir/login_mysql.txt"
#cat "$WORKINGDIR_K_HADOOP/masterCodeDir/longTaskDir/login_mysql.txt"


#20231221 add-------------------------------
#/home/ubuntu/PETS/pets_k/pets_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/Hadoop_information.txt*
sed -i "s/ip=.*/ip=$PETS_HADOOP_IP/g" "$WORKINGDIR_K_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt"
sed -i "s/port=.*/port=$PETS_HADOOP_PORT/g" "$WORKINGDIR_K_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt"
sed -i "s/web_ip=.*/web_ip=$SUBSERVICE_K_HOST/g" "$WORKINGDIR_K_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt"
#因為 kweb改成 所以不改
#response_g = requests.get("https://"+web_ip+"/kweb/api/WebAPI/GetKChecking", params=k_GetKChecking_para,timeout=None, verify=False) ()
sed -i "s/web_port=.*/web_port=$SUBSERVICE_K_PORT/g" "$WORKINGDIR_K_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt"
echo "Hadoop_information.txt --$WORKINGDIR_K_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt"
cat "$WORKINGDIR_K_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt"

#--------------------------------------------------------------

#20231212 #HDFS_HOSTNAME=$CURRENT_IP HDFS_PORT=5922 
#sed -i "s/hdfs_hostname = .*/hdfs_hostname = $PETS_K_HDFS_HOSTNAME/g" "$WORKINGDIR_K_WEB/APP__/config/development.ini"
#sed -i "s/hdfs_port = .*/hdfs_port = $PETS_K_HDFS_PORT/g" "$WORKINGDIR_K_WEB/APP__/config/development.ini"
#for appsetting.json (1215) PETS_K_HADOOP_PORT= 5008 flask5997_compose
#echo "development.txt --$WORKINGDIR_K_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt"
#cat "$WORKINGDIR_K_WEB/APP__/config/development.ini"
#return 


#return
############pets_syn###########
sed -i "s/server=.*/server=$MARIA_IP;database=SynService;uid=deidadmin;pwd=citcw200;charset=utf8mb4;Port=$MARIA_PORT\"/g" "$WORKINGDIR_SYN_WEB/appsettings.json"
sed -i "s/ip = .*/ip = $MARIA_IP/g" "$WORKINGDIR_SYN_WEB/APP__/config/development.ini"
sed -i "s/port = .*/port = $MARIA_PORT/g" "$WORKINGDIR_SYN_WEB/APP__/config/development.ini"
#20231212 #HDFS_HOSTNAME=$CURRENT_IP HDFS_PORT=5922 (not use)
sed -i "s/hdfs_hostname = .*/hdfs_hostname = $PETS_K_HDFS_HOSTNAME/g" "$WORKINGDIR_SYN_WEB/APP__/config/development.ini"
sed -i "s/hdfs_port = .*/hdfs_port = $PETS_K_HDFS_PORT/g" "$WORKINGDIR_SYN_WEB/APP__/config/development.ini"
#return
#20231212
#for joint，用在scp, port=6922
#/home/ubuntu/PETS/pets_syn/pets_syn/sourceCode/webService/APP__/config/Hadoop_information.txt 
sed -i "s/ip=.*/ip=$PETS_HADOOP_IP/g" "$WORKINGDIR_SYN_WEB/APP__/config/Hadoop_information.txt"
#return
sed -i "s/hdfs_port =.*/hdfs_port = $PETS_HADOOP_PORT/g" "$WORKINGDIR_SYN_WEB/APP__/config/Hadoop_information.txt"
#return
sed -i "s/user=.*/user=$CURRENT_USER/g" "$WORKINGDIR_SYN_WEB/APP__/config/Hadoop_information.txt"
sed -i "s/passwd=.*/passwd=$CURRENT_PASS/g" "$WORKINGDIR_SYN_WEB/APP__/config/Hadoop_information.txt"
echo "syn -- Hadoop_information.txt for join $WORKINGDIR_SYN_WEB/APP__/config/Hadoop_information.txt"
cat "$WORKINGDIR_SYN_WEB/APP__/config/Hadoop_information.txt"

#for appsetting.json ########### (pets_syn)####################
sed -i "s/http:.*:$PETS_SYN_DEIDWEBAPI_PORT/http:\/\/flask_syn_compose:$PETS_SYN_DEIDWEBAPI_PORT/g" "$WORKINGDIR_SYN_WEB/appsettings.json"
#sed -i "s/https:.*:$SUBSERVICE_SYN_PORT/http:\/\/$SUBSERVICE_SYN_HOST:$SUBSERVICE_SYN_PORT/g" "$WORKINGDIR_SYN_WEB/appsettings.json"
#sed -i "s/https:.*:$SUBSERVICE_SYN_PORT/http:\/\/$SUBSERVICE_SYN_HOST:$SUBSERVICE_SYN_PORT/g" "$WORKINGDIR_SYN_WEB/appsettings.json"

#######appsettings.json (pets_syn)  20240819 add for DNS##################################################################################1
#VAR_SYN="IN_data-privacy.com.tw" 
if [ "$VARTOHTTPSDNS" = "$HTTPS_DOMAIN_NMAE" ]; then  
    echo "----------IN_pedsas.moda.gov.tw"  
    #CURRENT_DNS=data-privacy.com.tw
    sed -i "s/https:.*\/synweb/https:\/\/$CURRENT_DNS\/synweb/g"  "$WORKINGDIR_SYN_WEB/appsettings.json"
else     
    sed -i "s/https:.*\/synweb/https:\/\/$PETS_SYN_HOSTNAME\/synweb/g"  "$WORKINGDIR_SYN_WEB/appsettings.json"
fi 

#https://35.194.150.235:11016
sed -i "s/https:.*:11016/https:\/\/$PETS_SYN_HOSTNAME:11016/g" "$WORKINGDIR_SYN_WEB/appsettings.json"

echo "syn -- appsetting.json $WORKINGDIR_SYN_WEB/appsettings.json"
cat "$WORKINGDIR_SYN_WEB/appsettings.json"
#SUBSERVICE_SYN_HOST=$CURRENT_IP
#SUBSERVICE_SYN_PORT=11055=PETS_SYN_WEBAPI_PORT



############pets_dp###########
#sed -i "s/server=.*/server=$MARIA_IP;database=DpService;uid=deidadmin;pwd=citcw200;charset=utf8mb4;Port=$MARIA_PORT\"/g" $WORKINGDIR_DP_WEB/appsettings.json
sed -i "s/ip = .*/ip = $MARIA_IP/g" "$WORKINGDIR_DP_WEB/APP__/config/development.ini"
sed -i "s/port = .*/port = $MARIA_PORT/g" "$WORKINGDIR_DP_WEB/APP__/config/development.ini"
#20231212 #HDFS_HOSTNAME=$CURRENT_IP HDFS_PORT=5922 (not use)
sed -i "s/hdfs_hostname =.*/hdfs_hostname =$PETS_K_HDFS_HOSTNAME/g" "$WORKINGDIR_DP_WEB/APP__/config/development.ini"
sed -i "s/hdfs_port =.*/hdfs_port =$PETS_K_HDFS_PORT/g" "$WORKINGDIR_DP_WEB/APP__/config/development.ini"

#cat "--dp development.ini-- $WORKINGDIR_DP_WEB/APP__/config/development.ini"
#cat "$WORKINGDIR_DP_WEB/APP__/config/development.ini"
#return
#20231212
#for joint，用在scp, port=6922 (PETS_HADOOP_PORT)
#/home/ubuntu/PETS/pets_syn/pets_syn/sourceCode/webService/APP__/config/Hadoop_information.txt 
sed -i "s/ip=.*/ip=$PETS_HADOOP_IP/g" "$WORKINGDIR_DP_WEB/APP__/config/Hadoop_information.txt"
sed -i "s/hdfs_port =.*/hdfs_port = $PETS_HADOOP_PORT/g" "$WORKINGDIR_DP_WEB/APP__/config/Hadoop_information.txt"

sed -i "s/user=.*/user=$CURRENT_USER/g" "$WORKINGDIR_DP_WEB/APP__/config/Hadoop_information.txt"
sed -i "s/passwd=.*/passwd=$CURRENT_PASS/g" "$WORKINGDIR_DP_WEB/APP__/config/Hadoop_information.txt"
echo "dp -- Hadoop_information.txt for join $WORKINGDIR_DP_WEB/APP__/config/Hadoop_information.txt"
cat "$WORKINGDIR_DP_WEB/APP__/config/Hadoop_information.txt"



########appsettings.json (pets_dp)###########
sed -i "s/server=.*/server=$MARIA_IP;database=DpService;uid=deidadmin;pwd=citcw200;charset=utf8mb4;Port=$MARIA_PORT\"/g" "$WORKINGDIR_DP_WEB/appsettings.json"
sed -i "s/http:.*:$PETS_DP_DEIDWEBAPI_PORT/http:\/\/flaskdp_compose:5088/g" "$WORKINGDIR_DP_WEB/appsettings.json"
sed -i "s/https:.*:$PETS_DP_WEBAPI_PORT/http:\/\/$PETS_DP_HDFS_HOSTNAME:$PETS_DP_WEBAPI_PORT/g" "$WORKINGDIR_DP_WEB/appsettings.json"
#sed -i "s/https:.*:$PETS_DP_API_PORT/http:\/\/$PETS_DP_HDFS_HOSTNAME:$PETS_DP_API_PORT/g" "$WORKINGDIR_DP_WEB/appsettings.json"
#sed -i "s/https:.*:$PETS_DP_WEBAPI_PORT/http:\/\/$PETS_DP_HDFS_HOSTNAME:$PETS_DP_WEBAPI_PORT/g" $WORKINGDIR_DP_WEB/appsettings.json

#######appsettings.json (pets_dp)  0240819 add for DNS##################################################################################1
#VAR_DP="IN_data-privacy.com.tw" 
if [ "$VARTOHTTPSDNS" = "$HTTPS_DOMAIN_NMAE" ]; then  
    echo "----------IN_pedsas.moda.gov.tw"  
    #CURRENT_DNS=data-privacy.com.tw
    sed -i "s/https:.*\/dpweb/https:\/\/$CURRENT_DNS\/dpweb/g"  "$WORKINGDIR_DP_WEB/appsettings.json"
else     
    sed -i "s/https:.*\/dpweb/https:\/\/$PETS_DP_HDFS_HOSTNAME\/dpweb/g"  "$WORKINGDIR_DP_WEB/appsettings.json"
    sed -i "s/http:.*\/dpweb/https:\/\/$PETS_DP_HDFS_HOSTNAME\/dpweb/g"  "$WORKINGDIR_DP_WEB/appsettings.json"
fi 
#https://35.194.150.235:11016
sed -i "s/https:.*:11016/https:\/\/$PETS_DP_HDFS_HOSTNAME:11016/g"  "$WORKINGDIR_DP_WEB/appsettings.json"


echo "dp -- appsetting.json $WORKINGDIR_DP_WEB/appsettings.json"
cat "$WORKINGDIR_DP_WEB/appsettings.json"

#sed -i "s/http:.*:$PETS_DP_API_PORT/http:\/\/34.81.119.49:8060/g" $WORKINGDIR_DP_WEB/appsettings.json
#sed -i "s/http:.*:8060/http:\/\/34.81.119.49:8060/g" $WORKINGDIR_DP_WEB/appsettings.json
#PETS_DP_API_PORT=8081




############pets_hadoop for join###########
sed -i "s/ip=.*/ip=MariaDB_nrtS/g" "$WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/login_mysql.txt"
sed -i "s/port=.*/port=3306/g" "$WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/login_mysql.txt"

echo "pets_hadoop -- login_mysql.txt $WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/login_mysql.txt"
#cat "$WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/login_mysql.txt"
#####20240306#############################
#for joint，用在scp, port=6922
#/home/ubuntu/PETS/pets_service/petsservice/config/Hadoop_information.txt
sed -i "s/ip=.*/ip=$PETS_HADOOP_IP/g" "$WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt"
sed -i "s/port=.*/port=$PETS_HADOOP_PORT/g" "$WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt"

sed -i "s/k_port=.*/k_port=$PETS_K_HDFS_PORT/g" "$WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt"
sed -i "s/web_ip=.*/web_ip=$SUBSERVICE_K_HOST/g" "$WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt"
sed -i "s/web_port=.*/web_port=$SUBSERVICE_K_PORT/g" "$WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt"
sed -i "s/gan_ip=.*/gan_ip=$SUBSERVICE_SYN_HOST/g" "$WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt"
sed -i "s/gan_port=.*/gan_port=$SUBSERVICE_SYN_PORT/g" "$WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt"
#PETS_DP_WEBAPI_PORT=11065
sed -i "s/dp_port=.*/dp_port=$PETS_DP_WEBAPI_PORT/g" "$WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt"


#data_privacy_ip=data-privacy.com.tw 
#requests.get("https://"+data_privacy_ip+"/kweb/api/WebAPI/k_conn
#requests.get("https://"+data_privacy_ip+"/synweb/api/WebAPI/syn_conn"
sed -i "s/data_privacy_ip=.*/data_privacy_ip=$SUBSERVICE_K_HOST/g" "$WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt"

echo "pets_hadoop -- login_mysql.txt $WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt"
cat "$WORKINGDIR_HADOOP_HADOOP/masterCodeDir/longTaskDir/Hadoop_information.txt"


############pets_service###########
#WORKINGDIR_PETS_SERVICES=$WORKINGDIR/pets_service
#/home/ubuntu/PETS/pets_service/petsservice/config/development.ini 呼叫 pets_hadoop join 程式 (tony新增), 所以port=6922
sed -i "s/ip = .*/ip = $MARIA_IP/g" "$WORKINGDIR_PETS_SERVICES/petsservice/config/development.ini"
sed -i "s/port = .*/port = $MARIA_PORT/g" "$WORKINGDIR_PETS_SERVICES/petsservice/config/development.ini"

#####################################0730使用內部IP 168.17.8.252=PET_join_Hadoop_nodemaster################################################################1
#sed -i "s/hdfs_hostname = .*/hdfs_hostname = $PETS_HADOOP_IP/g" "$WORKINGDIR_PETS_SERVICES/petsservice/config/development.ini"
#sed -i "s/hdfs_port = .*/hdfs_port = $PETS_HADOOP_PORT/g" "$WORKINGDIR_PETS_SERVICES/petsservice/config/development.ini"
sed -i "s/hdfs_hostname = .*/hdfs_hostname = 168.17.8.252/g" "$WORKINGDIR_PETS_SERVICES/petsservice/config/development.ini"
sed -i "s/hdfs_port = .*/hdfs_port = 22/g" "$WORKINGDIR_PETS_SERVICES/petsservice/config/development.ini"
#####################################0730使用內部IP 168.17.8.252=PET_join_Hadoop_nodemaster################################################################2
#20231212
#for joint，用在scp, port=6922
#/home/ubuntu/PETS/pets_service/petsservice/config/Hadoop_information.txt
#echo "10000000000000000000000---"
sed -i "s/ip=.*/ip=$PETS_HADOOP_IP/g" "$WORKINGDIR_PETS_SERVICES/petsservice/config/Hadoop_information.txt"
#echo "10000000000000000000000"
sed -i "s/port=.*/port=$PETS_HADOOP_PORT/g" "$WORKINGDIR_PETS_SERVICES/petsservice/config/Hadoop_information.txt"
sed -i "s/k_port=.*/k_port=$PETS_K_HDFS_PORT/g" "$WORKINGDIR_PETS_SERVICES/petsservice/config/Hadoop_information.txt"
sed -i "s/web_ip=.*/web_ip=$SUBSERVICE_K_HOST/g" "$WORKINGDIR_PETS_SERVICES/petsservice/config/Hadoop_information.txt"
sed -i "s/web_port=.*/web_port=$SUBSERVICE_K_PORT/g" "$WORKINGDIR_PETS_SERVICES/petsservice/config/Hadoop_information.txt"
sed -i "s/gan_ip=.*/gan_ip=$SUBSERVICE_SYN_HOST/g" "$WORKINGDIR_PETS_SERVICES/petsservice/config/Hadoop_information.txt"
sed -i "s/gan_port=.*/gan_port=$SUBSERVICE_SYN_PORT/g" "$WORKINGDIR_PETS_SERVICES/petsservice/config/Hadoop_information.txt"
sed -i "s/join_ip=.*/join_ip=$PETS_HADOOP_IP/g" "$WORKINGDIR_PETS_SERVICES/petsservice/config/Hadoop_information.txt"
sed -i "s/join_port=.*/join_port=$PETS_HADOOP_PORT/g" "$WORKINGDIR_PETS_SERVICES/petsservice/config/Hadoop_information.txt"
#echo "100000000000000000000001"
sed -i "s/host_ip=.*/host_ip=$CURRENT_IP/g" "$WORKINGDIR_PETS_SERVICES/petsservice/config/Hadoop_information.txt"
echo "for join pets_service -- $WORKINGDIR_PETS_SERVICES/petsservice/config/Hadoop_information.txt"

cat "$WORKINGDIR_PETS_SERVICES/petsservice/config/Hadoop_information.txt"


#pets service 環境變數
echo "======================================================="
echo $WORKINGDIR_PETS_SERVICES/petsservice/.env
echo "======================================================="
sed -i "s/DB_SERVER=.*/DB_SERVER=$MARIA_IP/g" "$WORKINGDIR_PETS_SERVICES/petsservice/.env"
sed -i "s/DB_PORT=.*/DB_PORT=$MARIA_PORT/g" "$WORKINGDIR_PETS_SERVICES/petsservice/.env"
echo "pets_service -- $WORKINGDIR_PETS_SERVICES/petsservice/.env"
cat "$WORKINGDIR_PETS_SERVICES/petsservice/.env"

#設定 要monitor docker container狀況的主機 IP :\/\/MARIA_IP\'/g
#MONITOR_IP=34.81.71.21，改程式
sed -i "s/tcp:.*/tcp:\/\/$MONITOR_IP:2376\', tls=tls_config)/g" "$WORKINGDIR_PETS_SERVICES/petsservice/config/getContainersStatus.py"

export WORKINGDIR_PETS_SERVICES
#20231214 for delete ip/prot
sed -i "s/ip=.*/ip=$CURRENT_IP/g" "$WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt"
sed -i "s/port = .*/port = $SSH_PORT/g" "$WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt"
sed -i "s/user=.*/user=$CURRENT_USER/g" "$WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt"
echo "--------CURRENT_PASS is----------------------------------------------------1"
echo $CURRENT_PASS
echo $CURRENT_USER
echo "$WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt"
echo "s/pets_hadoop_in = .*/pets_hadoop_in = \'$WORKINGDIR_PETS_SERVICES\/pets_hadoop\/pets_v1\/sourceCode\/hadoop\/data\/input\/\'/g"
echo "---------------------------------------------------------------------------2"




sed -i "s/passwd=.*/passwd=$CURRENT_PASS/g" "$WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt"
sed -i "s/k_web_ip = .*/k_web_ip = $SUBSERVICE_K_HOST/g" "$WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt"
sed -i "s/k_web_port = .*/k_web_port = $SUBSERVICE_K_PORT/g" "$WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt"
sed -i "s/syn_web_ip = .*/syn_web_ip = $SUBSERVICE_SYN_HOST/g" "$WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt"
sed -i "s/syn_web_port = .*/syn_web_port = $SUBSERVICE_SYN_PORT/g" "$WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt"
#####for delete path

##bash insert backslash for every slash in string
#string='/tmp/something'
#escapedstring="${string//\//\\\/}"
#printf '%s\n' "$escapedstring"     
#\/tmp\/something


WORKINGDIR_K_HADOOP_=$WORKINGDIR_K_HADOOP/pets_v1/sourceCode/hadoop/data/input/

echo $WORKINGDIR_HADOOP_HADOOP
#/home/ubuntu/deploy_PEDSA/pedsa_s/pets_hadoop/pets_v1/sourceCode/hadoop
WORKINGDIR_HADOOP_HADOOP_input=$WORKINGDIR_HADOOP_HADOOP/data/input/
WORKINGDIR_HADOOP_HADOOP_input_="${WORKINGDIR_HADOOP_HADOOP_input//\//\\\/}"
sed -i "s/pets_hadoop_in =.*/pets_hadoop_in =$WORKINGDIR_HADOOP_HADOOP_input_/g" "$WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt"

WORKINGDIR_HADOOP_HADOOP_output=$WORKINGDIR_HADOOP_HADOOP/data/output/
WORKINGDIR_HADOOP_HADOOP_output_="${WORKINGDIR_HADOOP_HADOOP_output//\//\\\/}"
sed -i "s/pets_hadoop_out =.*/pets_hadoop_out =$WORKINGDIR_HADOOP_HADOOP_output_/g" "$WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt"

WORKINGDIR_HADOOP_HADOOP_final_k_i=$WORKINGDIR_HADOOP_HADOOP/final_project/k/input/
WORKINGDIR_HADOOP_HADOOP_final_k_i_="${WORKINGDIR_HADOOP_HADOOP_final_k_i//\//\\\/}"
sed -i "s/pets_final_k_in =.*/pets_final_k_in =$WORKINGDIR_HADOOP_HADOOP_final_k_i_/g" "$WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt"

WORKINGDIR_HADOOP_HADOOP_final_k_o=$WORKINGDIR_HADOOP_HADOOP/final_project/k/output/
WORKINGDIR_HADOOP_HADOOP_final_k_o_="${WORKINGDIR_HADOOP_HADOOP_final_k_o//\//\\\/}"
sed -i "s/pets_final_k_out =.*/pets_final_k_out =$WORKINGDIR_HADOOP_HADOOP_final_k_o_/g" "$WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt"

#pets_final_syn_in =/home/ubuntu/deploy_PEDSA/pedsa_s/pets_hadoop/pets_v1/sourceCode/hadoop/final_project/syn/input/
WORKINGDIR_HADOOP_HADOOP_final_syn_i=$WORKINGDIR_HADOOP_HADOOP/final_project/syn/input/
WORKINGDIR_HADOOP_HADOOP_final_syn_i_="${WORKINGDIR_HADOOP_HADOOP_final_syn_i//\//\\\/}"
sed -i "s/pets_final_syn_in =.*/pets_final_syn_in =$WORKINGDIR_HADOOP_HADOOP_final_syn_i_/g" "$WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt"

#pets_final_syn_out =/home/ubuntu/deploy_PEDSA/pedsa_s/pets_hadoop/pets_v1/sourceCode/hadoop/final_project/syn/output/
WORKINGDIR_HADOOP_HADOOP_final_syn_o=$WORKINGDIR_HADOOP_HADOOP/final_project/syn/ouput/
WORKINGDIR_HADOOP_HADOOP_final_syn_o_="${WORKINGDIR_HADOOP_HADOOP_final_syn_o//\//\\\/}"
sed -i "s/pets_final_syn_out =.*/pets_final_syn_out =$WORKINGDIR_HADOOP_HADOOP_final_syn_o_/g" "$WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt"

WORKINGDIR_PETS_WEB_download_enc_k=$WORKINGDIR_PETS_WEB/download_folder/enc/k/
WORKINGDIR_PETS_WEB_download_enc_k_="${WORKINGDIR_PETS_WEB_download_enc_k//\//\\\/}"
sed -i "s/pets_download_enc =.*/pets_download_enc =$WORKINGDIR_PETS_WEB_download_enc_k_/g" "$WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt"
echo "00-------------------------------"
WORKINGDIR_PETS_SERVICES_sftp_upload_floder=$WORKINGDIR_PETS_WEB/sftp_upload_floder/
WORKINGDIR_PETS_SERVICES_sftp_upload_floder_="${WORKINGDIR_PETS_SERVICES_sftp_upload_floder//\//\\\/}"
#WORKINGDIR_PETS_SERVICES=$WORKINGDIR/pets_service
sed -i "s/pets_upload =.*/pets_upload =$WORKINGDIR_PETS_SERVICES_sftp_upload_floder_/g" "$WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt"
echo "0-------------------------------"
WORKINGDIR_SYN_WEB_user_upload_folder=$WORKINGDIR_SYN_WEB/APP__/user_upload_folder/
WORKINGDIR_SYN_WEB_user_upload_folder_="${WORKINGDIR_SYN_WEB_user_upload_folder//\//\\\/}"
sed -i "s/user_upload_folder =.*/user_upload_folder =$WORKINGDIR_SYN_WEB_user_upload_folder_/g" "$WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt"

echo "1-------------------------------"
WORKINGDIR_HADOOP_HADOOP_final_syn_iWORKINGDIR_SYN_WEB_folderForSynthetic=$WORKINGDIR_SYN_WEB/APP__/folderForSynthetic/
WORKINGDIR_SYN_WEB_folderForSynthetic_="${WORKINGDIR_SYN_WEB_folderForSynthetic//\//\\\/}"
sed -i "s/folderForSynthetic =.*/folderForSynthetic =$WORKINGDIR_SYN_WEB_folderForSynthetic_/g" "$WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt"

#---------------------
WORKINGDIR_DP=$WORKINGDIR/pets_dp/dp
#WORKINGDIR_DP_WEB=$WORKINGDIR/pets_dp/pets_dp/sourceCode/DP_webService
#export WORKINGDIR_DP_WEB

#dp_file_path =/home/ubuntu/PETS/pets_dp/dp/de-identification/static/test/

WORKINGDIR_DP_dp_file_path=$WORKINGDIR_DP/de-identification/static/test/
WORKINGDIR_DP_dp_file_path_="${WORKINGDIR_DP_dp_file_path//\//\\\/}"
sed -i "s/dp_file_path =.*/dp_file_path =$WORKINGDIR_DP_dp_file_path_/g" "$WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt"


#dp_upload_folder =/home/ubuntu/deploy_PEDSA/pedsa_s/pets_dp/pets_dp/sourceCode/DP_webService/APP__/user_upload_folder/
#WORKINGDIR_DP_WEB=$WORKINGDIR/pets_dp/pets_dp/sourceCode/DP_webService
#export WORKINGDIR_DP_WEB
WORKINGDIR_DP_WEB_dp_upload_folder=$WORKINGDIR_DP_WEB/APP__/user_upload_folder/
WORKINGDIR_DP_WEB_dp_upload_folder_="${WORKINGDIR_DP_WEB_dp_upload_folder//\//\\\/}"
sed -i "s/dp_upload_folder =.*/dp_upload_folder =$WORKINGDIR_DP_WEB_dp_upload_folder_/g" "$WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt"

#dp_folderForSynthetic =/home/ubuntu/deploy_PEDSA/pedsa_s/pets_dp/pets_dp/sourceCode/DP_webService/APP__/folderForSynthetic/
WORKINGDIR_DP_WEB_dp_folderForSynthetic=$WORKINGDIR_DP_WEB/APP__/folderForSynthetic/
WORKINGDIR_DP_WEB_dp_folderForSynthetic_="${WORKINGDIR_DP_WEB_dp_folderForSynthetic//\//\\\/}"
sed -i "s/dp_folderForSynthetic =.*/dp_folderForSynthetic =$WORKINGDIR_DP_WEB_dp_folderForSynthetic_/g" "$WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt"


#pets_hadoop_import_path= /home/ubuntu/deploy_PEDSA/pedsa_s/pets_hadoop/pets_v1/sourceCode/hadoop/data/input/
#WORKINGDIR_K_HADOOP=$WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop
#export WORKINGDIR_K_HADOOP
WORKINGDIR_K_HADOOP_pets_hadoop_import_path=$WORKINGDIR_K_HADOOP/data/input/
WORKINGDIR_K_HADOOP_pets_hadoop_import_path_="${WORKINGDIR_K_HADOOP_pets_hadoop_import_path//\//\\\/}"
sed -i "s/pets_hadoop_import_path =.*/pets_hadoop_import_path =$WORKINGDIR_K_HADOOP_pets_hadoop_import_path_/g" "$WORKINGDIR_PETS_SERVICES/petsservice/app/core/projects/delete_config.txt"



#-----------------------

#return


sed -i "s/NEXTAUTH_URL=.*/NEXTAUTH_URL=\'http:\/\/localhost:$NEXTAUTH_PORT\/\'/g" "$WORKINGDIR_PETS_WEB/pets_web/.env"

sed -i "s/PERMISSION_SERVICE=.*/PERMISSION_SERVICE=\'http:\/\/$PERMISSION_SERVICE\'/g" "$WORKINGDIR_PETS_WEB/pets_web/.env"
sed -i "s/PERMISSION_SERVICE_PORT=.*/PERMISSION_SERVICE_PORT=\'$PERMISSION_SERVICE_PORT\'/g" "$WORKINGDIR_PETS_WEB/pets_web/.env"

#######20240815 add for DNS##################################################################################1
#HTTPS_DOMAIN_NMAE=IN_data-privacy.com.tw
#VARTOHTTPSDNS="IN_data-privacy.com.tw"  
  
if [ "$VARTOHTTPSDNS" = "$HTTPS_DOMAIN_NMAE" ]; then  
    echo "----------IN_data-privacy.com.tw"  
    #CURRENT_DNS=data-privacy.com.tw
    #sed -i "s/SUBSERVICE_K_HOST=.*/SUBSERVICE_K_HOST=\'https:\/\/data-privacy.com.tw\'/g" $WORKINGDIR_PETS_WEB/pets_web/.env
    sed -i "s/SUBSERVICE_K_HOST=.*/SUBSERVICE_K_HOST=\'https:\/\/$CURRENT_DNS\'/g" "$WORKINGDIR_PETS_WEB/pets_web/.env"
    sed -i "s/SUBSERVICE_K_PORT=.*/SUBSERVICE_K_PORT=\'443\'/g" "$WORKINGDIR_PETS_WEB/pets_web/.env"

    #sed -i "s/SUBSERVICE_SYN_HOST=.*/SUBSERVICE_SYN_HOST=\'https:\/\/data-privacy.com.tw\'/g" $WORKINGDIR_PETS_WEB/pets_web/.env
    sed -i "s/SUBSERVICE_SYN_HOST=.*/SUBSERVICE_SYN_HOST=\'https:\/\/$CURRENT_DNS\'/g" "$WORKINGDIR_PETS_WEB/pets_web/.env"
    sed -i "s/SUBSERVICE_SYN_PORT=.*/SUBSERVICE_SYN_PORT=\'443\'/g" "$WORKINGDIR_PETS_WEB/pets_web/.env"

    #sed -i "s/SUBSERVICE_DP_HOST=.*/SUBSERVICE_DP_HOST=\'https:\/\/data-privacy.com.tw\'/g" $WORKINGDIR_PETS_WEB/pets_web/.env #$CURRENT_IP
    sed -i "s/SUBSERVICE_DP_HOST=.*/SUBSERVICE_DP_HOST=\'https:\/\/$CURRENT_DNS\'/g" "$WORKINGDIR_PETS_WEB/pets_web/.env"
    sed -i "s/SUBSERVICE_DP_PORT=.*/SUBSERVICE_DP_PORT=\'443\'/g" "$WORKINGDIR_PETS_WEB/pets_web/.env"
    sed -i "s/SUBSERVICE_DP_PORT=.*/SUBSERVICE_DP_PORT=\'443\'/g" "$WORKINGDIR_PETS_WEB/pets_web/.env"
else  
    echo "---pets_web-----------------NOT IN_data-privacy.com.tw"  
    #sed -i "s/SUBSERVICE_K_HOST=.*/SUBSERVICE_K_HOST=\'https:\/\/data-privacy.com.tw\'/g" $WORKINGDIR_PETS_WEB/pets_web/.env
    sed -i "s/SUBSERVICE_K_HOST=.*/SUBSERVICE_K_HOST=\'https:\/\/$CURRENT_IP\'/g" "$WORKINGDIR_PETS_WEB/pets_web/.env"
    sed -i "s/SUBSERVICE_K_PORT=.*/SUBSERVICE_K_PORT=\'443\'/g" "$WORKINGDIR_PETS_WEB/pets_web/.env"

    #sed -i "s/SUBSERVICE_SYN_HOST=.*/SUBSERVICE_SYN_HOST=\'https:\/\/data-privacy.com.tw\'/g" $WORKINGDIR_PETS_WEB/pets_web/.env
    sed -i "s/SUBSERVICE_SYN_HOST=.*/SUBSERVICE_SYN_HOST=\'https:\/\/$CURRENT_IP\'/g" "$WORKINGDIR_PETS_WEB/pets_web/.env"
    sed -i "s/SUBSERVICE_SYN_PORT=.*/SUBSERVICE_SYN_PORT=\'443\'/g" "$WORKINGDIR_PETS_WEB/pets_web/.env"

    #sed -i "s/SUBSERVICE_DP_HOST=.*/SUBSERVICE_DP_HOST=\'https:\/\/data-privacy.com.tw\'/g" $WORKINGDIR_PETS_WEB/pets_web/.env #$CURRENT_IP
    sed -i "s/SUBSERVICE_DP_HOST=.*/SUBSERVICE_DP_HOST=\'https:\/\/$CURRENT_IP\'/g" "$WORKINGDIR_PETS_WEB/pets_web/.env"
    sed -i "s/SUBSERVICE_DP_PORT=.*/SUBSERVICE_DP_PORT=\'443\'/g" "$WORKINGDIR_PETS_WEB/pets_web/.env"
    sed -i "s/SUBSERVICE_DP_PORT=.*/SUBSERVICE_DP_PORT=\'443\'/g" "$WORKINGDIR_PETS_WEB/pets_web/.env"
fi 
#######20240815 add for DNS##############################################################################2




#移到create_docker_env.sh，因為啟動前就要mount好所有(host 目錄)，
# docker才會正常連結 (內部目錄) 與 (host 目錄)
## mount --bind <source_data_owner> <target_mnt_point>
# mount --bind "/home/$CURRENT_USER/PETS/pets_hadoop/pets_v1/sourceCode/hadoop/final_project/k/input" "/home/$CURRENT_USER/PETS/pets_web/download_folder/enc/k"
# mount --bind "/home/$CURRENT_USER/PETS/pets_hadoop/pets_v1/sourceCode/hadoop/final_project/k/output" "/home/$CURRENT_USER/PETS/pets_web/download_folder/dec/k"
# mount --bind "/home/$CURRENT_USER/PETS/pets_hadoop/pets_v1/sourceCode/hadoop/final_project/syn/output" "/home/$CURRENT_USER/PETS/pets_web/download_folder/enc/syn"
# mount --bind "/home/$CURRENT_USER/PETS/pets_hadoop/pets_v1/sourceCode/hadoop/final_project/dp/output" "/home/$CURRENT_USER/PETS/pets_web/download_folder/enc/dp"


MariaDB_nrt_id=$(docker ps -aqf "name=MariaDB_nrt")

#----------------

IFS=' ' read -r -a array <<< "$MariaDB_nrt_id"
echo "--------all MariaDB_nrt_id are ""${array[@]}"
#for index in "${!array[@]}"
for element in "${array[@]}"
do
    echo "MariaDB_nrt_id is ""$element"
    val1L=${#element} #len=12
    if [ $val1L == 12 ]; then
        echo "-------------------------------------起始--rm MariaDB--- "
        docker rm -f $MariaDB_nrt_id
    else
	    echo "MariaDB_nrt_id is------"$MariaDB_nrt_id"------"
        echo "----#######-----------起始--rm MariaDB 失敗，注意MariaDB狀態--------######----------- "
        sleep 20
        #return
    fi

done

#################################################################################
PET_join_Hadoop_nodemaster_id=$(docker ps -aqf "name=PET_join_Hadoop_nodemaster")
#################################################################################
#----------------

IFS=' ' read -r -a array <<< "$PET_join_Hadoop_nodemaster_id"
echo "---------all PET_join_Hadoop_nodemaster_id are ""${array[@]}"
#for index in "${!array[@]}"
for element in "${array[@]}"
do
    echo "PET_join_Hadoop_nodemaster_id is ""$element"
    val1L=${#element} #len=12
    if [ $val1L == 12 ]; then
        echo "-------------------------------------起始--rm PET_join_Hadoop_nodemaster_id--- "
        docker rm -f $PET_join_Hadoop_nodemaster_id
    else
	       echo "PET_join_Hadoop_nodemaster_id is------"$PET_join_Hadoop_nodemaster_id"------"
        echo "----#######-----------起始--rm PET_join_Hadoop_nodemaster 失敗，注意PET_join_Hadoop_nodemaster狀態--------######----------- "
        sleep 20
        #return
    fi

done

#---------------

#val1L=${#MariaDB_nrt_id} #len=12
#if [ $val1L == 12 ]; then
#    echo "-------------------------------------起始--rm MariaDB--- "
#    docker rm -f $MariaDB_nrt_id
#else
#	echo "MariaDB_nrt_id is------"$MariaDB_nrt_id"------"
#    echo "----#######-----------起始--rm MariaDB 失敗，注意MariaDB狀態--------######----------- "
#    sleep 20
#    #return
#fi


#/home/ubuntu/PETS/pets_hadoop
if [ -d "$WORKINGDIR/pets_hadoop/" ]; then
    #檔案 /path/to/dir/filename存在
    echo "$WORKINGDIR/pets_hadoop/ exists................"

    #--------20240906--1--------------#
    if [ -d "$WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/hiveMetaDB_postgre" ]; then
        echo "------$WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/hiveMetaDB_postgre exists....."
    else
        mkdir $WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/hiveMetaDB_postgre
        # /home/ubuntu/pedsa_s/pets_k/pets_v1/sourceCode/hadoop/hiveMetaDB_postgre
    fi

    if [ -d "$WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/MariaDBdata" ]; then
        echo "$WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/MariaDBdata exists....."
    else
        mkdir $WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/MariaDBdata
    fi  


    if [ -d "$WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/masterDirN" ]; then
        echo "$WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/masterDirN exists....."
    else
        mkdir $WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/masterDirN
    fi
    if [ -d "$WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/masterDirD" ]; then
        echo "$WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/masterDirD exists....."
    else
        mkdir $WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/masterDirD
    fi      
    if [ -d "$WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/data" ]; then
        echo "$WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/data exists....."
    else
        mkdir $WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/data
    fi 

    if [ -d "$WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/dataMac" ]; then
        echo "$WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/dataMac exists....."
    else
        mkdir $WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/dataMac
    fi

    if [ -d "$WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/final_project" ]; then
        echo "$WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/final_project exists....."
    else
        mkdir $WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/final_project
    fi

    if [ -f "$WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/hadoop-yarn-common-2.7.4.jar" ]; then
        echo "$WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/hadoop-yarn-common-2.7.4.jar exists....."
    else
        echo "$WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/hadoop-yarn-common-2.7.4.jar not exist....."
        
        echo "----------------停止啟動"
        return
    fi

    

    if [ -d "$WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/ssh_conf" ]; then
        echo "$WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/ssh_conf exists....."
        if [ -f "$WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/ssh_conf/config" ]; then
            echo "$WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/ssh_conf/config exists....."
        else
            cd $WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop
            source ./create_ssh_config.sh    
        fi    

    else
        mkdir $WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop/ssh_conf
        cd $WORKINGDIR/pets_hadoop/pets_v1/sourceCode/hadoop
        source ./create_ssh_config.sh  
    fi         

    #--------20240906--2-----masterDirN---------#



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

echo "finish data link(join) service  in $PWD/pets_hadoop/pets_v1...."
sleep 15

#如果兩個容器不在同一個 Docker Swarm 網路中，它們無法使用主機 IP 和外部連接埠直接相互通訊。####################
#####造成與DB同主機的服務連不上DB，但不同主機卻可以#####
#解法:  將MariaDB連上非overlay網路############
MariaDB_nrt_id=$(docker ps -aqf "name=MariaDB_nrt")

echo "get MariaDB id is  --- $MariaDB_nrt_id ..........."



val1L=${#MariaDB_nrt_id} #len=12
if [ $val1L == 12 ]; then
    echo "---------------------------------------將MariaDB連上hadoopnet_overlay網路--- "

    hadoopnet_overlay_id=$(docker network ls --filter name=hadoopnet_overlay --format "{{.ID}}")
    echo "----hadoopnet_overlay_id is ""$hadoopnet_overlay_id"
    docker network disconnect $hadoopnet_overlay_id $MariaDB_nrt_id >/dev/null 2>&1
    #MARIA_IP=168.17.8.253
    #MARIA_IP=MariaDB_nrtS
    #docker network connect --alias MariaDB_nrtS --ip $MARIA_IP hadoopnet_overlay $MariaDB_nrt_id  >/dev/null 2>&1
    #docker network connect  --ip $MARIA_IP hadoopnet_overlay $MariaDB_nrt_id >/dev/null 2>&1
    echo "-----docker network connect  --ip $MARIA_IP $hadoopnet_overlay_id $MariaDB_nrt_id----"
    docker network connect  --ip $MARIA_IP $hadoopnet_overlay_id $MariaDB_nrt_id
    ##############################################################################################
    #docker network connect  --ip 168.17.8.252 $hadoopnet_overlay_id $PET_join_Hadoop_nodemaster_id 
    ##############################################################################################
 
    if [ "$?" -eq "0" ]; then
       echo "MariaDB成功連上hadoopnet_overlay網路---(1)"
    else
       echo "MariaDB無法連上hadoopnet_overlay網路.再試一次"
       hadoopnet_overlay_id=$(docker network ls --filter name=hadoopnet_overlay --format "{{.ID}}")
       echo "----hadoopnet_overlay_id is ""$hadoopnet_overlay_id"
       #docker network disconnect $hadoopnet_overlay_id $MariaDB_nrt_id >/dev/null 2>&1

       #----------0219------------------1#
       docker rm -f my_MariaDB_nrt >/dev/null 2>&1

       docker run -d \
              --name my_MariaDB_nrt \
              -v ./MariaDBdata:/var/lib/mysql \
              -v ./key_db1.sql:/key_db1.sql \
              -v ./start_ssh1.sh:/start_ssh1.sh \
              -v ./initialDeIDServiceDBs_Tables.sh:/initialDeIDServiceDBs_Tables.sh \
            pets_mariadb:1.0
       echo "network connect hadoopnet_overlay  my_MariaDB_nrt"
       echo "--1------------------------------------"
       docker ps
       echo "--2------------------------------------"
       docker network connect hadoopnet_overlay  my_MariaDB_nrt 
       echo "--3------------------------------------"      
       

       #sleep 20
       ##############################################################################################################
       #docker network connect  --ip $MARIA_IP hadoopnet_overlay $MariaDB_nrt_id >/dev/null 2>&1
       docker network connect  --ip $MARIA_IP hadoopnet_overlay $MariaDB_nrt_id
       ###############################################################################################################
       if [ "$?" -ne "0" ]; then
           echo "MariaDB無法連上hadoopnet_overlay網路.檢查docker network，重新啟動"
           # docker rm -f my_MariaDB_nrt
           return
       else
           echo "MariaDB成功連上hadoopnet_overlay網路---(2)"
           sleep 5
       fi
       docker rm -f my_MariaDB_nrt
       #----------0219------------------1#


    fi
    #docker network connect --alias MariaDB_nrtSS  hadoopnet_overlay $MariaDB_nrt_id
else
	echo "MariaDB_nrt_id is------ "$MariaDB_nrt_id" ------"
    echo "----#######-----------MariaDB連上hadoopnet_overlay網路 失敗，須重啟--------######----------- "
    
    return
fi


#################################################################################
PET_join_Hadoop_nodemaster_id=$(docker ps -aqf "name=PET_join_Hadoop_nodemaster")
#################################################################################

val1L=${#PET_join_Hadoop_nodemaster_id} #len=12
if [ $val1L == 12 ]; then
    echo "---------------------------------------將PET_join_Hadoop_nodemaster連上hadoopnet_overlay網路--- "

    hadoopnet_overlay_id=$(docker network ls --filter name=hadoopnet_overlay --format "{{.ID}}")
    echo "----hadoopnet_overlay_id is ""$hadoopnet_overlay_id"
    docker network disconnect $hadoopnet_overlay_id $PET_join_Hadoop_nodemaster_id >/dev/null 2>&1
    #MARIA_IP=168.17.8.253
    #MARIA_IP=MariaDB_nrtS
    #docker network connect --alias MariaDB_nrtS --ip $MARIA_IP hadoopnet_overlay $MariaDB_nrt_id  >/dev/null 2>&1
    #docker network connect  --ip $MARIA_IP hadoopnet_overlay $MariaDB_nrt_id >/dev/null 2>&1
    #docker network connect  --ip $MARIA_IP $hadoopnet_overlay_id $MariaDB_nrt_id
    ##############################################################################################
    docker network connect  --ip 168.17.8.252 $hadoopnet_overlay_id $PET_join_Hadoop_nodemaster_id 
    ##############################################################################################
 
    if [ "$?" -eq "0" ]; then
       echo "PET_join_Hadoop_nodemaster成功連上hadoopnet_overlay網路  --- (1)"
    else
       echo "PET_join_Hadoop_nodemaster無法連上hadoopnet_overlay網路.再試一次"
       hadoopnet_overlay_id=$(docker network ls --filter name=hadoopnet_overlay --format "{{.ID}}")
       echo "----hadoopnet_overlay_id is ""$hadoopnet_overlay_id"
       #docker network disconnect $hadoopnet_overlay_id $PET_join_Hadoop_nodemaster_id >/dev/null 2>&1

       #----------0219------------------1#
       #docker run -d --name my_join_Hadoop_nodemasterJ hive_nonroot:ub2004_ch_term_sshpass_P36
       docker rm -f my_join_Hadoop_nodemasterJ >/dev/null 2>&1
       docker run -d \
          --name my_join_Hadoop_nodemasterJ \
          -v ./hive_conf:/home/hadoop/hive/conf \
          -v ./spark_conf:/home/hadoop/spark/conf \
          -v ./hadoop_conf:/home/hadoop/hadoop/etc/hadoop \
          -v ./masterCodeDir:/home/hadoop/proj_ \
          -v ./data:/home/hadoop/proj_/data \
          -v ./dataMac:/home/hadoop/proj_/dataMac \
          -v ./masterDirN:/home/hadoop/data/nameNode \
          -v ./masterDirD:/home/hadoop/data/dataNode \
          -v ./ssh_conf/config:/home/hadoop/.ssh/config \
          -v ./start_all.sh:/start_all.sh \
          -v ./start_hadoop.sh:/start_hadoop.sh \
          -v ./hadoop_bashrc:/home/hadoop/.bashrc \
          -v ./final_project:/home/hadoop/proj_/final_project \
          -v ./hadoop-yarn-common-2.7.4.jar:/home/hadoop/hadoop/share/hadoop/yarn/hadoop-yarn-common-2.7.4.jar \
          hive_nonroot:ub2004_ch_termP36 bash  /start_all.sh


       docker network connect hadoopnet_overlay  my_join_Hadoop_nodemasterJ  
       #sleep 10
       ##############################################################################################################
       docker network connect  --ip 168.17.8.252 hadoopnet_overlay $PET_join_Hadoop_nodemaster_id >/dev/null 2>&1
       ###############################################################################################################
       if [ "$?" -ne "0" ]; then
           echo "PET_join_Hadoop_nodemaster無法連上hadoopnet_overlay網路.重新啟動"
           docker rm -f my_join_Hadoop_nodemasterJ
           return
       else 
           echo "PET_join_Hadoop_nodemaster成功連上hadoopnet_overlay網路---(2)"
           sleep 5

       fi 
       docker rm -f my_join_Hadoop_nodemasterJ
       #----------0219------------------1#   	


    fi
    #docker network connect --alias MariaDB_nrtSS  hadoopnet_overlay $MariaDB_nrt_id
else
	echo "hadoopnet_overlay_id is------"$hadoopnet_overlay_id"------"
    echo "----#######-----------MariaDB連上hadoopnet_overlay網路 失敗，須重啟--------######----------- "
    sleep 20
    return
fi



################################################################################################
sleep 3




#/home/ubuntu/PETS/pets_k
if [ -d "$WORKINGDIR/pets_k/" ]; then
    #檔案 /path/to/dir/filename存在
    echo "$WORKINGDIR/pets_k/ exists................"

    #--------20240906--1--------------#
    if [ -d "$WORKINGDIR/pets_k/pets_v1/sourceCode/webService/deidweb_log" ]; then

        echo "$WORKINGDIR/pets_k/pets_v1/sourceCode/webService/deidweb_log exists....."
    else
        mkdir $WORKINGDIR/pets_k/pets_v1/sourceCode/webService/deidweb_log
    fi 
    if [ -d "$WORKINGDIR/pets_k/pets_v1/sourceCode/webService/APP__/log/webService" ]; then
        echo "$WORKINGDIR/pets_k/pets_v1/sourceCode/webService/APP__/log/webService exists....."
    else
        mkdir $WORKINGDIR/pets_k/pets_v1/sourceCode/webService/APP__/log/webService
    fi


    if [ -d "$WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop/hiveMetaDB_postgre" ]; then
        echo "$WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop/hiveMetaDB_postgre exists....."
    else
        mkdir $WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop/hiveMetaDB_postgre
    fi 

    if [ -d "$WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop/masterDirN" ]; then
        echo "$WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop/masterDirN exists....."
    else
        mkdir $WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop/masterDirN
    fi
    if [ -d "$WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop/masterDirD" ]; then
        echo "$WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop/masterDirD exists....."
    else
        mkdir $WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop/masterDirD
    fi  

    if [ -d "$WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop/data" ]; then
        echo "$WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop/data exists....."
    else
        mkdir $WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop/data
    fi
    if [ -d "$WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop/dataMac" ]; then
        echo "$WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop/dataMac exists....."
    else
        mkdir $WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop/dataMac
    fi 


    if [ -d "$WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop/ssh_conf" ]; then
        echo "$WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop/ssh_conf exists....."
        if [ -f "$WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop/ssh_conf/config" ]; then
            echo "$WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop/ssh_conf/config exists....."
        else
            cd $WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop
            source ./create_ssh_config.sh    
        fi    

    else
        mkdir $WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop/ssh_conf
        cd $WORKINGDIR/pets_k/pets_v1/sourceCode/hadoop
        source ./create_ssh_config.sh  
    fi                       


    #--------20240906--2--------------#

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




##pets_dp/ 20231221 add
#WORKINGDIR_DP_WEB=$WORKINGDIR/pets_dp/pets_dp/sourceCode/DP_webService
#export WORKINGDIR_DP_WEB
if [ -d "$WORKINGDIR/pets_dp/" ]; then
    #檔案 /path/to/dir/filename存在
    echo "$WORKINGDIR/pets_syn/ exists................"
    cd $WORKINGDIR/pets_dp/pets_dp/sourceCode/DP_webService
    echo "current path is $PWD...."
    echo "run docker stack rm  pets_dp ..."
    
    #docker-compose down
    docker stack rm  pets_dp
    sleep 5
    echo "run docker stack deploy  --with-registry-auth -c docker-compose.yml pets_dp ..."
    #docker-compose up -d
    docker stack deploy  --with-registry-auth -c docker-compose.yml pets_dp 


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


echo "finish deid_k service  in $PWD/pets_dp/pets_dp...."

sleep 5




#/home/ubuntu/PETS/pets_service
if [ -d "$WORKINGDIR/pets_service/" ]; then
    #檔案 /path/to/dir/filename存在
    echo "$WORKINGDIR/pets_service/ exists................"
    #/home/ubuntu/pedsa_s/pets_service/petsservice/log"
    if [ -d "$WORKINGDIR/pets_service/petsservice/log" ]; then
        echo "$WORKINGDIR/pets_service/petsservice/log exists....."
    else
        mkdir $WORKINGDIR/pets_service/petsservice/log
    fi 

    cd $WORKINGDIR/pets_service/petsservice
    echo "current path is $PWD...."
    echo "run docker stack rm  pets_service...."
    
    #docker-compose down
    docker stack rm  pets_service
    sleep 5
    echo "run docker stack deploy --with-registry-auth -c docker-compose.yaml pets_service...."
    #docker-compose up -d
    docker stack deploy --with-registry-auth -c docker-compose.yaml pets_service


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
    echo "run docker stack rm  pets_web...."
    
    #docker-compose down
    docker stack rm  pets_web
    sleep 5
    echo "run stack deploy --with-registry-auth -c docker-compose.yaml pets_web..."
    #docker-compose up -d
    docker stack deploy  --with-registry-auth -c docker-compose.yaml pets_web


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

    if [ -d "$WORKINGDIR/pets_syn/pets_syn/sourceCode/webService/syn_deidweb_log" ]; then
        echo "$WORKINGDIR/pets_syn/pets_syn/sourceCode/webService/syn_deidweb_log exists....."
    else
        mkdir $WORKINGDIR/pets_syn/pets_syn/sourceCode/webService/syn_deidweb_log
    fi 



    echo "run docker stack rm  pets_syn..."
    
    #docker-compose down
    docker stack rm  pets_syn
    sleep 5
    echo "run docker stack deploy --detach=false --with-registry-auth -c docker-compose.yml pets_syn..."
    #docker-compose up -d
    docker stack deploy --with-registry-auth -c docker-compose.yml pets_syn


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
