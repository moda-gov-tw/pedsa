from MyLib.connect_sql import ConnectSQL


class previewDeID():
    def __init__(self, projID, projName, tblName, df_k):
        self.projID = projID
        self.projName = projName
        self.tblName = tblName[2:]
        self.df_k = df_k
        self.conn = ConnectSQL()

    def updateToMysql(self, sampleKdata, distCount):
        # insert to sample data
        condisionSampleData = {
            'project_id': self.projID,
            'dbname': self.projName,
            'tbname': self.tblName
        }

        valueSampleData = {
            'project_id': self.projID,
            'dbname': self.projName,
            'tbname': self.tblName,
            'kdata': sampleKdata,
            'distinctCount': distCount
        }
        # def updateValue(self, dbName, tblName, conditions, setColsValue):
        resultSampleData = self.conn.updateValueMysql('DeIdService',
                                                      'T_ProjectSampleData',
                                                      condisionSampleData,
                                                      valueSampleData)
        if resultSampleData['result'] == 1:
            return("Update mysql succeed. {0}".format(resultSampleData['msg']))
        else:
            msg = resultSampleData['msg']
            return('insertSampleDataToMysql fail: ' + msg)

    def updateToMysql_SampleTable(self, kdataCol):
        # insert to sample data
        condisionSampleData = {
            'project_id': self.projID,
            'pro_db': self.projName,
            'pro_tb': self.tblName
        }

        valueSampleData = {
            'project_id': self.projID,
            'pro_db': self.projName,
            'pro_tb': self.tblName,
            'kdata_col_en': '\"'+str(kdataCol)+'\"'
        }
        # def updateValue(self, dbName, tblName, conditions, setColsValue):
        resultSampleData = self.conn.updateValueMysql('DeIdService',
                                                      'T_Project_SampleTable',
                                                      condisionSampleData,
                                                      valueSampleData)
        if resultSampleData['result'] == 1:
            return("Update mysql succeed. {0}".format(resultSampleData['msg']))
        else:
            msg = resultSampleData['msg']
            return('insertSampleDataToMysql fail: ' + msg)

    def random5Sample(self, nRows=5):
        '''
        input: pyspark.dataframe
        return: list of dicts
        '''
        try:
           #sample_ = df.sample(False,0.2).limit(nRows).toPandas().to_dict('records')
           sample_ = self.df_k.sample(False,0.2).limit(nRows).toPandas()
        except Exception as e:
            print('errTable:sample_data_fail: '+str(e))
            return 'error!!!!!!!!!!!!'
        return sample_

    def colUniqueNum(self, cols):
        uniqueNum = []
        pdf_k = self.df_k.toPandas()
        for col in cols:
            count = pdf_k[col].nunique()
            uniqueNum.append(str(count))
        return ','.join(uniqueNum)

    def write2mySql(self):
        sample5Df = self.random5Sample()
        print(sample5Df)
        enColName = sample5Df.columns.tolist()
        uniqueNum = self.colUniqueNum(enColName)
        '''
        getRawColName_ = "select after_col_cht from DeIdService.T_Project_SampleTable where project_id={} and pro_db=\'{}\' and pro_tb=\'{}\';".format(self.projID, self.projName, self.tblName)
        rawColName = self.conn.doSqlCommand(getRawColName_)
        try:
            sample5Df.columns = rawColName['fetchall'][0]['after_col_cht'].split(',')
        except Exception as e:
            return rawColName
        '''
        sampleStr = '[' + ','.join([str(i) for i in sample5Df.to_dict('records')]) + ']'
        sampleStr = str(sampleStr).replace("\'", "\"")
        sampleStr = sampleStr.replace("\": \"", "\":\"")
        sampleStr = sampleStr.replace("\", \"", "\",\"")
        sampleStr = sampleStr.replace("None", "\"None\"")
        #return sampleStr,uniqueNum
        if sampleStr is None:
            print('sampleStr error')
            return 'sampleStr error'
        else:
            #self.updateToMysql_SampleTable(enColName)
            return self.updateToMysql_SampleTable(','.join(enColName)), self.updateToMysql(sampleStr, uniqueNum)
            


