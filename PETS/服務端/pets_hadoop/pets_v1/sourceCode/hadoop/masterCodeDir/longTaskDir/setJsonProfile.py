#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from pyspark.sql import SparkSession
from pyspark.sql.functions import col,length
from py4j.protocol import Py4JJavaError
from funniest import HiveLibs
from funniest.logging_tester import _getLogger
from MyLib.loginInfo import getLoginMysql
import pymysql
import subprocess
from MyLib.parseData import exportData, checkListQuotes
import os.path
import io , sys
import json

from MyLib.connect_sql import ConnectSQL
#20191210, addssss
from MyLib.updateAppStatus import updateAppStatus
from MyLib.updateAppStatus import updateAppProgress

#20200318, addssss
from MyLib.updateTProjectStatus import updateTProjectStatus

####################################################################################
#20190718, mark for logging error (ValueError: underlying buffer has been detached)

if "UTF-8" in sys.stdout.encoding:
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
###################################################################################



def main__(qi_col, after_col_value, gen_qi_settingvalue, pro_col_cht, tablekeycol, dataitem, datatype, isNull, csv_name, minKvalue):
 
    '''
    get key from mysql, 
    QueryKeyBySchool, get db name & table name from loging_mysql.txt
    dbname is tag
    '''
    global sc, sqlContext, hiveLibs, _logger,spark,updateAppStatus_,updateTProjectStatus_
    _logger=_getLogger('setJsonProfile')

    #20190717, citc add for FB log
    #fb_udfMacCols
    _logger_fb=_getLogger('verify__setJsonProfile')

    # log input
    _logger.debug('qi_col:%s',qi_col)
    _logger.debug('after_col_value:%s',after_col_value)
    _logger.debug('gen_qi_settingvalue:%s',gen_qi_settingvalue)
    _logger.debug('pro_col_cht:%s',pro_col_cht)
    _logger.debug('tablekeycol:%s',tablekeycol)
    _logger.debug('dataitem:%s',dataitem)
    _logger.debug('datatype:%s',datatype)
    _logger.debug('isNull:%s',isNull)
    _logger.debug('csv_name:%s',csv_name)
    _logger.debug('minKvalue:%s',minKvalue) #2021/07/27


    try:
        parameters = {}
        parameters["qi_col"] = qi_col
        parameters["after_col_value"] = after_col_value
        parameters["gen_qi_settingvalue"] = gen_qi_settingvalue
        parameters["pro_col_cht"] = pro_col_cht
        parameters["tablekeycol"] = tablekeycol
        parameters["dataitem"] = dataitem
        parameters["datatype"] = datatype
        parameters["isNull"] = isNull
        parameters["minKvalue"] = minKvalue #2021/07/27

        print("parameters:%s" %(parameters)) 

        json_str = json.dumps(parameters, indent=4)
        print("json_str:%s" %(json_str)) 
        _logger.debug('json_str:%s',json_str)

        path =  "/home/hadoop/proj_/dataConfig"
        output_path = path + "/" + csv_name + ".json"

        with open(output_path, 'w', encoding='UTF-8') as f:
            json.dump(parameters, f, ensure_ascii=False )

    except Py4JJavaError as e:
        s = e.java_exception.toString()
        _logger.debug(s)


if __name__ == "__main__":

    qi_col = sys.argv[1]
    after_col_value =  sys.argv[2]
    gen_qi_settingvalue = sys.argv[3] 
    pro_col_cht = sys.argv[4]
    tablekeycol =sys.argv[5]
    dataitem = sys.argv[6]  
    datatype = sys.argv[7] 
    isNull = sys.argv[8]
    csv_name = sys.argv[9]
    minKvalue = sys.argv[10] #2021/07/27
    # main__(tblName, key, colsNum, totalLen,columns_mac)
    main__(qi_col, after_col_value, gen_qi_settingvalue, pro_col_cht, tablekeycol, dataitem, datatype, isNull, csv_name, minKvalue)