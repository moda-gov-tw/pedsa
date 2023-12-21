#!/bin/bash




parse_result(){

  local val_worker_service_ID=$1

  while read line; do    
     
     sec_name=$(echo $line | cut -d" " -f 2)
     echo "${sec_name}"
     val1L=${#sec_name}
     echo "${val1L}"
                                           
     if [ $val1L == 8 ] || [[ $sec_name == *"digestF_"* ]]; then
         retV=$(docker service update --secret-add $sec_name $val_worker_service_ID )
         retPID=$!
         wait retPID
         echo "$retPID is complete"
         if [[ $retV == *"have a conflicting "* ]]; then
             continue
         fi



     fi

  done
}

#input=test

# get worker service id
worker_service_id=$(docker service ls -qf name="CITCWebservice_worker")
val_worker_service_ID1=${worker_service_id:0:12}
val1L=${#val_worker_service_ID1}
if [ $val1L != 12 ]; then
    echo "get worker service id error"
    exit -1
fi
str="webservice_worker ID is $val_worker_service_ID1"
echo $str


# get nodemaster service id
nodemaster_service_id=$(docker service ls -qf name="CITCHadoop_nodemaster")
val_nodemaster_service_ID1=${nodemaster_service_id:0:12}
val1L=${#val_nodemaster_service_ID1}
if [ $val1L != 12 ]; then
    echo "get nodemaster service id error"
    exit -1
fi
str="CITCHadoop_nodemaster ID is $val_worker_service_ID1"
echo $str


parse_result $val_nodemaster_service_ID1 < <(docker secret ls)
