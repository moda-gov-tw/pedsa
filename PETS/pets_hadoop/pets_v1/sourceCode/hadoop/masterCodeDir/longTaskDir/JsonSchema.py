from marshmallow import Schema, fields,pprint

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
    colNames = fields.List(fields.Str())
    #email = fields.Email()
   
#####received json file Schemas (end)###########       
 
def loadJson(jsonData, jsonSchema):
    #schema = UserSchema()
    #print jsonData
    errors = jsonSchema.validate(jsonData)
    pprint(errors)
    if len(errors) > 0:
        return None 
    result = jsonSchema.load(jsonData)
    #pprint(result.data)
    #print type(result.data)
    pprint(result.data)
    #print result.data["name"]
    #print result.errors["name"]
    return result.data
