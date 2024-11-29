#!/bin/bash

#source ./test_shell_script_command_forGCP.sh 


# Read GCP 外部IP
echo -n 主機IP"(例如34.81.71.21):"
read  GCP_IP1
GCP_IP=$GCP_IP1


# Read 安裝目錄
echo -n 輸入PEDSA安裝目錄 "(例如/home/ubuntu/mohw0724):"
read  deploy_dir1
deploy_dir=$deploy_dir1

echo "目前目錄 為 "$PWD
echo "PEDSA安裝目錄(deploy_dir) 為 "$deploy_dir
sleep 5

echo "目前目錄 為 "$PWD
echo "主機IP 為 "$GCP_IP
sleep 5
 
 # Read Password
echo -n Host User Password:
read -s password

# source test_shell_script_command.sh citcw200@
#SUDO_PASSWD=$1
SUDO_PASSWD=$password

 
echo "(1) user password is " #$SUDO_PASSWD

sleep 5

#return
#ASSIGNED_USER=$USER
#echo "(1) HOST_USER is "$USER", for docker.service"

#hostname -I 
#ressult:
#       140.96.178.108 172.18.0.1 192.168.176.1 192.168.128.1 192.168.224.1 192.168.208.1 172.17.0.1 172.30.0.1 192.168.240.1 172.28.0.1 192.168.16.1 172.19.0.1
#-f1 : get first item (i.e. 140.96.178.108 )
#HOST_IP=$(hostname -I | cut -d" " -f1)

echo "(2) host IP is "$GCP_IP

echo "(3) working dir is "$PWD
sleep 5




###stop docker service 
string=$( docker -v )
if [[ $string == "Docker version"* ]]; then
  echo "docker alread exist, stop docker service: "$string
  echo $SUDO_PASSWD|sudo -S systemctl stop docker.socket
  #echo "1"
  echo $SUDO_PASSWD|sudo -S systemctl stop containerd
  #echo "2"
  echo $SUDO_PASSWD|sudo -S systemctl stop docker
  #echo "3"


fi

echo "(4) 進入 docker 複製docker相關檔案--"
cd docker

#chmod 755 icl_0414.txt
#echo $SUDO_PASSWD|sudo -S cp icl_0414.txt /usr/bin/
#chmod 755 containerd containerd-shim containerd-shim-runc-v2 ctr docker dockerd docker-init docker-proxy runc
chmod 755 containerd  containerd-shim-runc-v2  ctr  docker  dockerd  docker-init  docker-proxy  runc
#echo $SUDO_PASSWD|sudo -S cp containerd containerd-shim containerd-shim-runc-v2 ctr docker dockerd docker-init docker-proxy runc /usr/bin/
echo $SUDO_PASSWD|sudo -S cp containerd  containerd-shim-runc-v2  ctr  docker  dockerd  docker-init  docker-proxy  runc /usr/bin/


echo "------expected docker version 26"
docker -v
sleep 5

echo "(5) 修改docker設定及 /lib/systemd/system/docker.service--"
echo $SUDO_PASSWD|sudo -S groupadd docker


if [ -d "/home/$USER/docker_root/" ]; then
    echo "/home/$USER/docker_root/ "alread exist
else
    echo $SUDO_PASSWD|sudo -S mkdir "/home/$USER/docker_root"
fi

#回dockerd-src
cd ..
chmod 755 docker-compose
echo $SUDO_PASSWD|sudo -S cp docker-compose /usr/bin/
echo $SUDO_PASSWD|sudo -S cp containerd.service docker.service docker.socket /lib/systemd/system
echo "--expected dir is docherd-src, working dir is "$PWD
sleep 5

#ExecStart=/usr/bin/dockerd -H unix:///var/run/docker.sock -H tcp://0.0.0.0:2376 --data-root /home/ubuntu/docker_root --bip 169.17.0.1/24
#echo $SUDO_PASSWD|sudo -S sed -i "s/ExecStart=.*/ExecStart=\/usr\/bin\/dockerd -H unix:\/\/\/var\/run\/docker.sock -H tcp:\/\/0.0.0.0:2376 --data-root \/home\/$USER\/docker_root --bip 169.17.0.1\/24/g" /lib/systemd/system/docker.service
#OK
echo $SUDO_PASSWD|sudo -S sed -i "s/ExecStart=.*/ExecStart=\/usr\/bin\/dockerd -H unix:\/\/\/var\/run\/docker.sock -H tcp:\/\/0.0.0.0:2376 --data-root \/home\/$USER\/docker_root --bip 169.171.0.1\/24/g" /lib/systemd/system/docker.service
echo $SUDO_PASSWD|sudo -S usermod -aG docker $USER



echo "--expected: ExecStart=/usr/bin/dockerd -H unix:/var/run/docker.sock -H tcp://0.0.0.0:2376 --data-root /home/$USER/docker_root --bip 169.171.0.1\/24"
cat /lib/systemd/system/docker.service | grep ExecStart=

#su $USER
sleep 5


#when openssl form version 1 to version 3, then "sudo cp  /etc/ssl/openssl.cnf /usr/local/ssl"
echo "(6) docker TLS 憑證設定設定 --"

#2. cd docerd-authrization-plugin/opssl_CA_2023 (/home/jeremyho/dockerd-src/opssl_CA_2023)
#3. source ./makeDaemon.sh 10.140.0.10 pets_trainCERT (password: iclw200@)， 10.140.0.10為安裝的主機IP位址
#4. 進入資料夾 cd pets_trainCERT 
#5. sudo su
#6. 新建資料夾 mkdir /etc/docker/ssl
#7. 將原本的CA憑證與KEY匯入 docker ssl
#8. cp ../ca.pem server-cert.pem server-key.pem /etc/docker/ssl
cd opssl_CA_2023

#DIR_POSTFIX=$(echo $HOST_IP | cut -d"." -f4) #GCP_IP
DIR_POSTFIX=$(echo $GCP_IP | cut -d"." -f4)
echo "docker TLS cert dir is "pets_trainCERT$DIR_POSTFIX
sleep 5

#source ./makeDaemon.sh $HOST_IP pets_trainCERT$DIR_POSTFIX
source ./makeDaemon.sh $GCP_IP pets_trainCERT$DIR_POSTFIX

if [ -d "/etc/docker" ]; then
    echo "------/etc/docker exit"

else
    #檔案 /path/to/dir/filename 不存在
    echo "------mske \/etc\/docker"
    echo $SUDO_PASSWD|sudo -S mkdir /etc/docker
fi

##for the error: Can't open "/usr/local/ssl/openssl.cnf" for reading, No such file or directory
#由openssl 3.0.2 到 3.1.2會出錯
#ln -s /etc/ssl /usr/local/ssl
if [ -d "/usr/local/ssl" ]; then
    echo "------/usr/local/ssl exit"

else
    #檔案 /path/to/dir/filename 不存在
    echo "------ln -s /etc/ssl /usr/local/ssl"
    echo "for the error: Can't open \"/usr/local/ssl/openssl.cnf\""
    echo $SUDO_PASSWD|sudo -S ln -s /etc/ssl /usr/local/ssl
fi


echo $SUDO_PASSWD|sudo -S cp daemon.json /etc/docker/


if [ -d "/etc/docker/ssl" ]; then
    echo "------/etc/docker/ssl 存在"

else
    #檔案 /path/to/dir/filename 不存在
    echo "------make \/etc\/docker\/ssl"
    echo $SUDO_PASSWD|sudo -S mkdir /etc/docker/ssl
fi

echo $SUDO_PASSWD|sudo -S cp ./ca.pem pets_trainCERT$DIR_POSTFIX/server-cert.pem pets_trainCERT$DIR_POSTFIX/server-key.pem /etc/docker/ssl

#回dockerd-src
cd ..



echo "(7) 重啟docker 服務 --"

echo $SUDO_PASSWD|sudo -S systemctl daemon-reload
echo $SUDO_PASSWD|sudo -S systemctl start docker
#echo $SUDO_PASSWD|sudo systemctl status docker


retSring=$(echo $SUDO_PASSWD|sudo docker ps)
#$?變數保存上一個指令的退出狀態碼，
#$?的值為0 (對)；錯誤非零值 (錯誤)  可以根據這個值來判斷指令是否成功執行
if [ $? -ne 0 ]; then
    echo "---------------docker ps----------------執行失败"
    echo "退出目前terminal，重新開啟新terminal，重新執行一次"
    return 
fi


echo "(8) 建立docker network --"
HADOOPNET_OVERLAY=$(echo $SUDO_PASSWD|sudo docker network ls --filter name=hadoopnet_overlay)
val1L=${#HADOOPNET_OVERLAY}
#privacy@52-0A40394-31:~/20240403_188_PETS/new_images$ docker network ls --filter name=hadoopnet_overlay1
#NETWORK ID   NAME      DRIVER    SCOPE (length=38)
if [ $val1L == 38 ]; then
    echo "---create docker network hadoopnet_overlay--- "
    echo $SUDO_PASSWD|sudo -S docker swarm init
    echo $SUDO_PASSWD|sudo -S docker network create -d overlay --scope=global --subnet=168.17.8.0/24 --gateway=168.17.8.1 --attachable=true hadoopnet_overlay
else
    echo "---docker network hadoopnet_overlay exist--- "
    #return
fi

HADOOPNET_OVERLAY=$(echo $SUDO_PASSWD|sudo -S docker network ls --filter name=hadoopnet_pet_overlay)
val1L=${#HADOOPNET_OVERLAY}
#privacy@52-0A40394-31:~/20240403_188_PETS/new_images$ docker network ls --filter name=hadoopnet_pet_overlay
#NETWORK ID   NAME      DRIVER    SCOPE (length=38)
if [ $val1L == 38 ]; then
    echo "---create docker network hadoopnet_pet_overlay--- "
    echo $SUDO_PASSWD|sudo -S docker network create -d overlay --scope=global --subnet=168.38.8.0/24 --gateway=168.38.8.1 --attachable=true hadoopnet_pet_overlay
else
    echo "---docker network hadoopnet_pet_overlay exist--- "
    #return
fi

HADOOPNET_OVERLAY=$(echo $SUDO_PASSWD|sudo -S docker network ls --filter name=hadoopnet_web_overlay)
val1L=${#HADOOPNET_OVERLAY}
#privacy@52-0A40394-31:~/20240403_188_PETS/new_images$ docker network ls --filter name=hadoopnet_pet_overlay
#NETWORK ID   NAME      DRIVER    SCOPE (length=38)
if [ $val1L == 38 ]; then
    echo "---create docker network hadoopnet_web_overlay--- "
    echo $SUDO_PASSWD|sudo -S docker network create -d overlay --scope=global --subnet=168.138.8.0/24 --gateway=168.138.8.1 --attachable=true hadoopnet_web_overlay
else
    echo "---docker network hadoopnet_web_overlay exist--- "
    #return
fi

#HADOOPNET=$(docker network ls --filter name=hadoopnet)
#val1L=${#HADOOPNET}
#docker network ls --filter name=hadoopnet
##NETWORK ID   NAME      DRIVER    SCOPE (length=38)
#if [ $val1L == 38 ]; then
#    echo "---create docker network hadoopnet--- "
#    #docker network create --subnet=172.26.1.0/24   --gateway=172.26.1.1 hadoopnet
#    echo $SUDO_PASSWD|sudo docker network create --subnet=168.68.8.0/24   --gateway=168.68.8.1 hadoopnet
#else
#    echo "---docker network hadoopnet_web_overlay exist--- "
#    #return
#fi


echo "(8) mount 下載目錄 --"
if [ -d "$deploy_dir/pedsa_s/pets_hadoop/pets_v1/sourceCode/hadoop/final_project/" ]; then
    echo "下載目錄 -- exists. mount /haddop/final_project directory to pets_web/download_folder"
    echo $SUDO_PASSWD|sudo mount --bind "$deploy_dir/pedsa_s/pets_hadoop/pets_v1/sourceCode/hadoop/final_project/k/input" "$deploy_dir/pedsa_s/pets_web/download_folder/enc/k"
    echo $SUDO_PASSWD|sudo mount --bind "$deploy_dir/pedsa_s/pets_hadoop/pets_v1/sourceCode/hadoop/final_project/k/output" "$deploy_dir/pedsa_s/pets_web/download_folder/dec/k"
    echo $SUDO_PASSWD|sudo mount --bind "$deploy_dir/pedsa_s/pets_hadoop/pets_v1/sourceCode/hadoop/final_project/syn/output" "$deploy_dir/pedsa_s/pets_web/download_folder/enc/syn"
    echo $SUDO_PASSWD|sudo mount --bind "$deploy_dir/pedsa_s/pets_hadoop/pets_v1/sourceCode/hadoop/final_project/dp/output" "$deploy_dir/pedsa_s/pets_web/download_folder/enc/dp"
                                                                                                                #/app/download_folder/dec/k/demo0530_single
else
    #檔案 /path/to/dir/filename 不存在
    echo ""
    echo "------下載目錄 -$deploy_dir- 不存在"
    echo "------開啟新的terminal， mount 下載目錄， 再安裝pedsa系統前須mount 下載目錄"

    return
    
fi  

echo "------expected docker version 20"
docker version

systemctl status docker
