#create folder for api
import os
import sys
import signal
from celery.task.control import revoke
import pandas as pd
from logging_tester import _getLogger

def main(args): 

	_logger  =_getLogger('error__killProcess')

	#PID = args['PID']#TASK_ID
	PID = int(args['PID'])#TASK_ID

	try:
		
		#revoke(PID, terminate=True)
		a = os.kill(PID, signal.SIGKILL)
		# a = os.kill(pid, signal.9) # same as above
		print ('kill pid %s' % (PID))

	except Exception as e:
		print("WRONT !")
		_logger.debug('killProcess fail: - %s:%s' %(type(e).__name__, e))
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
	parser.add_argument("-PID", "--PID", help='process PID wanted kill')

	args = vars(parser.parse_args())
	print(args)
	print ("in __main__")
	main(args)