#!/usr/bin/python
# -*- coding: utf-8 -*-     

#from pyspark import SparkFiles
import subprocess
import io , sys




if __name__ == "__main__":

    tblName = sys.argv[1]

    path_ = "/home/hadoop/proj_/dataMac/input/" + tblName + ".csv"
    print("Input path: " + path_)

    try:

        #20200629, for cluster 
        subprocess.run(["scp", path_, "node2:"+path_])
        subprocess.run(["scp", path_, "node3:"+path_])

    except Exception as e:
        s = e.java_exception.toString()
        print(s)
        print("Is single node!!!!!!!!!!!!!")
        print("scp in udfMacUID fail!!!!!!!!!!!!!")







