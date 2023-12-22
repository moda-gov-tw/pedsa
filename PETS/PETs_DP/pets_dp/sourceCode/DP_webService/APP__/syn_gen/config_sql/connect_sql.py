#!/usr/bin/python
# -*- coding: utf-8 -*-

import pymysql
from .loginInfo import getConfig


def get_mysql(ip, port_, user_, pwd):

    if port_ == '':
        connection = pymysql.connect(host=ip,
                                     user=user_,
                                     password=pwd,
                                     charset='utf8mb4',
                                     #charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor
                                         )

    else:
        connection = pymysql.connect(host=ip,
                                     port=int(port_),
                                     user=user_,
                                     password=pwd,
                                     charset='utf8mb4',
                                     #charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor
                                         )
    cursor = connection.cursor()
    cursor.execute("set names utf8")
    return connection, cursor


class ConnectSQL:

    def __init__(self, user_input=None, pwd_input=None):
        # Connect to mysql
        ip, port_, user_, pwd, type_ = getConfig().getLoginMysql()
        ip = str(ip)
        port_ = str(port_)
        type_ = str(type_).lower()

        if user_input is None and pwd_input is None:
            user_ = str(user_)
            pwd = str(pwd)
        else:
            # for hash function with id and pwd
            user_ = str(user_input)
            pwd = str(pwd_input)

        sql_list = {
            'mysql': get_mysql(ip, port_, user_, pwd)
        }

        self.connection, self.cursor = sql_list[type_]

    def doSqlCommand(self, sqlStr):
        """
        Do SQL command
        :param sqlStr: string
        :return: dict
        """
        try:
            # execute sql code
            self.cursor.execute(sqlStr)

            result = self.cursor.fetchall() # fetchall

            # commit to mysql
            self.connection.commit()

            return {'msg': sqlStr, 'fetchall': result, 'result': 1}

        except Exception as e:
            return {'msg': str(e), 'result': 0}

    def insertValue(self,dbName, tblName, colsValue, createTime=True):
        """
        Invert colsValue to dbName.tblName
        :param dbName: string
        :param tblName: string
        :param colsValue: dict
        :return: dict()
        """
        try:
            # combine to sql command
            cols = [str(col) for col in colsValue]
            cols = ','.join(cols)

            values = list()
            for col in colsValue:
                if colsValue[col] == 'NULL':
                    values.append(str(colsValue[col]))
                else:
                    values.append("'" + str(colsValue[col]) + "'")
            #values = ["'"+str(colsValue[col])+"'" for col in colsValue]
            values = [col.strip('\n') for col in values]
            values = ','.join(values)

            sqlStr = "INSERT INTO {}.{} ".format(dbName, tblName)
            if createTime:
                sqlStr += "({},createtime) ".format(cols)
                sqlStr += "VALUES ({},now())".format(values)
            else:
                sqlStr += "({}) ".format(cols)
                sqlStr += "VALUES ({})".format(values)

            # execute sql code
            self.cursor.execute("set names utf8")
            self.cursor.execute(sqlStr)

            # commit to mysql
            self.connection.commit()

            return {'msg': sqlStr, 'result': 1}

        except Exception as e:
            return {'msg': str(e) + sqlStr, 'result': 0}

    def updateValue(self, dbName, tblName, conditions, setColsValue):
        """
        Update setColsValue to dbName.tblName by conditions
        :param dbName: string
        :param tblName: string
        :param conditions: dict
        :param setColsValue: dict
        :return: dict
        """
        try:
            values = list()
            for col in setColsValue:
                if setColsValue[col] == 'NULL':
                    values.append(str(col)+"="+setColsValue[col])
                else:
                    values.append(str(col)+"='"+str(setColsValue[col])+"'")
            values = ','.join(values)

            conditions = [str(col)+"='"+str(conditions[col])+"'" for col in conditions]
            conditions = ' AND '.join(conditions)

            sqlStr = "UPDATE {}.{} ".format(dbName, tblName)
            sqlStr = sqlStr + "SET {},updatetime = now()".format(values)
            sqlStr = sqlStr + " WHERE {}".format(conditions)

            # execute sql code
            self.cursor.execute("set names utf8")
            self.cursor.execute(sqlStr.encode('utf8'))
            print(sqlStr.encode('utf8'))

            # commit to mysql
            self.connection.commit()

            return {'msg': sqlStr, 'result': 1}

        except Exception as e:
            return {'msg': str(e) + sqlStr, 'result': 0}

    def deleteValue(self, dbName, tblName, colsValue):
        """
        Delete colsValue in dbName.tblName
        :param dbName: string
        :param tblName: string
        :param colsValue: dict
        :return: dict
        """
        try:
            values = [str(col)+"='"+str(colsValue[col])+"'" for col in colsValue]
            values = ' AND '.join(values)

            sqlStr = "DELETE FROM {}.{} ".format(dbName, tblName)
            sqlStr = sqlStr + "WHERE {}".format(values)  

            # execute sql code
            self.cursor.execute(sqlStr)

            # commit to mysql
            self.connection.commit()
            return {'msg': sqlStr, 'result': 1}

        except Exception as e:
            return {'msg': str(e), 'result': 0}


    def checkAvailable(self, projID, tblName):
        """
        Check whether tblName of projID is used or not
        :param projID: int
        :param tblName: string
        :return: dict
        """
        try:
            sqlStr = "SELECT * FROM DeIdService.T_ProjectTableJobStatus "
            sqlStr = sqlStr + "WHERE projID='{}' ".format(projID)
            sqlStr = sqlStr + "AND tblName='{}' ".format(tblName)
            sqlStr = sqlStr + "AND status > 0 "

            # execute sql code
            self.cursor.execute(sqlStr)

            # return True if tbl is used
            if self.cursor.fetchone() is None:
                return {'msg': sqlStr, 'result': 1, 'used': 0}
            else:
                return {'msg': sqlStr, 'result': 1, 'used': 1}

        except Exception as e:
            return {'msg': str(e), 'result': 0, 'used': None}

    def jobStart(self, projID, jobID, tblName, remark):
        """
        Start to use tblName of projID
        :param projID: int
        :param jobID: string
        :param tblName: string
        :param remark: string
        :return: dict
        """
        try:
            colsValue = {
                'projID': projID,
                'jobID': jobID,
                'tblName': tblName,
                'status': 1,
                'remark': remark
            }
            return self.insertValue('DeIdService', 'T_ProjectTableJobStatus', colsValue)

        except Exception as e:
            return {'msg': str(e), 'result': 0}
       
    def jobEnd(self, projID, jobID, tblName, remark):
        """
        Update the state of tblName of projID when job is finish
        :param projID: int
        :param jobID: string
        :param tblName: string
        :param remark: string
        :return: dict
        """
        try:
            conditions = {
                'projID': projID,
                'jobID': jobID,
                'tblName': tblName,
                'status': 1,
                'remark': remark
            }

            setColsValue = {
                'status': 0
            }
            return self.updateValue('DeIdService', 'T_ProjectTableJobStatus', conditions, setColsValue)

        except Exception as e:
            return {'msg': str(e), 'result': 0}

    def close(self):
        self.connection.close()

    def updateValueMysql(self, db_, tbl_, conditionDict, setValueDict):
        # Insert or Update
        try:
            tableListResult = self.checkValueExist(db_, tbl_, conditionDict)

            if tableListResult['result'] == 0:
                return {'msg': tableListResult['msg'], 'result': 0}

            elif tableListResult['msg']:
                # Update
                updateResult = self.updateValue(db_, tbl_, conditionDict, setValueDict)
                if updateResult['result'] == 1:
                    return {'msg': updateResult['msg'], 'result': 1}
                else:
                    err = 'errTable: Update to {0}.{1} fail: {2}'.format(db_, tbl_, updateResult['msg'])
                    return {'msg': str(err), 'result': 0}
            else:
                # Insert
                insertResult = self.insertValue(db_, tbl_, setValueDict, True)
                if insertResult['result'] == 1:
                    return {'msg': insertResult['msg'], 'result': 1}
                else:
                    err = 'errTable: Insert to {0}.{1} fail: {2}'.format(db_, tbl_, insertResult['msg'])
                    return {'msg': str(err), 'result': 0}
        except Exception as e:
            err = 'errTable: Insert or Update mysql fail, {0}'.format(str(e))
            return {'msg': str(err), 'result': 0}

    def checkValueExist(self, db_, tbl_, conditionDict):

        conditions = [str(col) + "='" + str(conditionDict[col]) + "'" for col in conditionDict]
        conditions = ' AND '.join(conditions)

        sqlCommand = """
        select * from {0}.{1}
        WHERE {2}
        """.format(db_, tbl_, conditions)

        sqlResult = self.doSqlCommand(sqlCommand)

        if sqlResult['result'] == 0:
            err = 'errTable: Check value exists {0}.{1} fail: {2}'.format(db_, tbl_, sqlResult['msg'])
            return {'msg': str(err), 'result': 0}
        elif sqlResult['result'] == 1 and len(sqlResult['fetchall']) > 0:
            return {'msg': True, 'result': 1}
        else:
            return {'msg': False, 'result': 1}


