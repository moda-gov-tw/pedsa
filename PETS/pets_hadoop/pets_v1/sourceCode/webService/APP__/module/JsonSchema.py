#!/usr/bin/python
# -*- coding: utf-8 -*-

from marshmallow import Schema, fields, pprint

######JSON Response (start)###########
class jsonResponse(object):
    def __init__(self, appId, tableName,timeComsume):
        self.appId = appId
        self.tableName = tableName
        self.timeConsume = timeComsume
        #self.created_at = dt.datetime.now()

class jsonResponseSchema(Schema):
    appId = fields.Str()
    tableName = fields.Str()
    timeConsume = fields.Float()
    #created_at = fields.DateTime()
######JSON Response (end)###########
 
#####received json file Schemas (start)###########    
#1.   
class UserSchema(Schema):
    name = fields.Str()
    email = fields.Email()
    created_at = fields.DateTime()
#2. 
class tableInfoSchema(Schema):
    dbName = fields.Str()
    tableName = fields.Str()
    origColNames = fields.List(fields.Str())
    colNames = fields.List(fields.Str())
    keyNames = fields.List(fields.Str())
    QIcols = fields.List(fields.Str()) #joinData
    reqFunc = fields.Int() #distinctData
    #email = fields.Email()

#3. 
class joinInfoSchema(Schema):
    #dataInfo = fields.List(fields.Nested(tableInfoSchema, many=True))
    publicTableName = fields.Str()
    dataInfo = fields.Nested(tableInfoSchema, many=True)
    joinType = fields.Str()
    kValue = fields.Str()
#4.
class getGenNumLevelSchema(Schema):
    colName = fields.Str()
    userRule = fields.Str()
    apiName = fields.Str()

#5. 
class getNogenerlizeSchema(Schema):
    apiName = fields.Str()
    colName = fields.Str()
#6.
class getGenAddressSchema(Schema):
    apiName = fields.Str()
    colName = fields.Str()
    userRule = fields.Str()

#7.
class getGenStringSchema(Schema):
    apiName = fields.Str()
    colName = fields.Str()
    userRule = fields.Str()

#8.
class getGenDateSchema(Schema):
    apiName = fields.Str()
    colName = fields.Str()
    userRule = fields.Str()

#9.
class getGenEncAESHashSchema(Schema):
    apiName = fields.Str()
    colName = fields.Str()

#10.
class getGenSHA1Schema(Schema):
    apiName = fields.Str()
    colName = fields.Str()

#11.
class getGenNumIntervalSchema(Schema):
    apiName = fields.Str()
    colName = fields.Str()
    userRule = fields.Str()
    
#12.
class getGenUdfSchema(Schema):
    apiName = fields.Str()
    colName = fields.Str()
    userRule = fields.Str()

#13.
class getImportSchema(Schema):
    tblName = fields.Str()

#14.
class getExportSchema(Schema):
    pro_tb = fields.Str()
    finaltblName = fields.Str()
    location = fields.Str()

#15.
class getCheckTempleteSchema(Schema):
    userRule = fields.Str()

#16. 
class jobIDSchema(Schema):
    applicationID = fields.Str()
    #email = fields.Email()

#17.
class jsonBase64Schema(Schema):
    #dataInfo = fields.List(fields.Nested(tableInfoSchema, many=True))
    jsonBase64 = fields.Str()

#18.
class getCreateProjectSchema(Schema):
    user = fields.Str()
    dbName = fields.Str()

#19.
class getGenNumLevelMinMaxSchema(Schema):
    colName = fields.Str()
    userRule = fields.Str()
    apiName = fields.Str()
#####received json file Schemas (end)###########       
 
def loadJson(jsonData, jsonSchema):
    #schema = UserSchema()
    #print jsonData
    errors = jsonSchema.validate(jsonData)
    if errors:
        msg = "JaonSchema.loadJson error: {0}".format(errors)
        print(msg)
    if len(errors) > 0:
        return None 
    result = jsonSchema.load(jsonData)
    #pprint(result.data)
    #print type(result.data)
    #pprint(result.data)
    #print result.data["name"]
    #print result.errors["name"]
    return result.data
