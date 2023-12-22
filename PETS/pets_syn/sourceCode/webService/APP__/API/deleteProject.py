# -*- coding: utf-8 -*-
import os 
import pandas as pd
from logging_tester import _getLogger
import shutil

# 砍掉folderForSynthetic中的projName_/
def main(args): 
	#regist logger in API/logging_setting.yaml
	_logger  =_getLogger('error__deleteProject')

	projName = args['projName']

	folderForSynthetic = "folderForSynthetic"

	parent_project_path = "app/devp/"+folderForSynthetic+"/"
	print(parent_project_path)
	
	project_path = parent_project_path+projName+'/'

	# inputRawdata_path = project_path+'inputRawdata'+'/'
	# output_path = project_path+'output'+'/'
	# synprocess_path = project_path+'synProcess'+'/'


	try:
		if os.path.isdir(project_path):
			shutil.rmtree(project_path)
		else:
			_logger.debug('delete porject fail: - there is NOT a folder named as Project Name')
	except Exception as e:
		print("WRONT PROJECT NAME DEFINED!")
		_logger.debug('create folder fail: - %s:%s' %(type(e).__name__, e))
		return None

	print("citc____Mission Complete")


if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("-projName", "--projName", help='projName for make a folder')

	args = vars(parser.parse_args())
	print(args)
	print ("in __main__")
	main(args)