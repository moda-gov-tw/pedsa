#!/bin/bash

# 檢查是否有提供兩個參數
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <type> <para>"
    echo "Valid type: docker, join, k, dp, syn"
    echo "Valid para: f/c, YYYYMMDD, YYYYMMDD, api/gan, api/gan/c"
    echo "--------------------------------------------------------"
fi

# 讀取參數
type=$1
para=$2

# 根據參數選擇對應的命令
case $type in
    join)
        echo "Tail log file  hadoop join /home/itri-pedsa/deploy_PEDSA/pedsa_s/pets_hadoop/pets_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/log/hadoop"
        tail -f /home/itri-pedsa/deploy_PEDSA/pedsa_s/pets_hadoop/pets_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/log/hadoop/hadoop_$para.log
	;;
      
        
    k)
        echo "Tail log file  hadoop join /home/itri-pedsa/deploy_PEDSA/pedsa_s/pets_k/pets_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/log/hadoop"
        tail -f /home/itri-pedsa/deploy_PEDSA/pedsa_s/pets_k/pets_v1/sourceCode/hadoop/masterCodeDir/longTaskDir/log/hadoop/hadoop_$para.log
        ;;
       
        
    docker)
        case $para in
            f)
                echo "docker logs fastapi"
                docker service logs -f pets_service_fastapi
		;;
            c)
                echo "docker logs cerely"
                docker service logs -f pets_service_celery
        	;;
	esac
	;;
    syn)
        case $para in
            api)
                echo "Tail log file  hadoop syn api /home/itri-pedsa/deploy_PEDSA/pedsa_s/pets_syn/pets_syn/sourceCode/webService/APP__/log/API.log"
                tail -f /home/itri-pedsa/deploy_PEDSA/pedsa_s/pets_syn/pets_syn/sourceCode/webService/APP__/log/API.log
            	;;
	    gan)
                echo "Tail log file  hadoop syn gan /home/itri-pedsa/deploy_PEDSA/pedsa_s/pets_syn/pets_syn/sourceCode/webService/APP__/log/GAN.log"
                tail -f /home/itri-pedsa/deploy_PEDSA/pedsa_s/pets_syn/pets_syn/sourceCode/webService/APP__/log/GAN.log
        	;;
        c)
                echo "Tail log file  hadoop syn gan /home/itri-pedsa/deploy_PEDSA/pedsa_s/pets_syn/pets_syn/sourceCode/webService/APP__/log/celery_log.txt"
                tail -f /home/itri-pedsa/deploy_PEDSA/pedsa_s/pets_syn/pets_syn/sourceCode/webService/APP__/log/celery_log.txt
            ;;
	esac
	;;
    dp)
        case $para in
            api)
                echo "Tail log file  hadoop dp api /home/itri-pedsa/deploy_PEDSA/pedsa_s/pets_dp/pets_dp/sourceCode/DP_webService/APP__/log/API.log"
                tail -f /home/itri-pedsa/deploy_PEDSA/pedsa_s/pets_dp/pets_dp/sourceCode/DP_webService/APP__/log/API.log
            	;;
	    gan)
                echo "Tail log file  hadoop dp gan /home/itri-pedsa/deploy_PEDSA/pedsa_s/pets_dp/pets_dp/sourceCode/DP_webService/APP__/log/GAN.log"
                tail -f /home/itri-pedsa/deploy_PEDSA/pedsa_s/pets_dp/pets_dp/sourceCode/DP_webService/APP__/log/GAN.log
        	;;
	esac
	;;
esac
