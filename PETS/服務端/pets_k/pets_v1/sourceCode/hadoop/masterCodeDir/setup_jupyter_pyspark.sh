#!/bin/bash
NOTEBOOK_PORT=8888
# $SPARK_HOME/sbin/start-history-server.sh
export PATH=$SPARK_HOME/bin:/opt/conda/bin:$PATH
export PYTHONPATH=$PYTHONPATH:/opt/conda/lib/python3.7/site-packages
export PYTHONPATH=$PYTHONPATH:$SPARK_HOME/python

##for centos, PYTHONPATH=$PYTHONPATH:/opt/conda/lib/python3.7/site-packages
#export JAVA_HOME=/usr/lib/jvm/java-8-oracle
#export DERBY_HOME=/usr/lib/jvm/java-8-oracle/db 
#export SCALA_HOME=/usr/share/scala 
#export SBT_HOME=/usr/share/sbt-launcher-packaging

export PYSPARK_DRIVER_PYTHON=/opt/conda/bin/jupyter 
#export PYSPARK_DRIVER_PYTHON_OPTS="notebook --NotebookApp.open_browser=False --NotebookApp.ip='140.96.81.21' --NotebookApp.port=$NOTEBOOK_PORT"
export PYSPARK_DRIVER_PYTHON_OPTS="notebook --ip='*' --port=8999 --no-browser --allow-root --NotebookApp.token='ncku12345'"
#jupyter notebook --notebook-dir=/home/spark/code --ip='*' --port=8888 --no-browser
pyspark --jars /root/proj_/udfEncrypt_6.jar,/root/proj_/myLogging_1.jar,/root/proj_/mysql-connector-java-8.0.13.jar

