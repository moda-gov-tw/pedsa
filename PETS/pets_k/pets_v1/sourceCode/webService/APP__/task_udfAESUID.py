#!/usr/bin/python
# -*- coding: utf-8 -*-

from app import app
from app import celery
from flask_redis import FlaskRedis
import time
import re
from config.ssh_hdfs import ssh_hdfs
from log.logging_tester import _getLogger
from config.loginInfo import getConfig
import paramiko



from config.connect_sql import ConnectSQL

redis_store = FlaskRedis(app)

###itri, for Mac (start)###################### 
@celery.task(bind=True)
def aes_longTask(self, tblName,key, sep,columns_mac,projName,projID,dateHash,onlyHash,userId="1",userAccount="deidadmin"):
	# with app.app_context():

		# Set log.
	global _logger, _vlogger
	_logger=_getLogger('AESUID')
	_vlogger=_getLogger('verify__' + 'AESUID')
	print("################################################")
	ts0 = time.time()

	try:
		jarfiles = getConfig().getJarFiles()
		path = getConfig().getImportPath('local')
		#sparkCode = getConfig().getSparkCode('udfMacUID_new.py')
		sparkCode = getConfig().getSparkCode('udfAESUID_new.py')        


	   
		cmdStr='''
		spark-submit --jars {0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11}'''.format(jarfiles,
															  sparkCode,
															  '\"'+tblName+'\"',
															  '\"'+key+'\"',
															  '\"'+sep+'\"',
															  '\"'+columns_mac+'\"',
															  '\"'+projName+'\"',
															  '\"'+projID+'\"',
															  '\"'+dateHash+'\"',
															  '\"'+onlyHash+'\"',
                                                              '\"'+userId+'\"',
                                                              '\"'+userAccount+'\"'
															  )

		print(cmdStr)
		ssh_for_bash = ssh_hdfs()
		print(cmdStr)
		_logger.debug(cmdStr)
		stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=True)
		print(stdout)
		print(stderr)
	except Exception as e:
		print("************************************************")
		errMsg = 'ssh connect error: ' + str(e)
		print(errMsg)
		_logger.debug(errMsg)
		self.update_state(state="FAIL_CELERY", meta={'errMsg': errMsg})
		return

	if 0:
		lines = stdout.readlines()
		print(lines)
		print(stderr.readlines())


		for line in lines:
			print(line)

		outList = getSparkAppId_( lines)
		print(outList)
	else:
		##c. get spark ID, table name##########
		outList = getSparkAppId(self, stdout, False)
		print(outList)
		_logger.debug(outList)

	#self.update_state(self.request.id, state="PROGRESS", meta={'progress': 90})
	#time.sleep(1)

	if len(outList) < 2:
		#appID=app_ID
		appID="9999"
		outTblName="errTable"
	else:
		appID=outList[1]
		outTblName=outList[0]
	print(outTblName)
	print(len(outTblName))

	outTblName = outTblName[:-1]
	appID=appID[:-1]


	ts1 = time.time()
	print(ts1-ts0)
	##d. close ssh section##########
	return outList


def getColoumnsFromMysql(projName, tblOutput, conn):
	# query columns name
	colCompare = dict()

	sqlCommand = """
	SELECT pro_col_en,pro_col_cht
	FROM {0}.{1}
	WHERE pro_db='{2}'
	AND finaltblName='{3}'
	""".format('DeIdService', 'T_Project_SampleTable', projName, tblOutput)

	_logger.debug(sqlCommand)

	result = conn.doSqlCommand(sqlCommand)
	_logger.debug(result)

	if len(result['fetchall']) == 0:
		errMsg = 'Can not find finaltblName: {}'.format(tblOutput)
		_logger.debug(errMsg)
		return colCompare

	pro_col_en = [col.strip(' ') for col in result['fetchall'][0]['pro_col_en'].split(',')]
	pro_col_cht = [col.strip(' ') for col in result['fetchall'][0]['pro_col_cht'].split(',')]

	for i in range(len(pro_col_en)):
		colCompare[pro_col_en[i]] = pro_col_cht[i]
	_logger.debug(colCompare)
	return colCompare

def getSparkAppId(self, stdout_, viewSparkProcess_):
    app_ID=9999
    outList=[]
    print('in getSparkAppId')
    _logger.debug('in getSparkAppId')
    viewSparkProcess = viewSparkProcess_
    meta_={}# python dict
    self.update_state(state="PROGRESS", meta=meta_)
    while True:
        line = stdout_.readline()
        #print(line)
        #print("##########line#################")
        if line == '':
            break
        print(line)
		#sys.stdout.write(line)
		#sys.stdout.flush()

		#####20220301, citc add###########
		
        if "===end====" in  line:
            _logger.debug('success :' + line)
            print('success :' + line)
            #meta_['file_path'] = line
            path__index=line.find('/home/hadoop/proj_')
            path__=line[path__index:]
            meta_['out_path'] = path__

            outList.append(meta_['out_path'])
            self.update_state(state="ICL_END", meta=meta_)
			#break;
        #==AES_Enc end==
        if "==AES_Enc end==" in  line:
            _logger.debug('success :' + line)
            print('success :' + line)
            self.update_state(state="ICL_END", meta=meta_)
            break;			

		##20180103 add, citc add for error###########
        if "errTable_" in  line:
            kTable_index=line.find('errTable_')
            errReson_=line[kTable_index:]
            errReson_ = errReson_.strip('\n')
            _logger.debug('The errReson_ is ' + errReson_)
            print(errReson_)
            print('task id is '+self.request.id)
            #self.update_state(self.request.id, state="PROGRESS", meta={'progress': kTable_})
            meta_['errTable'] = errReson_
            #self.update_state( state="PROGRESS", meta={'progress': kTable_})
            outList.append(errReson_)
            break;


        if "sc.applicationId:" in  line:
            app_ID_index=line.find('application_')
            app_ID=line[app_ID_index:]
            #this gives the app_ID
            _logger.debug('The app ID (jobID) is ' + app_ID)
            print('The app ID (jobID) is ')
            print(app_ID)
            meta_['jobID'] = app_ID
#           self.update_state(state="PROGRESS", meta={'progress': app_ID})
            self.update_state(state="ICL_START", meta=meta_)
            outList.append(app_ID)
    print('#####meta_######')
    print(len(meta_))
    print(meta_)

#############################################################
	##20180103 add, citc add for error#############
    if(meta_.has_key('errTable')):
        #icl, modified 20220802
		#self.update_state(state="FAIL", meta=meta_)
        print('meta_.has_key(errTable)')
        print(meta_)
        self.update_state(state="FAIL_CELERY", meta=meta_)
    else:
		self.update_state(state="PROGRESS", meta=meta_)
	##20180103 add, citc add for error (end)###########

			
##(end, 2018/03/30)###################

#####################################################################

    return outList
