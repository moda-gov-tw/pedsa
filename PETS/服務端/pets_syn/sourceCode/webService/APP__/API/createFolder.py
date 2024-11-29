#create folder for api
import os 
import pandas as pd
from logging_tester import _getLogger
import re
import argparse

def main(args): 

	_logger  =_getLogger('error__createFolder')

	projName = args['projName'] #check
	if not re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", projName)or projName.isdigit()or '..' in projName or '/' in projName:
		_logger.debug(f'{projName}__errTable:Invalid projName format: - ' )
		print("Invalid projName format")  
		return 'FAIL'

	parent_project_path = os.path.join("app/devp/","folderForSynthetic")
	
	project_path = os.path.join(parent_project_path,projName)

	inputRawdata_path = os.path.join(project_path,'inputRawdata')
	output_path = os.path.join(project_path,'output')
	synprocess_path = os.path.join(project_path,'synProcess')

	try:
		if not os.path.exists(parent_project_path):
			os.mkdir(parent_project_path)  
	except Exception as e:
		print("Non standard path. Error Create parent path folder!")
		_logger.debug(f'{projName}__create folder fail: - %s:%s' %(type(e).__name__, e))
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
		_logger.debug(f'{projName}__create folder fail: - %s:%s' %(type(e).__name__, e))
		return None

	print("citc____Mission Complete")

def valid_path(value):
    if not re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", value)or value.isdigit()or '..' in value or '/' in value:
        raise argparse.ArgumentTypeError(f'Invalid path: {value}')
    return value

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-projName", "--projName",type=valid_path, help='projName for make a folder')
	args = vars(parser.parse_args())
	print ("in __main__")
	main(args)