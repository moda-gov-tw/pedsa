# -*- coding: utf-8 -*-
import os 
import pandas as pd
from logging_tester import _getLogger
import shutil
import re
import argparse

# 砍掉folderForSynthetic中的projName_/
def main(args): 
	#regist logger in API/logging_setting.yaml
	_logger  =_getLogger('error__deleteProject')

	projName = args['projName']
	if not re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", value)or value.isdigit()or '..' in value or '/' in value:
			_logger.debug(f'{projName}__Invalid projName format: - ' )
			print(f"{projName}__Invalid projName format")  
			return 'FAIL'
	
	parent_project_path = os.path.join("app/devp/","folderForSynthetic")
	print(parent_project_path)
	
	project_path = os.path.join(parent_project_path,projName)

	try:
		if os.path.isdir(project_path):
			shutil.rmtree(project_path)
		else:
			_logger.debug(f'{projName}__delete porject fail: - there is NOT a folder named as Project Name')
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