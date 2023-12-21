#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark import SparkConf, SparkContext, StorageLevel
from py4j.protocol import Py4JJavaError
from funniest import HiveLibs
from funniest.logging_tester import _getLogger

from lib.base64convert import getJsonParser


###########################################################################################
#
#Add 20180517
#
#from DataIO.GetData import *
import base64
import json
###########################################################################################
#
#Add 20180517
#
from lib.base64convert import getJsonParser
#from pprint import pprint
#import ast


#20200212, addssss###########
#for adding app status into mysql (spark_status.appStatus) 
from MyLib.updateAppStatus import updateAppStatus
from MyLib.updateAppStatus import updateAppProgress
#######################################################
import preview
from MyLib.connect_sql import ConnectSQL

#202000318, addssss
from MyLib.updateTProjectStatus import updateTProjectStatus

###########################################################################################
from MyLib.connect_sql import ConnectSQL
###########################################################################################

def initSparkContext(name):
    appName = name
    #master = 'yarn-client' #yarn
    master_ = 'yarn'
    try:
        #20200309, modified foe hive warehouse (located in hdfs)#################################
        #spark_ = SparkSession.builder.enableHiveSupport().master(master_).appName(appName).getOrCreate()

        warehouse_location = "hdfs://nodemaster:9000/user/hive/warehouse"
        #warehouse_location = "hdfs:///user/hive/warehouse"

        spark_ = SparkSession.builder.enableHiveSupport().master(master_).appName(appName) \
                     .config("spark.sql.warehouse.dir", warehouse_location) \
                                     .getOrCreate()
        ###################################################################################         

        sc_ = spark_.sparkContext
        sc_.setSystemProperty("hive.metastore.uris", "thrift://nodemaster:9083")

        hiveLibs = HiveLibs(sc_)
        sqlContext = hiveLibs.dbOperation.get_sqlContext()
        _logger.debug("sparkContext_succeed.")

        """
        sc = SparkContext(conf=SparkConf().setAppName(appName).setMaster(master))
        hiveLibs = HiveLibs(sc)
        sqlContext = hiveLibs.dbOperation.get_sqlContext()
        _logger.debug("sparkContext_succeed.")
        """

    except Exception as e:
        _logger.debug(sys.exc_info()[0])
        _logger.debug(sys.exc_info()[1])
        _logger.debug(len(sys.exc_info()))
        _logger.debug("errTable_fundation_getKchecking_one:"+str(e))
        _logger.debug("errTable_errSC")
        return SparkContext(conf=SparkConf())

    return sc_,hiveLibs, sqlContext

def registerTempTable_forsparksql(data_frame_, tb_name_):
    data_frame_.registerTempTable(tb_name_)
    return tb_name_

######################################################################
###################  201806030 #######################################
######################################################################
def all_lower(L1):
    return [s.lower() for s in L1]

#�?list 轉�??��?�?

def computKvalue_usingDF(list_, df_):
    cols = []
    for col_ in list_:
        cols.append(col_)
    #print cols
    kValueDF0420_ = df_.groupby(cols).count()
    return kValueDF0420_

def randomSample(df, nRows=100):
    '''
    input: pyspark.dataframe
    return: list of dicts
    '''
    try:
       #sample_ = df.sample(False,0.2).limit(nRows).toPandas().to_dict('records')
       sample_ = df.toPandas()#.sample(False,1.0).limit(nRows).toPandas()
    except Exception as e:
        _logger.debug('errTable:'+NAME+'_sample_data_fail: '+str(e))
        return None

    return sample_


def maskSmallKValue_NoRowId(key_col,mask_list_, kValue,tb_name__ ):
    tmpStr='\n'
    tmpStr = tmpStr+ 'select '+key_col+', '
    for col_name_ in mask_list_:
        tmpStr = tmpStr+'\n'+'case'+' '+'when'
        tmpStr = tmpStr+ ' count <'+ str(kValue)+'\n'+'then '
        tmpStr = tmpStr+'regexp_replace('+col_name_+', \'.\', \'*\')'
        tmpStr = tmpStr+ '\nelse '
        tmpStr = tmpStr+col_name_
        tmpStr = tmpStr+ '\nend as '+col_name_+','

    tmpStr = tmpStr+ 'count '
    tmpStr = tmpStr+'from '+ tb_name__
    _logger.debug(tmpStr)
    df_=sqlContext.sql(tmpStr)
    df____=df_
    return df____

def join2DF_removeDF1Duplication(df1, df2, cond,duplicationList, type):
    cols = df1.columns
    print(cols)
    for colname in duplicationList:
        cols.remove(colname)
    df1 = df1.select([column for column in df1.columns if column not in cols])
    dfJoin = df1.join(df2, cond, type)#.drop(df_y.caseno).drop(df_y.seqno).drop(df_y.trackdate)
    #dfJoin = df_y.join(kValueDF0420_, cond, 'right').drop(df_y.caseno)
    return dfJoin


def rmcol(data,cols):
    aa = data.select([column for column in data.columns if column not in cols])
    return aa


def registerRealHiveTable_forsparksql(data_frame_, tb_name_):
    data_frame_.write.format("orc").mode("overwrite").saveAsTable(tb_name_)
    df_count = data_frame_.count()
    return df_count

###########################################################################################

###########################################################################################

def checkWarningCol(df, passCols, kvalue):
    _logger.debug("Start to check warning col")
    columns = df.columns
    print (columns)
    for col in passCols:
        columns.remove(col)
    _logger.debug("columns")
    _logger.debug(columns)
#    warningCols = dict()
#    for col in columns:
#        df1 = df.persist()
#        df2 = df1.groupby(col).count()
#        condition = "count < {0}".format(kvalue)
#        df3 = df2.filter(condition)
#
#        if df3.take(1):
#            # warning col
#            warningNum = df3.select(F.sum("count")).collect()[0][0]
#            warningCols[col] = warningNum

    if columns == []:
        warningCols = dict()
    else:
        warningCols = dict()
        for col in columns:
            df1 = df.persist()
            df2 = df1.groupby(col).count()
            condition = "count < {0}".format(kvalue)
            df3 = df2.filter(condition)

            if df3.take(1):
                # warning col
                warningNum = df3.select(F.sum("count")).collect()[0][0]
                warningCols[col] = warningNum

        df1.unpersist()
        df2.unpersist()
        df3.unpersist()

    return warningCols

#def main__(dbName, tblName, colsNum, totalLen):
def main():
    global sc, sqlContext, hiveLibs, _logger , _vlogger, updateAppStatus_, updateTProjectStatus_

    ############################################################################################
    #Add log
    #20180518
    #_logger=_getLogger('udfEncUID')
    _logger = _getLogger("getKchecking_one")
    _vlogger = _getLogger("verify__getKchecking_one")

#    _logger.debug('###################sc.applicationId')
#    _logger.debug(sc.applicationId)
   ############################################################################################
#    try:
#        json__ = getJsonParser(base64_)
#        _vlogger.debug(json__)
#    except Exception as e:
#        _logger.debug("get json error !")
#


    # spark setting
    appName = 'getKchecking_one'
    sc, hiveLibs, sqlContext = initSparkContext(appName)


    try:
        dd = getJsonParser(base64_)
        _logger.debug(dd)

        _logger.debug("------ userAccount  userId --start-------")
        userAccount = dd[u'userAccount']
        userId = dd[u'userId']
        _logger.debug('k_userAccount_%s',userAccount)
        _logger.debug('k_userId_%s',userId)
        _logger.debug("------ userAccount  userId --end-------")

        data = dd[u'mainInfo']
        jobName = dd[u'jobName']
        _logger.debug(jobName)

        projStep = dd[u'projStep']
        _logger.debug(projStep)

        projID = dd[u'projID']
        _logger.debug(projID)
        _logger.debug('###################projID___')
        _logger.debug('projID___: {}'.format(projID))
        _vlogger.debug('projID___: {}'.format(projID))

        projName = dd[u'projName']
        _logger.debug(projName)

        db_name = data[u'dataInfo'][0][u'dbName']
        _logger.debug(db_name)

        tables_name = data[u'dataInfo'][0][u'tableName']
        _logger.debug(tables_name)

        QIcols = data[u'dataInfo'][0][u'QIcols']
        _logger.debug(QIcols)

        cols = data[u'dataInfo'][0][u'colNames']
        _logger.debug(cols)

        k_value = int(dd[u'mainInfo'][u'kValue'])
        _logger.debug(k_value)
        _logger.debug(type(k_value))

        key = [data[u'dataInfo'][i][u'keyNames'] for i in range(len(data[u'dataInfo']))]
                #key = all_lower(["id"])
        _logger.debug(key)

        newkey = key[0]
        _logger.debug(newkey)
        newkeyin = newkey[0]
        _logger.debug(newkeyin)





#        _logger.debug('###################dbName')
#        _logger.debug("dbName: {}".format(db_name))
#        _logger.debug('###################tb_name_')
#        _logger.debug("tb_name_: {}".format(tables_name_))
      #_logger.debug(list_)
        #_logger.debug(cols)
#        _logger.debug('###################sc.applicationIdecking_one.py)
#        _logger.debug(sc.applicationId)

    except Py4JJavaError as e:
        s = e.java_exception.toString()
        _logger.debug(s)
    except Exception:
        _logger.debug(sys.exc_info()[0])
        _logger.debug(sys.exc_info()[1])
        _logger.debug(sys.exc_info()[2])
        _logger.debug(len(sys.exc_info()))
        _logger.debug("errTable_errReadFromHive")
    
       # 20221217
    # userAccount = "deidadmin"
    # userId = "7"
    # _logger.debug('spark_k_userAccount_%s',userAccount)
    # _logger.debug('spark_k_userId_%s',userId)
    
     
    
    
    ###20200212, add for checking app status(write to mysql)##############
    try:
        #appID, appName
        #"projID": "1"
        projID = dd[u'projID']
        #updateAppStatus_ = updateAppStatus(sc.applicationId, NAME)
        updateAppStatus_ = updateAppStatus(sc.applicationId, appName,db_name,projID,userId)
    except Exception as e:
        
        _logger.debug('updateAppStatus error: %s', str(e))
        return False
    
    ###202000318, add for checking app status(write to mysql)##############
    ###202000319, move here##############
    project_id = projID
    try:
        updateTProjectStatus_ = updateTProjectStatus(project_id,userId)
    except Exception as e:        
        _logger.debug('updateTProjectStatus error: %s', str(e))
        return False 
   
    
    
    #1 app status
    #updateToMysql(self,appState, progress,progress_state="Running")
    updateAppStatus_.updateToMysql("Init_1","5") #5%
    #_logger.debug("------20200206-3-------------")
    #####################################################################


    _logger.debug('###################dbName___')
    _vlogger.debug('dbName___: {}'.format(db_name))
    _logger.debug('###################tb_name_')
    _vlogger.debug("tb_name_: {}".format(tables_name))
    _logger.debug('###################final_table_name_')
    # final_tb_name = projName+"_"+jobName+"_"+projStep+"_"+tables_name+"_final"
    final_tb_name = tables_name + "_k_" + jobName
    _vlogger.debug('final_tb_name: {}'.format(final_tb_name))
    _logger.debug('###################sc.applicationId')
    _logger.debug("sc.applicationId:" + sc.applicationId)
#    _logger.debug('###################sc.applicationId')
#    _logger.debug(sc.applicationId)

#    _logger.debug('###################minKvalue')
#    _vlogger.debug("minKvalue:%i" %(k_value))

        ####################################################################################
        ####################################################################################
        ####################################################################################


    _logger.debug('updateUserID')
    your_conn = ConnectSQL()
    dbSQL = "DeIdService"
    tblSQL = "T_Project_SampleTable"
    conditions = {
            'pro_db': db_name, 
            'pro_tb': tables_name[2:]
        }
    setColsValue = {
            'createMember_Id': userId,
            'updateMember_Id': userId
        }
    your_conn.updateValue(dbSQL, tblSQL, conditions, setColsValue)


    try:
        sqlContext.sql('use ' + db_name)

        put =""
        for colNam_ in cols:
            if colNam_ in cols[-1:]:
                put=put + colNam_
            else:
                put=put+ colNam_+ ","
        print(put)
        tem='select ' + put + ' from ' + tables_name
        df_  = sqlContext.sql(tem)
        df_count = df_.count()
        print(df_count)

        _logger.debug('###################df_count')
        _vlogger.debug("df_count:%i" %(df_count))
#        print("mask_count :%f" %(d2[0]))

        ###20200212, add for checking app status(write to mysql)##############
        #after compute Table count
        try:
            updateAppStatus_.updateToMysql("compute Table count","15") #5%
        except Exception as e:            
            _logger.debug('updateAppStatus error: %s', str(e))
            return False
           
        #####################################################################


        #df_ = sqlContext.sql("select * from " + tables_name)
#        df_.show(5)


        cc = all_lower(df_.columns)
        print(cc)

        #all_QIcols = [x for j in QIcols for x in j]
        #print all_QIcols
        print(QIcols)
        ##20200212, citc add
        _logger.debug("QIcols:%s" %(QIcols))
###################################################################
#        aa = computKvalue_usingDF(QIcols, df_)
        put1 =""
        for colNam_ in QIcols:
            if colNam_ in QIcols[-1:]:
                put1=put1 + colNam_
            else:
                put1=put1+ colNam_+ ","
        print(put1)

        all_key = ''
        for keyName_ in newkey:
            if keyName_ in newkey[-1:]:
                all_key = all_key + keyName_
            else:
                all_key = all_key + keyName_+ ","
        print(all_key)

        _logger.debug('###################key ')
        _vlogger.debug("all_key:%s" %(all_key))
        tem='select ' + put1 + ',count(distinct('+all_key+')) as count' +' from ' + tables_name +' group by '+ put1
        print(tem)
        _logger.debug('###################kchecking_code ')
        #_logger.debug("kchecking_code: {}".format(tem))
        #kchecking_code: select c_3571_5,c_3571_9,count(distinct(c_3571_1,c_3571_2)) as count from g_mac_adult_id group by c_3571_5,c_3571_9
        _vlogger.debug("kchecking_code: {}".format(tem))
        aa = sqlContext.sql(tem)

        ###20200212, add for checking app status(write to mysql)##############
        #after compute QIs count (for k value)
        try:
            updateAppStatus_.updateToMysql("compute QIs count (for k value)","30") #5%
        except Exception as e:            
            _logger.debug('updateAppStatus error: %s', str(e))
            return False
        #####################################################################




        #sampleDf = randomSample(aa)
        #_logger.debug(sampleDf) 
###################################################################
#        aa.show(30)

        """ old version
        QI_data = df_.join(aa,QIcols, "left")
#        QI_data.show(30)
:q
        all_key = [x for j in key for x in j]
        all_key

        str_all_key =""
        for colNam_ in all_key:
            if colNam_ in all_key[-1:]:
                str_all_key = str_all_key + colNam_
            else:
                str_all_key = str_all_key+ colNam_+ ","
        print(str_all_key)


        df = registerTempTable_forsparksql( QI_data,  "QI_data")
        maskkValueDF_ =  maskSmallKValue_NoRowId(str_all_key, QIcols , k_value, df)
        print(k_value)
        _logger.debug('###################minKvalue ')
        _vlogger.debug("minKvalue:%i" %(k_value))
        """

        QI_data = df_.join(aa, QIcols, "left")
        #        QI_data.show(30)
        without_QI = list(filter(lambda x: x not in QIcols, cols))
        print(without_QI)

        no_QI = ""
        for colNam_ in without_QI:
            if colNam_ in without_QI[-1:]:
                no_QI = no_QI + colNam_
            else:
                no_QI = no_QI + colNam_ + ","
        print(no_QI)

        df = registerTempTable_forsparksql(QI_data, "QI_data")
        maskkValueDF_ = maskSmallKValue_NoRowId(no_QI, QIcols, k_value, df)
        # _logger.debug(maskkValueDF_.take(50))
        #sampleDf = randomSample(maskkValueDF_)
        #_logger.debug(sampleDf) 

        print(k_value)
        _logger.debug('###################minKvalue ')
        _vlogger.debug("___minKvalue___:%i" % (k_value))

        ###20200212, add for checking app status(write to mysql)##############
        #after compute minKvalue (i.e. k value)
        try:
            updateAppStatus_.updateToMysql("compute minKvalue (i.e. k value)","40") #5%
        except Exception as e:            
            _logger.debug('updateAppStatus error: %s', str(e))
            return False
        #####################################################################


#########################################################################################

        cc =registerTempTable_forsparksql( maskkValueDF_,  "dfJoin_finish")
        x = QIcols[0]
        tem='select * from dfJoin_finish where '+x+ " like '%*%'"
        mask_count = sqlContext.sql(tem)
        mc = mask_count.count()

        ###20200212, add for checking app status(write to mysql)##############
        #after join maskValueDF to fininsed Table
        try:
            updateAppStatus_.updateToMysql("join maskValueDF to fininsed Table","50") #5%
        except Exception as e:            
            _logger.debug('updateAppStatus error: %s', str(e))
            return False
        #####################################################################

#        parsedData1 = mask_count.rdd.map(lambda x: x[0])
#        d2 = parsedData1.collect()
#        print(d2)

        _logger.debug('###################supCount ')
        _vlogger.debug("supCount:%i" %(mc))
#        print("mask_count :%f" %(mc))
        s_rate = float(mc)/float(df_count)
        print(s_rate)
        _logger.debug('###################supRate ')
        _vlogger.debug("supRate:%f" %(s_rate))


        count_col = ["count"]
        dfK_finish = rmcol(maskkValueDF_,count_col)
        dfK_finish.show(12)
#        print(dfK_finish.count())

        k_method = 'sup'
        if k_method == 'sup':
            dfK_finish = dfK_finish.filter(x + " not like '*%'")
            deid_df_count = dfK_finish.count()
        else:
            dfK_finish = dfK_finish

        dfK_finish_count = dfK_finish.count()
        _logger.debug('###################dfK_finish_count ')
        _vlogger.debug("dfK_finish_count:%i" %(dfK_finish_count))

        # Check warning columns
        try:
            rowId_col = data[u'dataInfo'][0][u'rowId'] #["rowId"]
        except Exception:
            rowId_col = []

        passCols = newkey + QIcols + rowId_col
        # passCols = newkey + QIcols
        _logger.debug("$$$$$$$$$$$$$$$$$$$$$$$$")
        _logger.debug(passCols)
        _logger.debug("$$$$$$$$$$$$$$$$$$$$$$$$")
        # dfK_finish.show(10)
        warningCols = checkWarningCol(dfK_finish, passCols, k_value)
        cols = list()
        counts = list()
        _logger.debug("warningCols")
        _logger.debug(warningCols)
#        for col in warningCols:
#            cols.append(str(col))
#            counts.append(str(warningCols[col]))
#        warningColsStr = ','.join(cols) + '*' + ','.join(counts)
#        _logger.debug("warningCols:%s" % (warningColsStr))
        if warningCols == {}:
            warningColsStr = ''
            _logger.debug("warningCols:%s" % (warningColsStr))
        else:
            for col in warningCols:
                cols.append(str(col))
                counts.append(str(warningCols[col]))
            warningColsStr = ','.join(cols) + '*' + ','.join(counts)
            _logger.debug("warningCols:%s" % (warningColsStr))


        df_distinct = registerTempTable_forsparksql(dfK_finish, "dfK_finish_count")
        # tem='select distinct ' + newkeyin + ' from dfK_finish_count'
        tem='select distinct ' + all_key + ' from dfK_finish_count'
        distinct_count = sqlContext.sql(tem)
        dc = distinct_count.count()
        print (dc)

        d_f_c = df_count-mc
        _logger.debug('###################distinct_count ')
        _vlogger.debug("distinct_count:%i" %(d_f_c))
        _logger.debug(warningCols)
        _logger.debug("warningCols:%s" % (warningColsStr))

        ###20200212, add for checking app status(write to mysql)##############
        #after compute suppression and warring columns
        try:
            updateAppStatus_.updateToMysql("compute suppression and warring columns","80") #5%
        except Exception as e:            
            _logger.debug('updateAppStatus error: %s', str(e))
             
            return False
        #####################################################################
        if dc != 0:
            pass
        else:
            _logger.debug('data empty')
            your_conn = ConnectSQL()
            dbSQL = "DeIdService"
            tblSQL = "T_Project_SampleTable"
            conditions = {
                    'pro_db': db_name, 
                    'pro_tb': tables_name[2:]
                }
            setColsValue = {
                    'supRate': "100.0%"
                }
            your_conn.updateValue(dbSQL, tblSQL, conditions, setColsValue)
            updateAppStatus_.updateToMysql("Py4JJavaError" ,"90","err")
            updateTProjectStatus_.updateToMysql(project_id, 90,"error")
            return
#########################################################################################

#        maskkValueDF_.show(30)

#        mask_count = maskkValueDF_.count()
#        _logger.debug('###################mask_count ')
#        _vlogger.debug("mask_count :%f" %(mask_count ))


#        aaa = rmcol(df_,QIcols)
#        aaa.show(12)

            #Join

#        l1 = newkey
#        dfJoin_finish = aaa.join(maskkValueDF_, l1, "left")
#        dfJoin_finish.show(30)
        #    dfJoin_finish.filter(dfJoin_finish.count < 3).show(15)
#        cc =registerTempTable_forsparksql( dfJoin_finish,  "dfJoin_finish")

        #    print(cols_name)
        #    print("################")
        #    print("################")
#        put =""
#        for colNam_ in cols:
#            if colNam_ in cols[-1:]:
#                put=put + colNam_
#            else:
#                put=put+ colNam_+ ","
#        print(put)
#        tem='select ' + put +  ' from  dfJoin_finish'
#        data_finish = sqlContext.sql(tem)
#        data_finish.show(5)



#        put =""
#        for colNam_ in QIcols:
#            if colNam_ in QIcols[-1:]:
#                put=put + colNam_
#            else:
#                put=put+ colNam_+ "_"
#        print(put)



        try:
            dfK_finish_count = registerRealHiveTable_forsparksql(dfK_finish, final_tb_name) #2022-1 #2022-3 for MLutility.py, final_tb_name=g_mac_adult_id_k_job1
        except Exception as e:
            _logger.debug('save data to Hive err: %s', str(e))
            updateAppStatus_.updateToMysql("Py4JJavaError" ,"97","err")
            updateTProjectStatus_.updateToMysql(project_id, 97,"error")
            return False

        ###20200212, add for checking app status(write to mysql)##############
        #after All_table_save_succeed
        try:
            updateAppStatus_.updateToMysql("All_table_save_succeed","100","Finished")#5%
        except Exception as e:            
            _logger.debug('updateAppStatus error: %s', str(e))
            return False
        #####################################################################
#registerRealHiveTable_forsparksql(maskkValueDF_, "Ntu"+"_"+jobName+"_"+projStep+"_"+put)

    except Py4JJavaError as e:
        s = e.java_exception.toString()
        _logger.debug(s)
        updateAppStatus_.updateToMysql("Py4JJavaError" ,"97","err")
        updateTProjectStatus_.updateToMysql(project_id, 97,"error")
    except Exception:
        _logger.debug(sys.exc_info()[0])
        _logger.debug(sys.exc_info()[1])
        _logger.debug(sys.exc_info()[2])
        _logger.debug(len(sys.exc_info()))
        _logger.debug("errTable_errReadFromHive")
        updateAppStatus_.updateToMysql("errTable_errReadFromHive" ,"97","err")
        updateTProjectStatus_.updateToMysql(project_id, 97,"error")

#    try:
#        preview_ = preview.previewDeID(projID, db_name, tables_name, dfK_finish)
#        _vlogger.debug(preview_.write2mySql())
#    except Exception as e:
#        _logger.debug('errTable: DeID preview fail: '+str(e))
#        updateAppStatus_.updateToMysql("errTable: DeID preview fai" ,"97","err")
#        updateTProjectStatus_.updateToMysql(project_id, 97,"error")
    
    #ICL, add 20220609
    try:
        project_status =9
        statusname='k checking finished'
        ret_ = updateTProjectStatus_.updateToMysql(project_id, project_status,statusname)
        if(ret_ == False):
            _logger.debug('------(k checking finished update fail)--------update updateTProjectStatus_ error') 
        if(ret_ == True):
            _logger.debug('------(k checking finished update success)--------') 
    except Exception as e:
        _logger.debug('update updateTProjectStatus_ error: %s', str(e)) 
    
    _logger.debug('###################sc.applicationId')
    _vlogger.debug(sc.applicationId)




if __name__ == "__main__":
    

    base64_ = sys.argv[1]
#    dbName = sys.argv[2]
#    tb_name_ = sys.argv[3]
#    dbName = sys.argv[1] #databases name
#    tb_name_ = sys.argv[2] # table name
#    base64_ = sys.argv[3]
#    list_  = sys.argv[3]   #All cols
#    cols = sys.argv[4]  #QI
    print('########')
#    print(dbName)
#    print(tb_name_)
#    print(colsNum)
#    print(totalLen)
    print('#############')
    main()
