#!/bin/bash

echo "in start_all.sh"
whoami
echo "before su"
#ls -al
#ls -al /start_hadoop.sh
#chown hadoop:hadoop /home/hadoop/hadoop/sbin/start-dfs.sh
chmod 777 /start_hadoop.sh

#citc, 20220215
#chmod 664 /home/hadoop/.ssh/config

#ls -al /home/hadoop/hadoop/sbin/start-dfs.sh
echo ">> Starting sshd ..."
mkdir /var/run/sshd
/usr/sbin/sshd  -D&

#citc mark  20220121 ########
#create  wirking dir and change owner, permission # citc, 20220121
val_cdpg_id = 8168
groupadd --gid ${val_cdpg_id} cdpg
usermod -g cdpg hadoop
if [ -d "/home/hadoop/data/nameNode" ]; then
    #檔案 /path/to/dir/filename存在
    echo "/home/hadoop/data/nameNode exists."
    chown -R hadoop:cdpg /home/hadoop/data/nameNode
else
    #檔案 /path/to/dir/filename 不存在
    echo "/home/hadoop/data/nameNode does not exists."
    exit 1
fi

if [ -d "/home/hadoop/data/dataNode" ]; then
    #檔案 /path/to/dir/filename存在
    echo "/home/hadoop/data/dataNode exists."
    chown -R hadoop:cdpg /home/hadoop/data/dataNode
else
    #檔案 /path/to/dir/filename 不存在
    echo "/home/hadoop/data/dataNode does not exists."
    exit 1
fi

#/home/hadoop/proj_/dataMac
if [ -d "/home/hadoop/proj_/dataMac" ]; then
    #檔案 /path/to/dir/filename存在
    echo "/home/hadoop/proj_/dataMac exists."
    chown -R hadoop:cdpg /home/hadoop/proj_/dataMac
    chmod -R 770 /home/hadoop/proj_/dataMac
else
    #檔案 /path/to/dir/filename 不存在
    echo "/home/hadoop/proj_/dataMac does not exists."
    exit 1
fi

#/home/hadoop/proj_/data
if [ -d "/home/hadoop/proj_/data" ]; then
    #檔案 /path/to/dir/filename存在
    echo "/home/hadoop/proj_/data exists."
    chown -R hadoop:cdpg /home/hadoop/proj_/data
    chmod -R 770 /home/hadoop/proj_/data
else
    #檔案 /path/to/dir/filename 不存在
    echo "/home/hadoop/proj_/data does not exists."
    exit 3
fi

#/home/hadoop/.ssh
if [ -d "/home/hadoop/.ssh" ]; then
    #檔案 /path/to/dir/filename存在
    echo "/home/hadoop/.ssh exists."
    chown -R hadoop:cdpg /home/hadoop/.ssh
    chmod -R 770 /home/hadoop/.ssh
    chmod -R 664 /home/hadoop/.ssh/config
    chmod -R 664 /home/hadoop/.ssh/authorized_keys
    chmod -R 600 /home/hadoop/.ssh/id_rsa
else
    #檔案 /path/to/dir/filename 不存在
    echo "/home/hadoop/.ssh does not exists."
    exit 4
fi 

#"/start_all.sh
if [ -f "/start_all.sh" ]; then
    #檔案 /path/to/dir/filename存在
    echo "/start_all.sh exists."
    chown -R hadoop:cdpg /start_all.sh
else
    #檔案 /path/to/dir/filename 不存在
    echo "/start_all.sh does not exists."
    exit 5
fi

#"/start_hadoop.sh
if [ -f "/start_hadoop.sh" ]; then
    #檔案 /path/to/dir/filename存在
    echo "/start_all.sh exists."
    chown -R hadoop:cdpg /start_hadoop.sh
else
    #檔案 /path/to/dir/filename 不存在
    echo "/start_hadoop.sh does not exists."
    exit 6
fi 

#/home/hadoop/hive/conf
if [ -d "/home/hadoop/hive/conf" ]; then
    #檔案 /path/to/dir/filename存在
    echo "/home/hadoop/hive/conf exists."
    chown -R hadoop:cdpg /home/hadoop/hive/conf
else
    #檔案 /path/to/dir/filename 不存在
    echo "/home/hadoop/hive/conf does not exists."
    exit 7
fi

#/home/hadoop/spark/conf
if [ -d "/home/hadoop/spark/conf" ]; then
    #檔案 /path/to/dir/filename存在
    echo "/home/hadoop/spark/conf exists."
    chown -R hadoop:cdpg /home/hadoop/spark/conf
else
    #檔案 /path/to/dir/filename 不存在
    echo "/home/hadoop/spark/conf does not exists."
    exit 8
fi

#/home/hadoop/hadoop/etc/hadoop
if [ -d "/home/hadoop/hadoop/etc/hadoop" ]; then
    #檔案 /path/to/dir/filename存在
    echo "/home/hadoop/hadoop/etc/hadoop exists."
    chown -R hadoop:cdpg /home/hadoop/hadoop/etc/hadoop
else
    #檔案 /path/to/dir/filename 不存在
    echo "/home/hadoop/hadoop/etc/hadoop does not exists."
    exit 9
fi

#/home/hadoop/proj_
if [ -d "/home/hadoop/proj_" ]; then
    #檔案 /path/to/dir/filename存在
    echo "/home/hadoop/proj_ exists."
    chown -R hadoop:cdpg /home/hadoop/proj_
else
    #檔案 /path/to/dir/filename 不存在
    echo "/home/hadoop/proj_ does not exists."
    exit 10
fi 

#/home/hadoop/.bashrc
if [ -f "/home/hadoop/.bashrc" ]; then
    #檔案 /path/to/dir/filename存在
    echo "/home/hadoop/.bashrc exists."
    chown -R hadoop:cdpg /home/hadoop/.bashrc
else
    #檔案 /path/to/dir/filename 不存在
    echo "/home/hadoop/.bashrc does not exists."
    exit 11
fi 

#/home/hadoop/proj_/dataConfig
if [ -d "/home/hadoop/proj_/dataConfig" ]; then
    #檔案 /path/to/dir/filename存在
    echo "/home/hadoop/proj_/dataConfig exists."
    chown -R hadoop:cdpg /home/hadoop/proj_/dataConfig
    chmod -R 770 /home/hadoop/proj_/dataConfig
else
    #檔案 /path/to/dir/filename 不存在
    echo "/home/hadoop/proj_/dataConfig does not exists."
    exit 12
fi

#/home/hadoop/proj_/data_bak
if [ -d "/home/hadoop/proj_/data_bak" ]; then
    #檔案 /path/to/dir/filename存在
    echo "/home/hadoop/proj_/data_bak exists."
    chown -R hadoop:cdpg /home/hadoop/proj_/data_bak
    chmod -R 770 /home/hadoop/proj_/data_bak
else
    #檔案 /path/to/dir/filename 不存在
    echo "/home/hadoop/proj_/data_bak does not exists."
    exit 13
fi


#/home/hadoop/proj_/dataConfig_bak
if [ -d "/home/hadoop/proj_/dataConfig_bak" ]; then
    #檔案 /path/to/dir/filename存在
    echo "/home/hadoop/proj_/dataConfig_bak exists."
    chown -R hadoop:cdpg /home/hadoop/proj_/dataConfig_bak
    chmod -R 770 /home/hadoop/proj_/dataConfig_bak
else
    #檔案 /path/to/dir/filename 不存在
    echo "/home/hadoop/proj_/dataConfig_bak does not exists."
    exit 14
fi

###### citc, mark 20220121 ##end#####


#citc. rm hadoop from sudo group
gpasswd -d hadoop sudo
#citc. add hadoop to sudo group
#usermod -aG sudo hadoop


su hadoop -c "/start_hadoop.sh"
#su hadoop -c "/home/hadoop/hadoop/sbin/start-dfs.sh"
echo "leave start_all.sh"
whoami
#su hadoop bash -c "service ssh start"



#sleep 5
#echo ">> Starting hdfs ..."
#su hadoop bash -c "start-dfs.sh"
#sleep 5
#echo ">> Starting yarn ..."
#su hadoop -c "start-yarn.sh"
