#!/bin/bash


#在服務端產生ssh key如下

#test="/home/itri/AITMP"
#ls -al $test/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys
#return 
rm -f "$PWD/sftp_key.pem"
rm -f "$PWD/sftp_key.pem.pub"

sleep 1
#echo ""|ssh-keygen -t rsa -b 2048 -f sftp_key.pem
ssh-keygen -t rsa -b 2048 -f sftp_key.pem -N ''

chmod 600 "$PWD/sftp_key.pem"
chmod 644 "$PWD/sftp_key.pem.pub"
ls "$PWD"/sftp_key.*

#whoami

#ls -al ~/.ssh/authorized_keys

if [ -f "$HOME/.ssh/authorized_keys" ]; then
    echo "$HOME/.ssh/authorized_keys "alread exist
else
    echo "$HOME/.ssh/authorized_keys "not exist
    return
    #echo "" >  ~/.ssh/authorized_keys
fi
#echo "" >  ~/.ssh/authorized_keys

 
echo "add pub key--- $PWD/sftp_key.pem.pub >> $HOME/.ssh/authorized_keys"
cat "$PWD"/sftp_key.pem.pub >> $HOME/.ssh/authorized_keys
cat ~/.ssh/authorized_keys 
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys



# Read 安裝目錄
#/home/ubuntu/mohw_188/PETS 則取 /home/ubuntu/mohw_188
echo "當pets_dir_v1的路徑為/home/itri-pedsa/deploy_PEDSA_mohw/pets_dir_v1 則安裝目錄取 /home/itri-pedsa/deploy_PEDSA_mohw"
echo -n 輸入PEDSA 使用端的安裝目錄 "(例如/home/itri-pedsa/deploy_PEDSA_mohw):"
read  deploy_dir1
deploy_dir=$deploy_dir1
echo "目前目錄 為 "$PWD
echo "使用端的安裝目錄(deploy_dir) 為 $deploy_dir"
sleep 5

# Read 使用端的使用者名稱 
echo -n 輸入PEDSA 使用端的使用者名稱 "(例如 itri-pedsa):"
read  node3_user1
node3_user=$node3_user1
echo "使用端的使用者名稱  為 "$node3_user
sleep 5

# Read 使用端的使用者密碼 
echo -n 輸入PEDSA 使用端的使用者密碼  "(例如 petspass):"
echo -n
echo -n 當使用端使用金鑰登入，直接按eneter
echo -n
read  -s SSH_DATA1
SSH_DATA=$SSH_DATA1
#echo "P使用端的使用者密碼 為 "$SSH_DATA
#sleep 1
echo "\n"
#Read 使用端的IP 
echo -n 輸入PEDSA 使用端的IP "(例如 140.96.81.222):"
read  node3_ip1
node3_ip=$node3_ip1
echo "使用端的IP 為 "$node3_ip
#sleep 1

#AITMP/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys/

#SSH_DATA='petspass@'

if [ -f "id_rsa_itri-pedsa.pem" ]; then

    #scp -i id_rsa_itri-pedsa.pem itri-pedsa@35.221.150.250:~/installOpenSSLSSH098P1_for_ubuntu2204.tar.gz .
    # ssh -i id_rsa_itri-pedsa.pem itri-pedsa@35.221.150.250 "ls -al ~"
    echo "icl print- chmod 600 ${deploy_dir}/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys/sftp_key.pem"

    ssh -i id_rsa_itri-pedsa.pem ${node3_user}@${node3_ip} "sudo chown -R  $(whoami):$(whoami) ${deploy_dir}/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys"
    #sleep 1

    scp -i id_rsa_itri-pedsa.pem -o StrictHostKeyChecking=no "$PWD/sftp_key.pem" "$PWD/sftp_key.pem.pub" "${node3_user}@${node3_ip}:${deploy_dir}/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys"  
    #return
    #sleep 1


    echo "icl print - chmod 600 ${deploy_dir}/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys/sftp_key.pem"
    ssh -i id_rsa_itri-pedsa.pem ${node3_user}@${node3_ip} "sudo  chmod 600 ${deploy_dir}/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys/sftp_key.pem"
    #sleep 1



    ssh -i id_rsa_itri-pedsa.pem ${node3_user}@${node3_ip} "sudo  chmod 644 ${deploy_dir}/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys/sftp_key.pem.pub"
    #sleep 1

    ssh -i id_rsa_itri-pedsa.pem ${node3_user}@${node3_ip} "sudo  ls -al $deploy_dir/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys"
    #ls -al $deploy_dir/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys


else


    echo "icl print- chmod 600 ${deploy_dir}/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys/sftp_key.pem"

    sshpass -p $SSH_DATA ssh ${node3_user}@${node3_ip} "echo ${SSH_DATA}|sudo  -S chown -R  $(whoami):$(whoami) ${deploy_dir}/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys"
    #sleep 1

    sshpass -p ${SSH_DATA} scp -o StrictHostKeyChecking=no "$PWD/sftp_key.pem" "$PWD/sftp_key.pem.pub" "${node3_user}@${node3_ip}:${deploy_dir}/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys"  
    #return
    #sleep 1


    echo "icl print - chmod 600 ${deploy_dir}/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys/sftp_key.pem"
    sshpass -p $SSH_DATA ssh ${node3_user}@${node3_ip} "echo ${SSH_DATA}|sudo  -S chmod 600 ${deploy_dir}/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys/sftp_key.pem"
    #sleep 1



    sshpass -p $SSH_DATA ssh ${node3_user}@${node3_ip} "echo ${SSH_DATA}|sudo  -S chmod 644 ${deploy_dir}/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys/sftp_key.pem.pub"
    #sleep 1

    sshpass -p $SSH_DATA ssh ${node3_user}@${node3_ip} "echo ${SSH_DATA}|sudo  -S ls -al $deploy_dir/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys"
    #ls -al $deploy_dir/pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys

fi




#將sftp_key.pem放進
#pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys/sftp_key.pem
#chmod 600 sftp_key.pem

#將sftp_key.pem.pub放進
#pets_dir_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/sftp_keys/sftp_key.pem.pub
#chmod 600 sftp_key.pem.pub
