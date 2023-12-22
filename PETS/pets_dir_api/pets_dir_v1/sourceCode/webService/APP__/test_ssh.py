#!/usr/bin/python
# -*- coding: utf-8 -*-

from config.loginInfo import getConfig
from config.ssh_hdfs import ssh_hdfs
import os



def main():


    # Connect mysql
    try:
        #combine commands
        #serverPath = "/user/itribd/import"
        #serverPath = "hdfs://Aquila-nn2.citc.local/user/gau/import"

        projName = "aaa"


        type_ = 'local'
        serverPath = getConfig().getImportPath(type_)
        filePath = os.path.join(serverPath, projName, '*/*')
        if type_ == 'hdfs':
            cmdStr = 'hadoop fs -stat "%n" ' + filePath
        else:
            cmdStr = 'stat --format "%n" ' + filePath
        print('++100++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(cmdStr)
        print(filePath)
        print('++100++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

        ssh_for_bash = ssh_hdfs()
        stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=False)
        print('+++++stdout+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(stdout)
        print('+++++end+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')


    except Exception as e:
        errMsg = 'ssh_connect_error: ' + str(e)
        print('+++++errMsg+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        
        print(errMsg)
        print('+++++errMsg+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

        return 

if __name__ == "__main__":
    main()

