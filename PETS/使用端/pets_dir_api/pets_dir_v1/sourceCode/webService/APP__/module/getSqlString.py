#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import JsonSchema as js
from checkTemplete import getUserRule, getReplacePath


def getGenNumLevel(colInfo):
    # check colInfo schema
    schema = js.getGenNumLevelSchema()
    data = js.loadJson(colInfo,schema) # return None if error
    if data is None:
        return 'celery_gen_error_getSqlString_getGenNumLevel_json_not_found'

    # colInfo
    colName = data['colName']
    userRule = data['userRule'] #1,10,100...
    tmpStr = "getGenNumLevel_(" + colName + ", \"" + userRule + "\") as " + colName
    return tmpStr

def getGenNumLevelMinMax(colInfo, bound=False):
    # check colInfo schema
    schema = js.getGenNumLevelMinMaxSchema()
    data = js.loadJson(colInfo,schema) # return None if error
    if data is None:
        return 'celery_gen_error_getSqlString_getGenNumLevelMinMax_json_not_found'

    # colInfo
    colName = data['colName']
    userRule = data['userRule']
    min_bound, level, max_bound = userRule.split(',')
    tmpStr = "getGenNumLevel_(" + colName + ", \"" + level + "\") as " + colName
    if not bound:
        return tmpStr
    else:
        return min_bound, max_bound

def getGenDate(colInfo):
    # check colInfo schema
    schema = js.getGenDateSchema()
    data = js.loadJson(colInfo,schema) # return None if error
    if data is None:
        return 'celery_gen_error_getSqlString_getGenDate_json_not_found'

    # colInfo
    colName = data['colName']
    try:
        userRule = data['userRule'] #Y,Mo,D,H,Mi
    except UnicodeEncodeError:
        userRule = str(data['userRule'].encode('utf-8'))

    tmpStr = "getGenDate_(" + colName + ", \"" + userRule + "\") as " + colName
    return tmpStr


def getGenString(colInfo):
    # check colInfo schema
    schema = js.getGenStringSchema()
    data = js.loadJson(colInfo,schema) # return None if error
    if data is None:
        return 'celery_gen_error_getSqlString_getGenString_json_not_found'

    # colInfo
    colName = data['colName']
    userRule = data['userRule']
    beginPoint, endPoint = userRule.split('_')
    tmpStr = "getGenString_(" + colName + ", \"" + beginPoint + "\", \"" + endPoint+ "\") as " + colName
    return tmpStr


def getNogenerlize(colInfo):
    # check colInfo schema
    schema = js.getNogenerlizeSchema()
    data = js.loadJson(colInfo,schema) # return None if error

    if data is None:
        return #待討論

    colName = str(data['colName'])
    return colName


def getGenSHA1(colInfo):
    # check colInfo schema
    schema = js.getGenSHA1Schema()
    data = js.loadJson(colInfo,schema) # return None if error
    if data is None:
        return 'celery_gen_error_getSqlString_getGenSHA1_json_not_found'

    # colInfo
    colName = data['colName']
    tmpStr = "getGenSHA1_(" + colName + ") as " + colName
    return tmpStr


def getGenNumInterval(colInfo):
    # check colInfo schema
    schema = js.getGenNumIntervalSchema()
    data = js.loadJson(colInfo,schema) # return None if error
    if data is None:
        return 'celery_gen_error_getSqlString_getGenNumInterval_json_not_found'

    # colInfo
    colName = data['colName'] #str

    userRule = data['userRule']
    userRuleList = userRule.split('^')
    valueStart = list()
    valueEnd = list()
    toValue = list()
    for i in range(len(userRuleList)):
        start, end, to = userRuleList[i].split('_')
        valueStart.append(start)
        valueEnd.append(end)
        toValue.append(to)

    idx =0
    tmpValueStart='array('
    tmpValueEnd='array('
    tmpToValue='array('

    for i in range(len(toValue)):
        if idx==len(toValue)-1:
            try:
                tmpValueStart=tmpValueStart+'"'+str(valueStart[i])+'")'
            except UnicodeEncodeError:
                tmpValueStart=tmpValueStart+'"'+str(valueStart[i].encode('utf-8'))+'")'

            try:
                tmpValueEnd=tmpValueEnd+'"'+str(valueEnd[i])+'")'
            except UnicodeEncodeError:
                tmpValueEnd=tmpValueEnd+'"'+str(valueEnd[i].encode('utf-8'))+'")'

            try:
                tmpToValue=tmpToValue+'"'+str(toValue[i])+'")'
            except UnicodeEncodeError:
                tmpToValue=tmpToValue+'"'+str(toValue[i].encode('utf-8'))+'")'                   
        else:
            try:
                tmpValueStart=tmpValueStart+'"'+str(valueStart[i])+'",'
            except UnicodeEncodeError:
                tmpValueStart=tmpValueStart+'"'+str(valueStart[i].encode('utf-8'))+'",'
            try:
                tmpValueEnd=tmpValueEnd+'"'+str(valueEnd[i])+'",'
            except UnicodeEncodeError:
                tmpValueEnd=tmpValueEnd+'"'+str(valueEnd[i].encode('utf-8'))+'",'
            try:
                tmpToValue=tmpToValue+'"'+str(toValue[i])+'",'
            except UnicodeEncodeError:
                tmpToValue=tmpToValue+'"'+str(toValue[i].encode('utf-8'))+'",'                                        
                    
        idx=idx+1

    tmpStr = "getGenNumInterval_("+colName+","+tmpValueStart+","+tmpValueEnd+","+tmpToValue+") as "+colName
    return tmpStr

'''
def getGenAddress(colInfo):
    # check colInfo schema
    schema = js.getGenAddressSchema()
    data = js.loadJson(colInfo,schema) # return None if error
    if data is None:
        return 'celery_gen_error_getSqlString_getGenAddress_json_not_found'

    # colInfo
    colName = data['colName']
    level = data['level']

    #logic
    code = {'A':'縣',
            'B':'市',
            'C':'區',
            'D':'鄉',
            'E':'鎮',
            'F':'巷',
            'G':'號'}

    address = code[level]

    tmpStr = "getGenAddress_(" + colName + ", \"" + address + "\") as " + colName
    return tmpStr
'''


def getGenAddress(colInfo):
    # check colInfo schema
    schema = js.getGenAddressSchema()
    data = js.loadJson(colInfo,schema) # return None if error
    if data is None:
        return 'celery_gen_error_getSqlString_getGenAddress_json_not_found'

    # colInfo
    colName = data['colName']
    userRule = data['userRule']

    # userRule: 1~9

    tmpStr = "getGenAddress_(" + colName + ", \"" + userRule + "\") as " + colName
    return tmpStr



def getGenUdf(colInfo):
    # check colInfo schema
    schema = js.getGenUdfSchema()
    data = js.loadJson(colInfo,schema) # return None if error
    if data is None:
        return 'celery_gen_error_getSqlString_getGenUdf_json_not_found'

    # colInfo
    colName = data['colName']
    userRule = data['userRule'] # local file path

    if (os.path.isfile(userRule)):

        #autoGen, autoGenValue, userRule = getUserRule(userRule)
        autoGen, autoGenValue, level, userRule = getUserRule(userRule)
        if autoGen == 0:
            return 'celery_gen_error_getSqlString_getGenUdf: '+ autoGenValue

        replacePath = getReplacePath(userRule,level)
        if replacePath[:18] == 'checkTemplet_error':
            return 'celery_gen_error_getSqlString_getGenUdf: ' + replacePath

        tmpStr = "getGenUdf_(" + colName + ", \"" + replacePath + "\", \"" + autoGen + "\", \"" + autoGenValue + "\") as " + colName
        return tmpStr

    else:
        return 'celery_gen_error_file_not_found: '+userRule