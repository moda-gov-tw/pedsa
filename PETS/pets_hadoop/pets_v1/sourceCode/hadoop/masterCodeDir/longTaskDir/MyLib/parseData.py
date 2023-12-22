#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import path
import subprocess


def doCommand(hdfsCmdList):
    hdfsCommand = subprocess.Popen(hdfsCmdList,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    errLines = hdfsCommand.stderr.readlines()

    msg = list()
    for line in errLines:
        if line.decode('utf-8') is not None:
            msg.append(str(line))

    return ','.join(msg)


def exportToHdfs(df, path_):
    df.write.format('com.databricks.spark.csv')\
            .mode('overwrite')\
            .option("header", "false")\
            .option("quoteAll", "true")\
            .save(path_)

#2023/11/21 05:34:42 - export - DEBUG - Check config file exist condition: 
#{'pro_db': '30k_test132', 'finaltblName': 'g_mac_sample2000_demo_k_job1'}

def exportData(dbName, dfDF, headers, tblName, path_):
    '''
    Export data to csv in local
    :param dbName: str, database name (project name)
    :param dfDF: Dataframe, body of df
    :param headers: list, header of df
    :param tblName: str, name of df which need to be exported.
    :param path_: str, path of output df
    :return: dict, if succeed, return {'msg': stdout, 'result': 1}, otherwise return {'msg': stderr, 'result': 0}
    '''

    try:
        from pyspark.sql import SparkSession

        returnMsg = list()

        # step 1: Create folder
        # outputPath = path.join('output', dbName, tblName)
        outputPath = path.join('output', dbName)


        result = doCommand(['hadoop', 'fs', '-mkdir', 'output'])
        if result:
            returnMsg.append(result)

        result = doCommand(['hadoop', 'fs', '-mkdir', path.join('output',dbName)])
        if result:
            returnMsg.append(result)

        # result = doCommand(['hadoop', 'fs', '-mkdir', path.join('output',dbName,tblName)])
        # if result:
        #     returnMsg.append(result)

        # step 2: Write df to hdfs
        bodyPath = path.join(outputPath, tblName) + ".csv"
        exportToHdfs(dfDF, bodyPath)

        # step 3: Write header to hdfs
        sparkSession = SparkSession.builder.appName("write").getOrCreate()
        headers = [tuple(headers)]
        header_df = sparkSession.createDataFrame(headers)
        headerPath = path.join(outputPath, tblName) + "_header.csv"
        exportToHdfs(header_df, headerPath)

        # step 4: get merge body
        # exportPath = 'file://' + str(path.join(path_, dbName, tblName, tblName)) + '.csv'
        exportPath = 'file://' + str(path.join(path_, dbName, tblName)) + '.csv'
        #20231127 change filename to k_proj.csv (i.e. k_dbName.csv)
        #outFileName_='k_'+dbName
        #exportPath = 'file://' + str(path.join(path_, dbName, tblName, outFileName_)) + '.csv'


         
        result = doCommand(['hadoop', 'fs', '-getmerge', path.join(headerPath, 'p*'), path.join(bodyPath, 'p*'), exportPath])
        if result:
            returnMsg.append(result)
        
        #20190718, citc add
        returnMsg = [msg for msg in returnMsg if "WARN" not in msg]
        
        
        errorMsg = [msg for msg in returnMsg if "File exists" not in msg]
        if errorMsg:
            return {'msg': ';'.join(returnMsg), 'result': 0}
        else:
            return {'msg': ';'.join(returnMsg), 'result': 1}

    except Exception as e: 
        return {'msg': str(e), 'result': 0}


def exportDataMac(dbName, dfDF, headers, tblName, path_):
    '''
    Export data to csv in local
    :param dbName: str, database name (project name)
    :param dfDF: Dataframe, body of df
    :param headers: list, header of df
    :param tblName: str, name of df which need to be exported.
    :param path_: str, path of output df
    :return: dict, if succeed, return {'msg': stdout, 'result': 1}, otherwise return {'msg': stderr, 'result': 0}
    '''

    try:
        from pyspark.sql import SparkSession

        returnMsg = list()

        # step 1: Create folder
        outputPath = path.join('output', dbName, tblName)
        # outputPath = path.join('output', dbName)


        result = doCommand(['hadoop', 'fs', '-mkdir', 'output'])
        if result:
            returnMsg.append(result)

        result = doCommand(['hadoop', 'fs', '-mkdir', path.join('output',dbName)])
        if result:
            returnMsg.append(result)

        result = doCommand(['hadoop', 'fs', '-mkdir', path.join('output',dbName,tblName)])
        if result:
            returnMsg.append(result)

        # step 2: Write df to hdfs
        bodyPath = path.join(outputPath, tblName) + ".csv"
        exportToHdfs(dfDF, bodyPath)

        # step 3: Write header to hdfs
        sparkSession = SparkSession.builder.appName("write").getOrCreate()
        headers = [tuple(headers)]
        header_df = sparkSession.createDataFrame(headers)
        headerPath = path.join(outputPath, tblName) + "_header.csv"
        exportToHdfs(header_df, headerPath)

        # step 4: get merge body
        exportPath = 'file://' + str(path.join(path_, dbName, tblName, tblName)) + '.csv'
        # exportPath = 'file://' + str(path.join(path_, dbName, tblName)) + '.csv'

        result = doCommand(['hadoop', 'fs', '-getmerge', path.join(headerPath, 'p*'), path.join(bodyPath, 'p*'), exportPath])
        if result:
            returnMsg.append(result)
        
        #20190718, citc add
        returnMsg = [msg for msg in returnMsg if "WARN" not in msg]
        
        
        errorMsg = [msg for msg in returnMsg if "File exists" not in msg]
        if errorMsg:
            return {'msg': ';'.join(returnMsg), 'result': 0}
        else:
            return {'msg': ';'.join(returnMsg), 'result': 1}

    except Exception as e: 
        return {'msg': str(e), 'result': 0}



def importData(dbName, pathData, tblName, spark_, user_=None):
    """
    Read file from local and put into hdfs by subprocess. Read file as spark
    dataframe from hdfs and return it.
    :param user: str
    :param dbName: str
    :param pathData: str
    :param tblName: str
    :param spark_: SparkSession
    :return: spark dataframe
    """
    returnMsg = list()

    try:
        if user_ is not None:
            result = doCommand(['hadoop', 'fs', '-mkdir', 'input'])
            result = doCommand(['hadoop', 'fs', '-mkdir', path.join('input', user_)])
            result = doCommand(['hadoop', 'fs', '-mkdir', path.join('input', user_, dbName)])
            result = doCommand(['hadoop', 'fs', '-put', '-f', pathData, path.join('input', user_, dbName)])
            if result:
                returnMsg.append(result)

            df = spark_.read.csv(path.join('input', user_, dbName, tblName), header=True, sep=",")

        else:
            result = doCommand(['hadoop', 'fs', '-mkdir', 'input'])
            result = doCommand(['hadoop', 'fs', '-mkdir', path.join('input')])
            result = doCommand(['hadoop', 'fs', '-mkdir', path.join('input', dbName)])
            result = doCommand(['hadoop', 'fs', '-put', '-f', pathData, path.join('input', dbName)])
            if result:
                returnMsg.append(result)
            df = spark_.read.csv(path.join('input', dbName, tblName) + '.csv', header=True, sep=",")

        if returnMsg:
            return {'msg': ';'.join(returnMsg), 'result': 0, 'df': None}
        else:
            return {'msg': ';'.join(returnMsg), 'result': 1, 'df': df}

    except Exception as e:
        if len(returnMsg) > 0:
            return {'msg': str(e) + ';' + ','.join(returnMsg), 'result': 0, 'df': None}
        else:
            return {'msg': str(e), 'result': 0, 'df': None}

def checkListQuotes(list_):
    checkFormat = ['\'', '\"']
    checkList = 0
    for i in range(len(list_)):
        value = str(list_[i])
        if value is not '':
            if (value[0] in checkFormat) and (value[-1] in checkFormat):
                checkList += 1
    if checkList:
        raise Exception("There are {0} columns of list values contain double quotes, "
                        "pleace check table format.".format(checkList))

def checkListQuotes_1side(list_, tblName):
    checkFormat = ['\'', '\"']
    checkList = 0
    for i in range(len(list_)):
        value = str(list_[i])
        if value is not '':
            if (value[-1] in checkFormat):
                checkList += 1
    if checkList:
        raise Exception("There are {0} columns of list values contain double quotes, "
                        "pleace check table: {1}.".format(checkList, tblName))



def exportDataJoin(dbName, dfDF, headers, tblName, path_):
    '''
    Export data to csv in local
    :param dbName: str, database name (project name)
    :param dfDF: Dataframe, body of df
    :param headers: list, header of df
    :param tblName: str, name of df which need to be exported.
    :param path_: str, path of output df
    :return: dict, if succeed, return {'msg': stdout, 'result': 1}, otherwise return {'msg': stderr, 'result': 0}
    '''

    try:
        from pyspark.sql import SparkSession

        returnMsg = list()

        # step 1: Create folder
        # outputPath = path.join('output', dbName, tblName)
        outputPath = path.join('output', dbName)


        result = doCommand(['hadoop', 'fs', '-mkdir', 'output'])
        if result:
            returnMsg.append(result)

        result = doCommand(['hadoop', 'fs', '-mkdir', path.join('output',dbName)])
        if result:
            returnMsg.append(result)

        result = doCommand(['hadoop', 'fs', '-mkdir', path.join('output',dbName,tblName)])
        if result:
            returnMsg.append(result)

        # step 2: Write df to hdfs
        
        doCommand(['echo','citcw200@','|','sudo','-S','chown','-R','hadoop:hadoop',"/home/hadoop/proj_/data/output"+"/"+dbName])
        bodyPath = path.join(outputPath, tblName) + ".csv"
        exportToHdfs(dfDF, bodyPath)

        # step 3: Write header to hdfs
        sparkSession = SparkSession.builder.appName("write").getOrCreate()
        headers = [tuple(headers)]
        header_df = sparkSession.createDataFrame(headers)
        headerPath = path.join(outputPath, tblName) + "_header.csv"
        exportToHdfs(header_df, headerPath)

        # step 4: get merge body
        exportPath = 'file://' + str(path.join(path_, dbName, tblName, tblName)) + '.csv'
        # exportPath = 'file://' + str(path.join(path_, dbName, tblName)) + '.csv'

        result = doCommand(['hadoop', 'fs', '-getmerge', path.join(headerPath, 'p*'), path.join(bodyPath, 'p*'), exportPath])
        if result:
            returnMsg.append(result)
        
        #20190718, citc add
        returnMsg = [msg for msg in returnMsg if "WARN" not in msg]
        
        
        errorMsg = [msg for msg in returnMsg if "File exists" not in msg]
        if errorMsg:
            return {'msg': ';'.join(returnMsg), 'result': 0}
        else:
            return {'msg': ';'.join(returnMsg), 'result': 1}

    except Exception as e: 
        return {'msg': str(e), 'result': 0}




