import yaml
import logging
import logging.config

from os import path, getcwd
import os
#print (os.path.dirname(__file__))
#log_setting_file =path.relpath( "logging_setting.yaml")
log_setting_file =path.join( getcwd(),"app/devp/syn_gen","logging_setting.yaml")
#log_setting_file ="/workspace/logging_setting.yaml"
#log_setting_file =path.join( getcwd(),"longTaskDir","logging_setting.yaml")
with open(log_setting_file, 'r') as f:
    config = yaml.load(f)
    logging.config.dictConfig(config)

