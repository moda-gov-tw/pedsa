#create folder for api
import os 
import pandas as pd
from logging_tester import _getLogger

def main(args): 

	_logger  =_getLogger('error__createFolder')

	projName = args['projName']

	folderForSynthetic = "folderForSynthetic"

	parent_project_path = "app/devp/"+folderForSynthetic+"/"
	print(parent_project_path)
	
	project_path = parent_project_path+projName+'/'

	inputRawdata_path = project_path+'inputRawdata'+'/'
	output_path = project_path+'output'+'/'
	synprocess_path = project_path+'synProcess'+'/'

	try:
		if not os.path.exists(parent_project_path):
			os.mkdir(parent_project_path)  
	except Exception as e:
		print("Non standard path. Error Create parent path folder!")
		_logger.debug('create folder fail: - %s:%s' %(type(e).__name__, e))
		return None

	try:
		if not os.path.exists(project_path):
			os.mkdir(project_path)
		if not os.path.exists(inputRawdata_path):
			os.mkdir(inputRawdata_path)

		if not os.path.exists(output_path):
			os.mkdir(output_path)

		if not os.path.exists(synprocess_path):
			os.mkdir(synprocess_path)
	except Exception as e:
		print("WRONT PROJECT NAME DEFINED!")
		_logger.debug('create folder fail: - %s:%s' %(type(e).__name__, e))
		return None

	'''
	try:
		if not os.path.exists(inputRawdata_path):
			os.mkdir(inputRawdata_path)

		if not os.path.exists(output_path):
			os.mkdir(output_path)

		if not os.path.exists(synprocess_path):
			os.mkdir(synprocess_path)
	except Exception as e:
		print("WRONT Result folder DEFINED!")
		_logger.debug('create folder fail: - %s:%s' %(type(e).__name__, e))
		return None
	'''
	print("citc____Mission Complete")


if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("-projName", "--projName", help='projName for make a folder')

	args = vars(parser.parse_args())
	print(args)
	print ("in __main__")
	main(args)