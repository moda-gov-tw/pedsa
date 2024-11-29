import logging
from . import logging_setting

def  _getLogger(name):
	return logging.getLogger(name)
	


if __name__ == '__main__':
    # logging.debug('This is a debug')
    # logging.info('This is an info')
    # logging.warning('This is an warning')
    # logging.error('This is an error')
    # logging.critical('This is an critical')

    # logger = logging.getLogger()
    # logger.debug('This is a debug')
    # logger.info('This is an info')
    # logger.warning('This is an warning')
    # logger.error('This is an error')
    # logger.critical('This is an critical')

    logger_mylog = logging.getLogger('mymodule.myclass')
    logger_mylog.debug('This is a debug')
    logger_mylog.info('This is an info')
    logger_mylog.warning('This is an warning')
    logger_mylog.error('This is an error')
    logger_mylog.critical('This is an critical') 
