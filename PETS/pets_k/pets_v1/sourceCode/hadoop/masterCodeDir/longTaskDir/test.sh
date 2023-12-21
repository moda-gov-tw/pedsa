#spark-submit --jars udfEncrypt_7.jar,myLogging_1.jar,mysql-connector-java-8.0.13.jar udfMacUID.py adult_id Bar12345Bar12345Bar12345Bar12345 "^|" 2 id workclass
#spark-submit --jars udfEncrypt_7.jar,myLogging_1.jar,mysql-connector-java-8.0.13.jar udfMacUID.py adult_id_new Bar12345Bar12345Bar12345Bar12345 "^|" 2 id workclass
spark-submit --jars udfEncrypt_7.jar,myLogging_1.jar,mysql-connector-java-8.0.13.jar udfMacUID.py testchh_org Bar12345Bar12345Bar12345Bar12345 "," 1 COUNTY
#testchh_org.csv
#docker exec -w /home/hadoop/proj_/longTaskDir -it -u hadoop nodemaster /bin/bash -c "source /home/hadoop/proj_/longTaskDir/test.sh"
