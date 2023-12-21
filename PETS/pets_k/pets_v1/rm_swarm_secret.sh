#!/bin/bash
##############################################
# parse_result: copy swarm secret to services#
##############################################
parse_result(){

  #local val_worker_service_ID=$1

  while read line; do    

    sec_time=$(echo $line | cut -d" " -f 4)
    echo "${sec_time}"
     
     sec_name=$(echo $line | cut -d" " -f 2)
     echo "${sec_name}"
     val1L=${#sec_name}
     echo "${val1L}"
                                           
     if [ $val1L == 8 ] && [[ $sec_name != *"7B3B2BcF"* ]] && [[ $sec_name != *"57Ef2ab1"* ]]; then
        docker secret rm $sec_name
        echo "-----${sec_name}----"

        

     fi

  done
}

parse_result < <(docker secret ls)

#parse_result $val_nodemaster_service < <(docker secret ls)


