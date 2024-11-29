#create folder for api
import os 
import pandas as pd
from os import listdir


from MyLib.connect_sql import ConnectSQL 

from logging_tester import _getLogger
import pymysql
from mysql_create_api import createDB_SynService, createTbl_T_ProjectGetFolder

def updateToMysql_sample(conn,userID,projID, projName, data):

	# insert to sample data
	condisionSampleData = {
			'project_id': projID,
			'pro_name': projName,
		}

	if type(data)==list: 
		valueSampleData = {
				'project_id': projID,
				'user_id':userID,
				'pro_name': projName,
				'csvdata': ','.join(data)
			}
	else: 
		valueSampleData = {
				'project_id': projID,
				'user_id':userID,
				'pro_name': projName,
				'csvdata': data
			}

	resultSampleData = conn.updateValueMysql('DpService',#'DeIdService',
												 'T_ProjectGetFolder',
												 condisionSampleData,
												 valueSampleData)
	if resultSampleData['result'] == 1:
		#_logger.debug("Update mysql succeed. {0}".format(resultSampleData['msg']))
		return None
	else:
		msg = resultSampleData['msg']
		#_logger.debug('insertSampleDataToMysql fail: ' + msg)
		return None

def find_csv_filenames( path_to_dir, suffix=".csv" ):
	filenames = listdir(path_to_dir)
	return [ filename for filename in filenames if filename.endswith( suffix ) ]

def main(args): 
	global  _logger,_vlogger, check_conn	 
	# debug log
	_logger  =_getLogger('error__getfolder')
	# verify log
	_vlogger =_getLogger('verify__getfolder')

	try:
		check_conn = ConnectSQL()
		_vlogger.debug("Connect SQL")

	except Exception as e:
		_logger.debug('connectToMysql fail: - %s:%s' %(type(e).__name__, e))
		return None
	#create DB AND table
	try :
		stepDict = {
			'0': createDB_SynService(check_conn),
			'1': createTbl_T_ProjectGetFolder(check_conn)
		}
		for i in range(len(stepDict)):
			# print(i)
			try:
				result = stepDict[str(i)]
				if result['result'] == 1:
					_vlogger.debug("createTbl")
					#_vlogger.debug(result['msg'])
				else:
					# print('mysql fail:' + result['msg'])
					#return False
			except:
				pass
	except Exception as e:
		_logger.debug('create DB fail: - %s:%s' %(type(e).__name__, e))
		return None

	projName = args['projName']
	userID = args['userID']
	projID = args['projID']

	user_upload_folder = "user_upload_folder"

	user_upload_folder_path = "app/devp/"+user_upload_folder+"/"
	# print(user_upload_folder_path)


	#check whether projName folder exist?
	user_csv_path = user_upload_folder_path+projName+'/'
	# print(user_csv_path)
	Flag = '1'
	try:
		if os.path.isdir(user_csv_path):
			#os.mkdir(user_csv_path ) 
			#list the csv file in the folder:
			filenames = find_csv_filenames(user_csv_path)
			# print(len(filenames))
			if len(filenames)==0:
				Flag = '-1'
				filenames = 'There is no CSV file in the folder.'
				_logger.debug('There is no CSV file in the folder.')

		else:
			Flag = '-1'
			filenames = 'Cannot find the folder named as same as projName.'
			_logger.debug('getfolder fail: - {0}'.format('Cannot find the folder named as same as projName.'))
			# print('Cannot find the folder named as same as projName.')
			# print('You have to put the csv files under the folder named as same as projName.')

	except Exception as e:
		# print('getfolder fail: - %s:%s' %(type(e).__name__, e))
		#_logger.debug('INsert fail: - %s:%s' %(type(e).__name__, e))
		return None

	
	try:
		updateToMysql_sample(check_conn,userID,projID, projName, filenames)
		
		_vlogger.debug('update mysql.')
		if type(filenames)==list: 
			#_vlogger.debug('fileNames____{0}'.format(','.join(filenames)))
			# print('fileNames____{0}'.format(','.join(filenames)))
			print('Flag____{0}'.format(str(Flag)))
		else:
			#print('NNNNNNNNNNNNNNNNNNNNNNNN')
			# print('fileNames____{0}'.format(str(filenames)))
			print('Flag____{0}'.format(str(Flag)))
	except Exception as e:
		_logger.debug('errTable: getfolder fail. {0}'.format(str(e)))
		return

	print("citc____Mission Complete")


if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("-projName", "--projName", help='projName for make a folder')
	parser.add_argument("-projID", "--projID", help='projID for mysql')
	parser.add_argument("-userID", "--userID", help='update user info to mysql')
	args = vars(parser.parse_args())
	# print(args)
	# print ("in __main__")
	main(args)
