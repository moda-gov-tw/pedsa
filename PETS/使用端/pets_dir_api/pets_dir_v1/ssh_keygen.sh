#!/bin/bash


#在服務端產生ssh key如下
#rm -f "$PWD/sftp_key.pem"
#rm -f "$PWD/sftp_key.pem.pub"

sleep 1
#echo ""|ssh-keygen -t rsa -b 2048 -f sftp_key.pem

chmod 600 "$PWD/sftp_key.pem"
chmod 644 "$PWD/sftp_key.pem.pub"
ls "$PWD"/sftp_key.*

whoami

ls -al ~/.ssh/authorized_keys

 

#cat "$PWD"/sftp_key.pem.pub >> ~/.ssh/authorized_keys
cat ~/.ssh/authorized_keys 
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys



# Read 安裝目錄
echo -n 輸入PEDSA 服務端的安裝目錄 "(例如/home/itri/AITMP):"
read  deploy_dir1
deploy_dir=$deploy_dir1
echo "目前目錄 為 "$PWD
echo "使用端的安裝目錄(deploy_dir) 為 $deploy_dir"
sleep 5

# Read 使用端的使用者名稱 
echo -n 輸入PEDSA 服務端的使用者名稱 "(例如 itri):"
read  node3_user1
node3_user=$node3_user1
echo "使用端的使用者名稱  為 "$node3_user
sleep 5

# Read 使用端的使用者密碼 
echo -n 輸入PEDSA 服務端的使用者密碼  "(例如 petspass):"
read  SSH_DATA1
SSH_DATA=$SSH_DATA1
#echo "P使用端的使用者密碼 為 "$SSH_DATA
sleep 5

#Read 使用端的IP 
echo -n 輸入PEDSA 服務端的IP "(例如 34.80.134.144):"
read  node3_ip1
node3_ip=$node3_ip1
echo "使用端的IP 為 "$node3_ip
sleep 5

#AITMP/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys/

SSH_DATA='petspass@'
echo "icl print- chmod 600 ${deploy_dir}/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys/sftp_key.pem"

sshpass -p ${SSH_DATA} scp -o StrictHostKeyChecking=no "$PWD/sftp_key.pem" "$PWD/sftp_key.pem.pub" "${node3_user}@${node3_ip}:${deploy_dir}/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys"  
return

echo "icl print - chmod 600 ${deploy_dir}/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys/sftp_key.pem"
sshpass -p $SSH_DATA ssh ${node3_user}@${node3_ip} "echo ${SSH_DATA}|sudo  -S chmod 600 ${deploy_dir}/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys/sftp_key.pem"
        
sshpass -p $SSH_DATA ssh ${node3_user}@${node3_ip} "echo ${SSH_DATA}|sudo  -S chmod 644 ${deploy_dir}/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys/sftp_key.pem.pub"

#將sftp_key.pem放進
#pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys/sftp_key.pem
#chmod 600 sftp_key.pem

#將sftp_key.pem.pub放進
#pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys/sftp_key.pem.pub
#chmod 600 sftp_key.pem.pub
