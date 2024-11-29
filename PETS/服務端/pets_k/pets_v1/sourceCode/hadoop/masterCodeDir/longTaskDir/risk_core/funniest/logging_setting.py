import yaml
import logging
import logging.config
import time
from os import path, getcwd

log_setting_file =path.join("/home/hadoop/proj_/longTaskDir/log","logging_setting.yaml")

with open(log_setting_file, 'r') as f:
    config = yaml.load(f)
    todaytime = time.strftime("%Y%m%d")
    logDir = '/home/hadoop/proj_/longTaskDir/log/hadoop/'
    logFileName = 'hadoop_{}.log'.format(todaytime)
    config['handlers']['file']['filename'] = logDir+logFileName
    logging.config.dictConfig(config)
