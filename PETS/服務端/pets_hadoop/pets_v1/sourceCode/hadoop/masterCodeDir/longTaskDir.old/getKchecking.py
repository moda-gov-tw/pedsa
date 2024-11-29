#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from pyspark.sql import SparkSession
from pyspark import SparkConf, SparkContext, StorageLevel
from py4j.protocol import Py4JJavaError
from funniest import HiveLibs
from funniest.logging_tester import _getLogger
from lib.base64convert import getJsonParser

###########################################################################################

###########################################################################################

def initSparkContext(name):
    appName = name
    #master = 'yarn-client' #yarn
    master_ = 'yarn'
    try:
        spark_ = SparkSession.builder.enableHiveSupport().master(master_).appName(appName).getOrCreate()
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
        _logger.debug("errTable_fundation_getGenNumLevel:"+str(e))
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
    #print(cols)
    kValueDF0420_ = df_.groupby(cols).count()
    return kValueDF0420_


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
#    print(tmpStr)
    _vlogger.debug(tmpStr)
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
    return tb_name_

###########################################################################################

###########################################################################################

 
#def main__(dbName, tblName, colsNum, totalLen):     
def main():
    global sc, sqlContext, hiveLibs, _logger, _vlogger
   
    ############################################################################################
    #Add log 
    #20180518
    #_logger=_getLogger('udfEncUID')
    _logger = _getLogger("getKchecking")
    _vlogger = _getLogger("verify__getKchecking")


    ############################################################################################
#    try:
#        json__ = getJsonParser(base64)
#        _vlogger.debug(json__)
#    except Exception as e:
#        _logger.debug("get json error !")
#

    appName = 'getKchecking'
    sc, hiveLibs, sqlContext = initSparkContext(appName)

    _logger.debug('##################dbName___')
    _vlogger.debug("dbName___: {}".format(dbName))
    _logger.debug('###################tb_name_')
    _vlogger.debug("tb_name_: {}".format(tb_name_))
#    _logger.debug('###################sc.applicationId')
#    _logger.debug(sc.applicationId)
    

    try:
        dd = getJsonParser(base64)
#        dd
#        dd = ast.literal_eval(mainInfo)
#        dd
        print(dd)
        data = dd[u'mainInfo']
        jobName = dd[u'jobName']
        print(jobName)

        projStep = dd[u'projStep']
        print(projStep)

        projName = dd[u'projName']
        print(projName)

        db_name = [data[u'dataInfo'][i][u'dbName'] for i in range(len(data[u'dataInfo']))]
        print(db_name)
        
        tables_name = [data[u'dataInfo'][i][u'tableName'] for i in range(len(data[u'dataInfo']))]
        print(tables_name)
        
        QIcols = [data[u'dataInfo'][i][u'QIcols'] for i in range(len(data[u'dataInfo']))]
        print(QIcols)
        
        cols = [data[u'dataInfo'][i][u'colNames'] for i in range(len(data[u'dataInfo']))]
        print(cols)
        
        k_value = int(dd[u'mainInfo'][u'kValue'])
        print(k_value)
        print(type(k_value))
        
        key = [data[u'dataInfo'][i][u'keyNames'] for i in range(len(data[u'dataInfo']))]
        #key = all_lower(["id"])
        print(key)
        
        str_key = key[0]
        print(str_key)
        
        print(dbName)
        print(tb_name_)

        _logger.debug('###################projStep')
        _vlogger.debug("projStep: {}".format(projStep))
        _logger.debug('###################"projName')
        _vlogger.debug("projName: {}".format(projName))
        #_logger.debug(list_)
        #_logger.debug(cols)
#        _logger.debug('###################sc.applicationId')
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
        
 
        ####################################################################################
        ####################################################################################
        ####################################################################################
        
    try:

        sqlContext.sql('use ' + dbName)
        df_ = sqlContext.sql("select * from " + tb_name_)
        #        df_.show(5)

        df_count = df_.count()
        print(df_count)

        _logger.debug('###################df_count')
        _vlogger.debug("df_count:%i" % (df_count))

        cc = all_lower(df_.columns)
        #        print(cc)

        all_QIcols = [x for j in QIcols for x in j]
        all_QIcols

        aa = computKvalue_usingDF(all_QIcols, df_)
        #        aa.show(30)

        QI_data = df_.join(aa, all_QIcols, "left")
        #        QI_data.show(30)

        all_key = [x for j in key for x in j]
        all_key

        str_all_key = ""
        for colNam_ in all_key:
            if colNam_ in all_key[-1:]:
                str_all_key = str_all_key + colNam_
            else:
                str_all_key = str_all_key + colNam_ + ","
                #        print(str_all_key)

        df = registerTempTable_forsparksql(QI_data, "QI_data")
        maskkValueDF_ = maskSmallKValue_NoRowId(str_all_key, all_QIcols, k_value, df)

        print(k_value)
        _logger.debug('###################minKvalue ')
        _vlogger.debug("minKvalue:%i" % (k_value))
#########################################################################################

        cc =registerTempTable_forsparksql( maskkValueDF_,  "dfJoin_finish")
        x = QIcols[0][0]
        print(x)


        #tem='select * from dfJoin_finish where '+x+ " like '%*%'"
        tem = "select * from dfJoin_finish where {} like '%*%'".format(x)
        _vlogger.debug(tem)
        mask_count = sqlContext.sql(tem)
        mc = mask_count.count()

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



#        maskkValueDF_.show(30)
        
#        maskkValueDF_.count()
        
        put =""
        for colNam_ in all_QIcols:
            if colNam_ in all_QIcols[-1:]:
                put=put + colNam_  
            else:
                put=put+ colNam_+ "_"

#        print(put)
        
        ####################################################################################
        registerRealHiveTable_forsparksql(maskkValueDF_, projName+"_"+jobName+"_"+"kchecking")
        ####################################################################################
#registerRealHiveTable_forsparksql(maskkValueDF_, "Ntu"+"_"+jobName+"_"+projStep+"_"+put)
 
        _logger.debug('###################final_tb_name_')
        _vlogger.debug('final_tb_name_:%s' %(projName+"_"+jobName+"_"+"kchecking"))

 
    except Py4JJavaError as e:
        s = e.java_exception.toString()
        _logger.debug(s)
    except Exception:
        _logger.debug(sys.exc_info()[0])
        _logger.debug(sys.exc_info()[1])
        _logger.debug(sys.exc_info()[2])
        _logger.debug(len(sys.exc_info()))
        _logger.debug("errTable_errReadFromHive")        

        #dbName input
        #tblName input


        ####################################################################################
        ####################################################################################
        ####################################################################################
    try:
        for i in range(len(db_name)):

            QItable = registerTempTable_forsparksql(maskkValueDF_,  "QItable")
        #    maskkValueDF_.show(30)
            key
            print(key)
            newkey = key[i]
            print(newkey)
            newkeyin = newkey[0]
            
            print(newkeyin)
            kk = sqlContext.sql("select " + newkeyin+",count from QItable")
#            kk.show(30)
            
            db = db_name[i]
            
            sqlContext.sql("use " + db)
            
            QI = QIcols[i]
            QI = all_lower(QI)
            print(QI)
  
            cols_name = cols[i]
            cols_name = all_lower(cols_name)
            print(cols_name)

            tb = tables_name[i]
            print(tb)
            

            put =""
            for colNam_ in cols_name:
                if colNam_ in cols_name[-1:]:
                    put=put + colNam_  
                else:
                    put=put+ colNam_+ ","
            print(put)
            tem='select ' + put + ' from ' + tb
            df_  = sqlContext.sql(tem)
#            df_.show(1)
            dfJoin = df_.join(kk,newkeyin, "left")
#            dfJoin.show(3)
            
            ddf = registerTempTable_forsparksql( dfJoin,  "dfJoin")
            maskkValueDFin4loop_ =  maskSmallKValue_NoRowId(newkeyin, QI , k_value , ddf)
        #    maskkValueDF_.show(30)


            mask_count = maskkValueDFin4loop_.count()
            _logger.debug('###################mask_count ')
            _vlogger.debug("mask_count :%f" %(mask_count ))


            # remove ori table QI col
        #    QI.append("count")
            aaa = rmcol(df_,QI)
#            aaa.show(12)

            #Join

            l1 = newkey
            dfJoin_finish = aaa.join(maskkValueDFin4loop_, l1, "left")
#            dfJoin_finish.show(30)
        #    dfJoin_finish.filter(dfJoin_finish.count < 3).show(15)
            cc =registerTempTable_forsparksql( dfJoin_finish,  "dfJoin_finish")

        #    print(cols_name)
        #    print("################")
        #    print("################")
            put =""
            for colNam_ in cols_name:
                if colNam_ in cols_name[-1:]:
                    put=put + colNam_  
                else:
                    put=put+ colNam_+ ","
            print(put)
            tem='select ' + put +  ' from  dfJoin_finish'
            data_finish = sqlContext.sql(tem)
            data_finish.show(5)

            print("################")
            print("#####finish####")
            print("################")
        #    registerRealHiveTable_forsparksql(data_frame_, tb_name_)
            registerRealHiveTable_forsparksql(data_finish,   projName+"_k_" + tb +"_deid")

         
    except Py4JJavaError as e:
        s = e.java_exception.toString()
        _logger.debug(s)
    except Exception:
        _logger.debug(sys.exc_info()[0])
        _logger.debug(sys.exc_info()[1])
        _logger.debug(sys.exc_info()[2])
        _logger.debug(len(sys.exc_info()))
        _logger.debug("errTable_errReadFromHive")

    _logger.debug('###################sc.applicationId')
    _vlogger.debug(sc.applicationId)

########################################################################################################  

if __name__ == "__main__":
    
    
    base64 = sys.argv[1]
    dbName = sys.argv[2]
    tb_name_ = sys.argv[3]
#    dbName = sys.argv[1] #databases name 
#    tb_name_ = sys.argv[2] # table name
#    base64 = sys.argv[3]
#    list_  = sys.argv[3]   #All cols
#    cols = sys.argv[4]  #QI
    print('########')
    print(dbName)
    print(tb_name_)
#    print(colsNum)
#    print(totalLen)
    print('#############')
    main()
