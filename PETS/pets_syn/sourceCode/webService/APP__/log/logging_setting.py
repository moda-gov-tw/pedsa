import yaml
import logging
import logging.config

from os import path, getcwd
#print os.path.dirname(__file__)
#log_setting_file =path.relpath( "logging_setting.yaml")
log_setting_file =path.join( "/app","app","devp","log","logging_setting.yaml")

with open(log_setting_file, 'r') as f:
    print("THE cODE IN log/")
    config = yaml.load(f)
    logging.config.dictConfig(config)
