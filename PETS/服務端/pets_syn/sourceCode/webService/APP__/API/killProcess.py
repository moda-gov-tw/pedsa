#create folder for api
import os
import sys
import signal
from celery.task.control import revoke
import pandas as pd
from logging_tester import _getLogger
import argparse

def main(args): 

	_logger  =_getLogger('error__killProcess')


	PID = int(args['PID'])#TASK_ID
	# 不需要再檢查 userID 是否為數字，因為它已經是整數類型
	if not isinstance(PID, int) or PID <= 0:
		_logger.debug(f'{PID}__errTable:errTable: Invalid userID format')
		print(f"{PID}__errTable:Invalid userID format")
		return 'FAIL'
	
	try:
		
		#revoke(PID, terminate=True)
		a = os.kill(PID, signal.SIGKILL)
		# a = os.kill(pid, signal.9) # same as above
		# print ('kill pid %s' % (PID))

	except Exception as e:
		print("killProcess fail !")
		_logger.debug('killProcess fail: - %s:%s' %(type(e).__name__, e))
		return None


	print("citc____Mission Complete")


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-PID", "--PID",type=int, help='process PID wanted kill')
	args = vars(parser.parse_args())
	print ("in __main__")
	main(args)