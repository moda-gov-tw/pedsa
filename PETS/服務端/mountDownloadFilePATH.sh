#!/bin/bash

#source ./mountDownloadFilePATH petspass@


## Read 安裝目錄
echo "當pedsa_s的路徑為/home/ubuntu/mohw_188/pedsa_s 則安裝目錄取 /home/ubuntu/mohw_188"
echo -n 輸入PEDSA安裝目錄 "(例如/home/ubuntu/mohw_188):"
read  deploy_dir1
deploy_dir=$deploy_dir1

echo "目前目錄 為 "$PWD
echo "PEDSA安裝目錄(deploy_dir) 為 "$deploy_dir
sleep 5
#SRC_DIR=PETS
#USER_=$USER

# Read Password
echo -n Host User Password:
read -s password
SUDO_PASSWD=$password
#echo "------passwd-$SUDO_PASSWD"
 

echo "mount 下載目錄 --"
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
    echo "------下載目錄 -$deploy_dir- 不存在, 啟動系統前須mount 下載目錄"

    return
    
fi 