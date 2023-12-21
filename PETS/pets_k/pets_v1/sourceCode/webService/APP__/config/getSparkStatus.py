
from ssh_hdfs import ssh_hdfs
import json

class checkSparkStatus:
    def __init__(self):
	    print('-----getSparkStatus')

    def nodeStatus(self):
        ssh_getNodeStatus = ssh_hdfs()
        
        cmdStr = 'python /home/hadoop/proj_/longTaskDir/getSparkStausInfo.py'
        #cmdStr = '/home/hadoop/bin/yarn node -list -all'
        print("cmdStr=%s"%cmdStr)
        ssh_get_tables = ssh_hdfs()
        stdin_, stdout_, stderr_ = ssh_get_tables.callCommand_output(cmdStr)
        #stdin_, stdout_, stderr_ = checkSparkStatus_.nodeStatus()
        
        line = stdout_.readlines()
        
        print("000000000000000000000000")
        print(line)

        print(line[-1])
        line_replace = line[-1].replace('\'','\"')
        print(line_replace)
        print("000000000000000000000000")
        
        try:
        	#20191209, json need '\"'
            line_replace = line[-1].replace('\'','\"')
            meta_ = dict()
            meta_ = json.loads(line_replace)

            #print(meta_)
            #{'Health-Report': '1/1 local-dirs are bad', 'Node-State': 'UNHEALTHY', 'Node-Id': 'nodemaster:8050'}
            print("meta_['Node-Id']=%s"%meta_['Node-Id'])
            print("meta_['Node-Stated']=%s"%meta_['Node-State'])
            print("meta_['Health-Report']=%s"%meta_['Health-Report'])
            return meta_
        except Exception as e:
            errMsg = 'checkSparkStatus.nodeStatus: ' + str(e)
            print(errMsg)
            #self.update_state(state="FAIL_CELERY", meta={'errMsg': errMsg})
            return 

    #def nappStatus(self):            



       