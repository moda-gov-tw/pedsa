#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import os
import json
import base64
from app import app

from . import task_createFolder, task_preview, task_getFolder, task_exportData
from . import tasks , task_getMLutility, task_getGenerationData
from . import task_killProcess
from . import task_resetProject, task_deleteProject
from . import task_PETs_preview, task_PETs_exportData, task_PETs_MLutility

from flask_redis import FlaskRedis
from flask import render_template, request, jsonify,make_response
from celery import states
from .module.JsonSchema import jsonBase64Schema,loadJson,tableInfoSchema,getCheckTempleteSchema,jobIDSchema, genDataInfoSchema
from .module.base64convert import getJsonParser, encodeDic
from .module.checkTemplete import getReplacePath, getUserRule


redis_store = FlaskRedis(app)


def splitSymbol(list_):
    return [i.split('\n',1)[0] for i in list_]


@app.route('/')
def index():
    return render_template('index.html')


###original code (start)##############
@app.route('/hello_world_')
def hello_world():
    redis_store.set('hello-world-msg', 'Hello from Flask-Redis-Celery')
    view_count = redis_store.incr('hello-world-view-count')

    msg = redis_store.get('hello-world-msg').decode("utf-8")

    return msg + '.<br /><br />This page has been seen ' + str(view_count) + ' times.'


@app.route('/save_counter')
def counter_save():
    tasks.counter_save.delay()

    return 'Sent an async request to Celery, to order Redis to SAVE data to disk.'


@app.route('/reset_counter')
def counter_reset():
    tasks.counter_reset.delay()

    return 'Sent an async request to Celery, to order Redis to RESET data to disk.'
###original code (end)##############

#2020316:delete project
@app.route('/deleteProject_async', methods=['POST'])
def deleteProject_async():
    print("Start deleteProject_async")
    ts0 = time.time()
    app_ID=99999
    try:
        data_raw = request.get_json()
        print (data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'Request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))

    schema = jsonBase64Schema()

    data = loadJson(data_raw, schema) ##from curl
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return err_msg, 405

    jsonBase64__ = data["jsonBase64"]
    print("Get jsonBase64 from UI: {0}".format(jsonBase64__))
    print(json.loads(base64.b64decode(jsonBase64__)))

    #####task#####################################################
    task = task_deleteProject.deleteProject_longTask.apply_async((jsonBase64__,1)) 
    #############################################################################
    
    response = {}#python dict

    if True:        
        state_ = "test"
        while state_ != 'PROGRESS':
            ##########################################################
            deleteProject_longTask_task = task_deleteProject.deleteProject_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = deleteProject_longTask_task.state
            print (state_)

            response['celeyId'] = deleteProject_longTask_task.id

            if state_ == 'PROGRESS':
                state_ = 'SUCCESS'
                response['PID'] =task.info.get('PID')
                response['userID'] = task.info.get('userID')
                response['projStep']=task.info.get('projStep')
                response['projID'] = task.info.get('projID')
                response['projName']=task.info.get('projName')
                response['stateno'] = '1'
                break;
                
            #####FAIL#####################################################
            if state_ == 'FAIL':
                response['projStep']='Delete Project'
                try : 
                    response['stateno'] = task.info.get('stateno')
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    response['ERRMSG']=  task.info.get('Msg')
                except Exception as e:
                    response['ERRMSG']= "UNKNOWN"
                break;
            #####SUCESS#################################################
            if state_ == states.SUCCESS:
                state_ == 'FAIL'
                response['projStep']='Delete Project'
                try : 
                    response['stateno'] = task.info.get('stateno')
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    response['ERRMSG']=  task.info.get('Msg')
                except Exception as e:
                    response['ERRMSG']= "UNKNOWN"
                break;    
            if state_ == states.FAILURE:
                print ('fail_')
                response['projStep']='Delete Project'
                response['err'] ='celery job fail -- '
                break;  
    ts1 = time.time()
    response['STATE'] = state_
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))

#2020316:reset project
@app.route('/resetProject_async', methods=['POST'])
def resetProject_async():
    print("Start resetProject_async")
    ts0 = time.time()
    app_ID=99999
    try:
        data_raw = request.get_json()
        print (data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'Request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))

    schema = jsonBase64Schema()

    data = loadJson(data_raw, schema) ##from curl
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return err_msg, 405

    jsonBase64__ = data["jsonBase64"]
    print("Get jsonBase64 from UI: {0}".format(jsonBase64__))
    print(json.loads(base64.b64decode(jsonBase64__)))

    #####task#####################################################
    task = task_resetProject.resetProject_longTask.apply_async((jsonBase64__,1)) 
    #############################################################################
    
    response = {}#python dict

    if True:        
        state_ = "test"
        while state_ != 'PROGRESS':
            ##########################################################
            resetProject_longTask_task = task_resetProject.resetProject_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = resetProject_longTask_task.state
            print (state_)

            response['celeyId'] = resetProject_longTask_task.id

            if state_ == 'PROGRESS':
                state_ = 'SUCCESS'
                response['PID'] =task.info.get('PID')
                response['userID'] = task.info.get('userID')
                response['projStep']=task.info.get('projStep')
                response['projID'] = task.info.get('projID')
                response['projName']=task.info.get('projName')
                response['stateno'] = '1'
                break;
                
            #####FAIL#####################################################
            if state_ == 'FAIL':
                response['projStep']='Reset Project'
                try : 
                    response['stateno'] = task.info.get('stateno')
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    response['ERRMSG']=  task.info.get('Msg')
                except Exception as e:
                    response['ERRMSG']= "UNKNOWN"
                break;
            #####SUCESS#################################################
            if state_ == states.SUCCESS:
                state_ == 'FAIL'
                response['projStep']='Reset Project'
                try : 
                    response['stateno'] = task.info.get('stateno')
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    response['ERRMSG']=  task.info.get('Msg')
                except Exception as e:
                    response['ERRMSG']= "UNKNOWN"
                break;    
            if state_ == states.FAILURE:
                print ('fail_')
                response['projStep']='Reset Project'
                response['err'] ='celery job fail -- '
                break;  
    ts1 = time.time()
    response['STATE'] = state_
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))


#20200207:kill process
@app.route('/killProcess_async', methods=['POST'])
def killProcess_async():
    print("Start killProcess_async")
    ts0 = time.time()
    app_ID=99999
    try:
        data_raw = request.get_json()
        print (data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'Request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))

    schema = jsonBase64Schema()#genDataInfoSchema()

    data = loadJson(data_raw, schema) ##1128from curl
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return err_msg, 405

    jsonBase64__ = data["jsonBase64"]
    print("Get jsonBase64 from UI: {0}".format(jsonBase64__))
    print(json.loads(base64.b64decode(jsonBase64__)))

    #####20181121, citc trace#####################################################
   #task = task_getGenerationData.getGenerationData_longTask.apply_async((projName, fileName, colNames_, keyName_)) #1224:pei
    
    task = task_killProcess.killProcess_longTask.apply_async((jsonBase64__,1),queue='hipri', routing_key='hipri:killProcess') #20191016
    #############################################################################
    
    response = {}#python dict
    #response['state'] = state

    if True:        
        state_ = "test"
        while state_ != 'PROGRESS':
            #####20181121, citc trace#####################################################
            killProcess_longTask_task = task_killProcess.killProcess_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = killProcess_longTask_task.state
            print (state_)
            #response['state'] = state_
            response['celeyId'] = killProcess_longTask_task.id
            #print state_
            if state_ == 'PROGRESS':
                state_ = 'SUCCESS'
                response['PID'] =task.info.get('PID')
                response['userID'] = task.info.get('userID')
                response['projStep']=task.info.get('projStep')
                response['projID'] = task.info.get('projID')
                response['projName']=task.info.get('projName')
                response['stateno'] = '1'
                break;
                
            #####2018014, citc add#####################################################
            if state_ == 'FAIL':
                #print 'fail_____'
                #print('testestest: '+task.info.get('stateno'))
                response['projStep']='kill Process'
                try : 
                    response['stateno'] = task.info.get('stateno')
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    #response['err'] ='spark job fail'
                    response['ERRMSG']=  task.info.get('Msg')
                except Exception as e:
                    response['ERRMSG']= "UNKNOWN"
                    #response['err'] ='spark job fail'
                break;
            #####2018014, citc add (end)#################################################
            if state_ == states.SUCCESS:
                #print 'fail_____'
                state_ == 'FAIL'
                response['projStep']='kill Process'
                try : 
                    response['stateno'] = task.info.get('stateno')
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    #response['err'] ='spark job fail'
                    response['ERRMSG']=  task.info.get('Msg')
                except Exception as e:
                    response['ERRMSG']= "UNKNOWN"
                    #response['err'] ='spark job fail'
                break;    
            if state_ == states.FAILURE:
                print ('fail_')
                response['projStep']='kill Process'
                #response['err'] ='spark job fail'
                response['err'] ='celery job fail -- '
                break;  
    ts1 = time.time()
    response['STATE'] = state_
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response)) 
#20191016:create Folder 
@app.route('/createFolder_async', methods=['POST'])
def createFolder_async():
    print("Start createFolder_async")
    ts0 = time.time()
    app_ID=99999
    try:
        data_raw = request.get_json()
        print (data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'Request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))

    schema = jsonBase64Schema()#genDataInfoSchema()

    data = loadJson(data_raw, schema) ##1128from curl
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return err_msg, 405

    jsonBase64__ = data["jsonBase64"]
    print("Get jsonBase64 from UI: {0}".format(jsonBase64__))
    print(json.loads(base64.b64decode(jsonBase64__)))

    #####20181121, citc trace#####################################################
   #task = task_getGenerationData.getGenerationData_longTask.apply_async((projName, fileName, colNames_, keyName_)) #1224:pei
    
    task = task_createFolder.createFolder_longTask.apply_async((jsonBase64__,1)) #20191016
    #############################################################################
    
    response = {}#python dict
    #response['state'] = state

    if True:        
        state_ = "test"
        while state_ != 'PROGRESS':
            #####20181121, citc trace#####################################################
            createFolder_longTask_task = task_createFolder.createFolder_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = createFolder_longTask_task.state
            print (state_)
            #response['state'] = state_
            response['celeyId'] = createFolder_longTask_task.id
            #print state_
            if state_ == 'PROGRESS':
                state_ = 'SUCCESS'
                response['PID'] =task.info.get('PID')
                response['userID'] = task.info.get('userID')
                response['projStep']=task.info.get('projStep')
                response['projID'] = task.info.get('projID')
                response['projName']=task.info.get('projName')
                response['stateno'] = '1'
                break;
                
            #####2018014, citc add#####################################################
            if state_ == 'FAIL':
                #print 'fail_____'
                #print('testestest: '+task.info.get('stateno'))
                response['projStep']='create folder'
                try : 
                    response['stateno'] = task.info.get('stateno')
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    #response['err'] ='spark job fail'
                    response['ERRMSG']=  task.info.get('Msg')
                except Exception as e:
                    response['ERRMSG']= "UNKNOWN"
                    #response['err'] ='spark job fail'
                break;
            #####2018014, citc add (end)#################################################
            if state_ == states.SUCCESS:
                #print 'fail_____'
                state_ == 'FAIL'
                response['projStep']='create folder'
                try : 
                    response['stateno'] = task.info.get('stateno')
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    #response['err'] ='spark job fail'
                    response['ERRMSG']=  task.info.get('Msg')
                except Exception as e:
                    response['ERRMSG']= "UNKNOWN"
                    #response['err'] ='spark job fail'
                break;    
            if state_ == states.FAILURE:
                print ('fail_')
                response['projStep']='create folder'
                #response['err'] ='spark job fail'
                response['err'] ='celery job fail -- '
                break;  
    ts1 = time.time()
    response['STATE'] = state_
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response)) 
####################################################
#20191224:getFolder
@app.route('/getFolder_async', methods=['POST'])
def getFolder_async():
    print("Start getFolder_async")
    ts0 = time.time()
    app_ID=99999
    try:
        data_raw = request.get_json()
        print (data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'Request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))

    schema = jsonBase64Schema()#genDataInfoSchema()

    data = loadJson(data_raw, schema) ##1128from curl
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return err_msg, 405

    jsonBase64__ = data["jsonBase64"]
    print("Get jsonBase64 from UI: {0}".format(jsonBase64__))
    print(json.loads(base64.b64decode(jsonBase64__)))

    #####20181121, citc trace#####################################################
   #task = task_getGenerationData.getGenerationData_longTask.apply_async((projName, fileName, colNames_, keyName_)) #1224:pei
    
    task = task_getFolder.getFolder_longTask.apply_async((jsonBase64__,1)) #20191016
    #############################################################################
    
    response = {}#python dict
    #response['state'] = state

    if True:        
        state_ = "test"
        while state_ != 'PROGRESS':
            #####20181121, citc trace#####################################################
            getFolder_longTask_task = task_getFolder.getFolder_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = getFolder_longTask_task.state
            print (state_)
            #response['state'] = state_
            response['celeyId'] = getFolder_longTask_task.id
            #print state_
            if state_ == 'PROGRESS':
                state_ = 'SUCCESS'
                response['PID'] =task.info.get('PID')
                response['userID'] = task.info.get('userID')
                response['projStep']=task.info.get('projStep')
                response['projID'] = task.info.get('projID')
                response['projName']=task.info.get('projName')
                response['fileNames']=task.info.get('fileNames')
                response['stateno'] = '1'
                break;
                
            #####2018014, citc add#####################################################
            if state_ == 'FAIL':
                #print 'fail_____'
                response['projStep']='get folder information'
                try : 
                    response['stateno'] = task.info.get('stateno')
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    #response['err'] ='spark job fail'
                    response['ERRMSG']=  task.info.get('Msg')
                except Exception as e:
                    response['ERRMSG']= "UNKNOWN"
                    #response['err'] ='spark job fail'

                break;
            #####2018014, citc add (end)#################################################
            if state_ == states.SUCCESS:
                response['PID'] =task.info.get('PID')
                response['userID'] = task.info.get('userID')
                response['projStep']=task.info.get('projStep')
                response['projID'] = task.info.get('projID')
                response['projName']=task.info.get('projName')
                response['fileNames']=task.info.get('fileNames')
                response['stateno'] = '1'
                break;    
            if state_ == states.FAILURE:
                #print 'fail_____'
                response['err'] ='celery job fail'
                break;  
    ts1 = time.time()
    response['STATE'] = state_
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))  

####################################################
#20191021:preview 
@app.route('/preview_async', methods=['POST'])
def preview_async():
    print("Start preview_async")
    ts0 = time.time()
    app_ID=99999
    try:
        data_raw = request.get_json()
        print (data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'Request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))

    schema = jsonBase64Schema()#genDataInfoSchema()

    data = loadJson(data_raw, schema) ##1128from curl
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return err_msg, 405

    jsonBase64__ = data["jsonBase64"]
    print("Get jsonBase64 from UI: {0}".format(jsonBase64__))
    print(json.loads(base64.b64decode(jsonBase64__)))

    #####20181121, citc trace#####################################################
   #task = task_getGenerationData.getGenerationData_longTask.apply_async((projName, fileName, colNames_, keyName_)) #1224:pei
    
    task = task_preview.preview_longTask.apply_async((jsonBase64__,1)) #20191016
    #############################################################################
    
    response = {}#python dict
    #response['state'] = state

    if True:        
        state_ = "test"
        while state_ != 'PROGRESS':
            #####20181121, citc trace#####################################################
            preview_longTask_task = task_preview.preview_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = preview_longTask_task.state
            print (state_)
            #response['state'] = state_
            response['celeyId'] = preview_longTask_task.id
            #print state_
            if state_ == 'PROGRESS':

                response['PID'] =task.info.get('PID')
                response['userID'] = task.info.get('userID')
                response['projStep']=task.info.get('projStep')
                response['projID'] = task.info.get('projID')
                response['projName']=task.info.get('projName')
                response['stateno'] = '1'
                break;
                
            #####2018014, citc add#####################################################
            if state_ == 'FAIL':
                #print 'fail_____'
                response['projStep']='preview'
                try : 
                    response['stateno'] = task.info.get('stateno')
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    #response['err'] ='spark job fail'
                    response['ERRMSG']=  task.info.get('Msg')
                except Exception as e:
                    response['ERRMSG']= "UNKNOWN"
                    #response['err'] ='spark job fail'

                break;
            #####2018014, citc add (end)#################################################
            if state_ == states.SUCCESS:
                state_ = "Fail"
                #print('testestest: '+task.info.get('stateno'))
                response['projStep']='preview'
                try : 
                    response['stateno'] = task.info.get('stateno')
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    #response['err'] ='spark job fail'
                    response['ERRMSG']=  task.info.get('Msg')
                except Exception as e:
                    response['ERRMSG']= "UNKNOWN"
                    #response['err'] ='spark job fail'
                break;     
            if state_ == states.FAILURE:
                #print 'fail_____'
                response['err'] ='celery job fail'
                break;  
    ts1 = time.time()
    response['STATE'] = state_
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response)) 
##################################################
#PETs_preview_async:20231124
@app.route('/PETs_preview_async', methods=['POST'])
def PETs_preview_async():
    print("Start PETs_preview_async")
    ts0 = time.time()
    app_ID=99999
    try:
        data_raw = request.get_json()
        print (data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'Request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))

    schema = jsonBase64Schema()#genDataInfoSchema()

    data = loadJson(data_raw, schema) ##1128from curl
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return err_msg, 405

    jsonBase64__ = data["jsonBase64"]
    print("Get jsonBase64 from UI: {0}".format(jsonBase64__))
    print(json.loads(base64.b64decode(jsonBase64__)))

    #####20181121, citc trace#####################################################   
    task = task_PETs_preview.PETs_preview_longTask.apply_async((jsonBase64__,1)) #20191016
    #############################################################################
    
    response = {}#python dict
    #response['state'] = state
    if True:        
        state_ = "test"
        while state_ != 'PROGRESS':
            #####20181121, citc trace#####################################################
            preview_longTask_task = task_PETs_preview.PETs_preview_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = preview_longTask_task.state
            print (state_)
            #response['state'] = state_
            response['celeyId'] = preview_longTask_task.id
            #print state_
            if state_ == 'PROGRESS':
                response['PID'] =task.info.get('PID')
                response['userID'] = task.info.get('userID')
                response['projStep']=task.info.get('projStep')
                response['projID'] = task.info.get('projID')
                response['projName']=task.info.get('projName')
                response['stateno'] = '1'
                break;
                
            #####2018014, citc add#####################################################
            if state_ == 'FAIL':
                #print 'fail_____'
                response['projStep']='preview'
                try : 
                    response['stateno'] = task.info.get('stateno')
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    #response['err'] ='spark job fail'
                    response['ERRMSG']=  task.info.get('Msg')
                except Exception as e:
                    response['ERRMSG']= "UNKNOWN"
                    #response['err'] ='spark job fail'

                break;
            #####2018014, citc add (end)#################################################
            if state_ == states.SUCCESS:
                state_ = "Fail"
                #print('testestest: '+task.info.get('stateno'))
                response['projStep']='preview'
                try : 
                    response['stateno'] = task.info.get('stateno')
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    #response['err'] ='spark job fail'
                    response['ERRMSG']=  task.info.get('Msg')
                except Exception as e:
                    response['ERRMSG']= "UNKNOWN"
                    #response['err'] ='spark job fail'
                break;     
            if state_ == states.FAILURE:
                #print 'fail_____'
                response['err'] ='celery job fail'
                break;  
    ts1 = time.time()
    response['STATE'] = state_
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response)) 

##################################################    
#####citc, 20181121 add for  task_train_feature###
####citc, 20181128 Pei revise task_train_feature###
#####"http://140.110.30.46:50071/genData_async"###
##################################################
####citc, 20190610 Pei revise task_train_feature###
###http://140.96.178.108:5995/genData_async###
################################################
@app.route('/genData_async', methods=['POST'])
def genData_async():
    print("Start getGenerationData_async")
    ts0 = time.time()
    app_ID=99999
    try:
        data_raw = request.get_json()
        print (data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'Request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))


    schema = jsonBase64Schema()#genDataInfoSchema()
    #dbName = fields.Str()
    #tableName = fields.Str()
    data = loadJson(data_raw, schema) ##1128from curl
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return err_msg, 405
    #result = schema.load(data_raw)
    #pprint(result.data)
    #print (type(data))
    # pprint(data)
    #print data["dbName"]
    #print data["tableName"]

    jsonBase64__ = data["jsonBase64"]
    print("Get jsonBase64 from UI: {0}".format(jsonBase64__))
    print(json.loads(base64.b64decode(jsonBase64__)))

    ############citc add, 20181122###
    #1projName = data["projName"]
    #2fileName =  data["fileName"]
    #3keyName_ = data["keyName"]
    # tarCol = data["tarCol"] #1212:pei   
    # genBool = data["genBool"]   
    #4colNames_=data["colNames"]    
    #5print (colNames_)
    ###1128:pei
    # sampleBool = data["sampleBool"] 
    #################################

    #####20181121, citc trace#####################################################
    # task = task_train_feature.train_feature_longTask.apply_async((fileName, tarCol, genBool, colNames_, sampleBool))
    # task = task_getGenerationData.getGenerationData_longTask.apply_async((fileName, genBool, colNames_, sampleBool)) #1212:pei
    #task = task_getGenerationData.getGenerationData_longTask.apply_async((projName, fileName, colNames_, keyName_)) #1224:pei
    
    task = task_getGenerationData.getGenerationData_longTask.apply_async((jsonBase64__,1)) #1224:pei
    #############################################################################
    
    response = {}#python dict
    #response['state'] = state

    if True:        
        state_ = "test"
        while state_ != 'PROGRESS':
            #####20181121, citc trace#####################################################
            genData_longTask_task = task_getGenerationData.getGenerationData_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = genData_longTask_task.state
            print (state_)
            #response['state'] = state_
            response['celeyId'] = genData_longTask_task.id
            #print state_
            if state_ == 'PROGRESS':
                # if task.info.get('jobID') is None:
                #     response['err'] ='spark job fail'
                #     break
                
                #if task.info.get('verify') is None:
                #    response['err'] ='verify job fail'
                #    break   


                #if task.info.get('kTable') is None:
                #    response['err'] ='spark job fail'
                #    break    


                # response['spark_jobID'] =task.info.get('jobID')
                #response['verify'] =task.info.get('verify')
                #response['synPath'] =task.info.get('synPath')
                #response['kTable'] =task.info.get('kTable')
                response['PID'] =task.info.get('PID')
                response['userID'] = task.info.get('userID')
                response['projStep']=task.info.get('projStep')
                response['projID'] = task.info.get('projID')
                response['stateno'] = '1'
                #print task.info
                #print(kcheck_longTask_task.backend)
                #self.update_state(state=states.PENDING)
                break;
                
            #####2018014, citc add#####################################################
            if state_ == 'FAIL':
                response['projStep']='GAN'
                try : 
                    response['stateno'] = task.info.get('stateno')
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    #response['err'] ='spark job fail'
                    response['ERRMSG']=  task.info.get('Msg')
                except Exception as e:
                    response['ERRMSG']= "UNKNOWN"
                    #response['err'] ='spark job fail'
                break;
            #####2018014, citc add (end)#################################################
            if state_ == states.SUCCESS:
                state_ = "Fail"
                #print('testestest: '+task.info.get('stateno'))
                response['projStep']='GAN'
                try : 
                    response['stateno'] = task.info.get('stateno')
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    #response['err'] ='spark job fail'
                    response['ERRMSG']=  task.info.get('Msg')
                except Exception as e:
                    response['ERRMSG']= "UNKNOWN"
                    #response['err'] ='spark job fail'
                break;
            if state_ == states.FAILURE:
                #print 'fail_____'
                response['err'] ='celery job fail'
                break;  
    #print(task.get(on_message=on_raw_message, propagate=False))
    #return task.id#jsonify({}), 202, {'Location': url_for('taskstatus',   task_id=task.id)}
    #print 'state_ is'
    #print state_ (SUCCESS)
    ts1 = time.time()
    response['STATE'] = state_
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response)) 

@app.route('/MLutility_async', methods=['POST'])
def MLutility_async():
    print("Start MLutility_async")
    ts0 = time.time()
    app_ID=99999
    try:
        data_raw = request.get_json()
        #print (data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'Request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))


    schema = jsonBase64Schema()#genDataInfoSchema()
    #dbName = fields.Str()
    #tableName = fields.Str()
    data = loadJson(data_raw, schema) ##1128from curl
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return err_msg, 405
    #result = schema.load(data_raw)
    #pprint(result.data)
    #print (type(data))
    # pprint(data)
    #print data["dbName"]
    #print data["tableName"]

    jsonBase64__ = data["jsonBase64"]
    print("Get jsonBase64 from UI: {}".format(jsonBase64__))
    print(json.loads(base64.b64decode(jsonBase64__)))

    ############citc add, 20181122###
    #1projName = data["projName"]
    #2fileName =  data["fileName"]
    #3keyName_ = data["keyName"]
    # tarCol = data["tarCol"] #1212:pei   
    # genBool = data["genBool"]   
    #4colNames_=data["colNames"]    
    #5print (colNames_)
    ###1128:pei
    # sampleBool = data["sampleBool"] 
    #################################

    #####20181121, citc trace#####################################################
    # task = task_train_feature.train_feature_longTask.apply_async((fileName, tarCol, genBool, colNames_, sampleBool))
    # task = task_getMLutility.getMLutility_longTask.apply_async((fileName, genBool, colNames_, sampleBool)) #1212:pei
    #task = task_getMLutility.getMLutility_longTask.apply_async((projName, fileName, colNames_, keyName_)) #1224:pei
    
    task = task_getMLutility.getMLutility_longTask.apply_async((jsonBase64__,1)) #1224:pei
    #############################################################################
    
    response = {}#python dict
    #response['state'] = state

    if True:        
        state_ = "test"
        while state_ != 'PROGRESS':
            #####20181121, citc trace#####################################################
            MLutility_longTask_task = task_getMLutility.getMLutility_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = MLutility_longTask_task.state
            print (state_)
            #response['state'] = state_
            #response['celeryId'] = MLutility_longTask_task.id
            if state_ == 'PROGRESS':
                response['PID'] =task.info.get('PID')
                response['userID'] = task.info.get('userID')
                response['projID'] = task.info.get('projID')
                response['projName']=task.info.get('projName')
                response['celeryId'] = task.info.get('celeryId')               
                #response['targetCols'] = task.info.get('targetCols')
                response['projStep'] = 'MLutility'
                response['state'] = '0'
                print(response)
                break;
                
            #####2018014, citc add#####################################################
            if state_ == 'FAIL':
                response['projStep']='MLutility'
                try : 
                    response['stateno'] = task.info.get('stateno')
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    #response['err'] ='spark job fail'
                    response['ERRMSG']=  task.info.get('Msg')
                except Exception as e:
                    response['ERRMSG']= "UNKNOWN"
                    #response['err'] ='spark job fail'
                break;
            #####2018014, citc add (end)#################################################
            if state_ == states.SUCCESS:
                state_ = "Fail"
                #print('testestest: '+task.info.get('stateno'))
                response['projStep']='MLutility'
                try : 
                    response['stateno'] = task.info.get('stateno')
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    #response['err'] ='spark job fail'
                    response['ERRMSG']=  task.info.get('Msg')
                except Exception as e:
                    response['ERRMSG']= "UNKNOWN"
                    #response['err'] ='spark job fail'
                break;    
            if state_ == states.FAILURE:
                #print 'fail_____'
                response['err'] ='celery job fail'
                break;  
    #print(task.get(on_message=on_raw_message, propagate=False))
    #return task.id#jsonify({}), 202, {'Location': url_for('taskstatus',   task_id=task.id)}
    #print 'state_ is'
    #print state_ (SUCCESS)
    ts1 = time.time()
    response['time_async'] =str(ts1-ts0)
    response['STATE'] = state_
    return make_response(jsonify(response))

@app.route('/exportData_async', methods=['POST'])
def exportData_async():
    print("Start exportData_async")
    ts0 = time.time()
    app_ID=99999
    try:
        data_raw = request.get_json()
        #print (data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'Request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = '-1'
        response['errMsg'] = errMsg
        return make_response(jsonify(response))


    schema = jsonBase64Schema()#genDataInfoSchema()
    #dbName = fields.Str()
    #tableName = fields.Str()
    data = loadJson(data_raw, schema) ##1128from curl
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return err_msg, 405
    #result = schema.load(data_raw)
    #pprint(result.data)
    #print (type(data))
    # pprint(data)
    #print data["dbName"]
    #print data["tableName"]

    jsonBase64__ = data["jsonBase64"]
    print("Get jsonBase64 from UI: {}".format(jsonBase64__))
    print(json.loads(base64.b64decode(jsonBase64__)))

    ############citc add, 20181122###
    #1projName = data["projName"]
    #2fileName =  data["fileName"]
    #3keyName_ = data["keyName"]
    # tarCol = data["tarCol"] #1212:pei   
    # genBool = data["genBool"]   
    #4colNames_=data["colNames"]    
    #5print (colNames_)
    ###1128:pei
    # sampleBool = data["sampleBool"] 
    #################################
    task = task_exportData.exportData_longTask.apply_async((jsonBase64__,1)) #1224:pei
    #############################################################################

    response = {}#python dict
    #response['state'] = state

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####20181121, citc trace#####################################################
            exportData_longTask_task = task_exportData.exportData_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = exportData_longTask_task.state
            print (state_)
            #response['state'] = state_
            #response['celeryId'] = MLutility_longTask_task.id
            if state_ == 'PROGRESS':
                # if task.info.get('jobID') is None:
                #     response['err'] ='spark job fail'
                #     break

                #if task.info.get('verify') is None:
                #    response['err'] ='verify job fail'
                #    break   


                #if task.info.get('kTable') is None:
                #    response['err'] ='spark job fail'
                #    break    

                response['PID'] = task.info.get('PID')
                response['celeryId'] = task.info.get('celeryId')
                response['projName'] = task.info.get('projName')
                #response['targetCols'] = task.info.get('targetCols')
                response['projStep'] = 'Export data'
                response['userID'] = task.info.get('userID')
                response['projID'] = task.info.get('projID')
                response['state'] = '0'
                print(response)
                #print task.info
                #print(kcheck_longTask_task.backend)
                #self.update_state(state=states.PENDING)
                break;

            #####2018014, citc add#####################################################
            if state_ == 'FAIL':
                response['projStep'] = 'Export data'
                try:
                    response['stateno'] = task.info.get('stateno')
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    response['ERRMSG'] = task.info.get('Msg')
                except Exception as e:
                    response['ERRMSG'] = 'UNKNOWN'
                break;

            #####2018014, citc add (end)#################################################
            if state_ == states.SUCCESS:
                response['projStep'] = 'Export data'
                try:
                    response['stateno'] = task.info.get('stateno')
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    response['ERRMSG'] = task.info.get('Msg')
                except Exception as e:
                    response['ERRMSG'] = 'UNKNOWN'
                break;
            if state_ == states.FAILURE:
 
                #print 'fail_____'
                response['err'] ='celery job fail'
                break;
    #print(task.get(on_message=on_raw_message, propagate=False))
    #return task.id#jsonify({}), 202, {'Location': url_for('taskstatus',   task_id=task.id)}
    #print 'state_ is'
    #print state_ (SUCCESS)
    ts1 = time.time()
    response['STATE'] = state_
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))

########################################
#PETs_exportData_async:20231124
@app.route('/PETs_exportData_async', methods=['POST'])
def PETs_exportData_async():
    print("Start PETs_exportData_async")
    ts0 = time.time()
    app_ID=99999
    try:
        data_raw = request.get_json()
        #print (data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'Request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = '-1'
        response['errMsg'] = errMsg
        return make_response(jsonify(response))


    schema = jsonBase64Schema()#genDataInfoSchema()
    #dbName = fields.Str()
    #tableName = fields.Str()
    data = loadJson(data_raw, schema) ##1128from curl
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return err_msg, 405


    jsonBase64__ = data["jsonBase64"]
    print("Get jsonBase64 from UI: {}".format(jsonBase64__))
    print(json.loads(base64.b64decode(jsonBase64__)))

    #################################
    task = task_PETs_exportData.PETs_exportData_longTask.apply_async((jsonBase64__,1)) #1224:pei
    #############################################################################

    response = {}#python dict
    #response['state'] = state

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####20181121, citc trace#####################################################
            exportData_longTask_task = task_PETs_exportData.PETs_exportData_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = exportData_longTask_task.state
            print (state_)
            #response['state'] = state_
            #response['celeryId'] = MLutility_longTask_task.id
            if state_ == 'PROGRESS':
                response['PID'] = task.info.get('PID')
                response['celeryId'] = task.info.get('celeryId')
                response['projName'] = task.info.get('projName')
                #response['targetCols'] = task.info.get('targetCols')
                response['projStep'] = 'Export data'
                response['userID'] = task.info.get('userID')
                response['projID'] = task.info.get('projID')
                response['state'] = '0'
                print(response)
                break;
            #####2018014, citc add#####################################################
            if state_ == 'FAIL':
                response['projStep'] = 'Export data'
                try:
                    response['stateno'] = task.info.get('stateno')
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    response['ERRMSG'] = task.info.get('Msg')
                except Exception as e:
                    response['ERRMSG'] = 'UNKNOWN'
                break;
            #####2018014, citc add (end)#################################################
            if state_ == states.SUCCESS:
                response['projStep'] = 'Export data'
                try:
                    response['stateno'] = task.info.get('stateno')
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    response['ERRMSG'] = task.info.get('Msg')
                except Exception as e:
                    response['ERRMSG'] = 'UNKNOWN'
                break;
            if state_ == states.FAILURE:
 
                #print 'fail_____'
                response['err'] ='celery job fail'
                break;
    ts1 = time.time()
    response['STATE'] = state_
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))

############################################################
#PETs_MLutility_async:20231129
@app.route('/PETs_MLutility_async', methods=['POST'])
def PETs_MLutility_async():
    print("Start PETs_MLutility_async")
    ts0 = time.time()
    app_ID=99999
    try:
        data_raw = request.get_json()
        #print (data_raw)
    except Exception as e:
        response = dict()
        errMsg = 'Request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))


    schema = jsonBase64Schema()#genDataInfoSchema()
    #dbName = fields.Str()
    #tableName = fields.Str()
    data = loadJson(data_raw, schema) ##1128from curl
    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return err_msg, 405
    #result = schema.load(data_raw)
    #pprint(result.data)
    #print (type(data))
    # pprint(data)
    #print data["dbName"]
    #print data["tableName"]

    jsonBase64__ = data["jsonBase64"]
    print("Get jsonBase64 from UI: {}".format(jsonBase64__))
    print(json.loads(base64.b64decode(jsonBase64__)))

    ############citc add, 20181122###
    #1projName = data["projName"]
    #2fileName =  data["fileName"]
    #3keyName_ = data["keyName"]
    # tarCol = data["tarCol"] #1212:pei   
    # genBool = data["genBool"]   
    #4colNames_=data["colNames"]    
    #5print (colNames_)
    ###1128:pei
    # sampleBool = data["sampleBool"] 
    #################################

    #####20181121, citc trace#####################################################
    # task = task_train_feature.train_feature_longTask.apply_async((fileName, tarCol, genBool, colNames_, sampleBool))
    # task = task_getMLutility.getMLutility_longTask.apply_async((fileName, genBool, colNames_, sampleBool)) #1212:pei
    #task = task_getMLutility.getMLutility_longTask.apply_async((projName, fileName, colNames_, keyName_)) #1224:pei
    
    task = task_PETs_MLutility.PETs_MLutility_longTask.apply_async((jsonBase64__,1)) 
    #############################################################################
    
    response = {}#python dict
    #response['state'] = state

    if True:        
        state_ = "test"
        while state_ != 'PROGRESS':
            #####20181121, citc trace#####################################################
            MLutility_longTask_task = task_PETs_MLutility.PETs_MLutility_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = MLutility_longTask_task.state
            print (state_)
            #response['state'] = state_
            #response['celeryId'] = MLutility_longTask_task.id
            if state_ == 'PROGRESS':
                response['PID'] =task.info.get('PID')
                response['userID'] = task.info.get('userID')
                response['projID'] = task.info.get('projID')
                response['projName']=task.info.get('projName')
                response['celeryId'] = task.info.get('celeryId')               
                #response['targetCols'] = task.info.get('targetCols')
                response['projStep'] = 'PETs_MLutility'
                response['state'] = '0'
                print(response)
                break;
                
            #####2018014, citc add#####################################################
            if state_ == 'FAIL':
                response['projStep']='PETs_MLutility'
                try : 
                    response['stateno'] = task.info.get('stateno')
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    #response['err'] ='spark job fail'
                    response['ERRMSG']=  task.info.get('Msg')
                except Exception as e:
                    response['ERRMSG']= "UNKNOWN"
                    #response['err'] ='spark job fail'
                break;
            #####2018014, citc add (end)#################################################
            if state_ == states.SUCCESS:
                state_ = "Fail"
                #print('testestest: '+task.info.get('stateno'))
                response['projStep']='PETs_MLutility'
                try : 
                    response['stateno'] = task.info.get('stateno')
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    #response['err'] ='spark job fail'
                    response['ERRMSG']=  task.info.get('Msg')
                except Exception as e:
                    response['ERRMSG']= "UNKNOWN"
                    #response['err'] ='spark job fail'
                break;    
            if state_ == states.FAILURE:
                #print 'fail_____'
                response['err'] ='celery job fail'
                break;  
    #print(task.get(on_message=on_raw_message, propagate=False))
    #return task.id#jsonify({}), 202, {'Location': url_for('taskstatus',   task_id=task.id)}
    #print 'state_ is'
    #print state_ (SUCCESS)
    ts1 = time.time()
    response['time_async'] =str(ts1-ts0)
    response['STATE'] = state_
    return make_response(jsonify(response))


# #####citc, 20180705 add##############
# @app.route('/killSparkJobB64', methods=['POST'])
# def killSparkJobB64():
#     print("Start killSparkJobB64")
#     try:
#         data_raw = request.get_json()
#     except Exception as e:
#         response = dict()
#         errMsg = 'request_error: ' + str(e)
#         errMsg = errMsg + ' ; request: {}'.format(request)
#         response['status'] = -1
#         response['errMsg'] = errMsg
#         return make_response(jsonify(response))

#     schema = jsonBase64Schema()
#     data = loadJson(data_raw, schema)
#     if data is None:
#         err_msg = "<p>Json file error '%s'</p>" % data_raw
#         return err_msg, 405
#     jsonBase64 = data["jsonBase64"]

#     jsonData = getJsonParser(jsonBase64)
#     print("Get jsonBase64 from UI: {0}".format(jsonBase64))
#     print(jsonData)

#     #print 'enter getSparkJobStatus_2'
#     schema = jobIDSchema()
#     #print 'enter getSparkJobStatus_3'
#     data = loadJson(jsonData, schema)
#     if data is None:
#         err_msg = "<p>Json file error '%s'</p>" % jsonData
#         return err_msg, 405
#     #print data
#     #print 'enter getSparkJobStatus_4'
#     jobID = data["applicationID"]
#     #print jobID
#     response = SparkJobManager.killSparkJob(jobID)
#     #print 'enter getSparkJobStatus_5'

#     base64_return = encodeDic(response)
#     print("Return base64: {0}".format(base64_return))
#     print(response)
#     return make_response(jsonify({'jsonBase64': base64_return}))


# #####citc, 20180705 add##############
# @app.route('/getSparkJobStatusB64', methods=['POST'])
# def getSparkJobStatusB64():
#     print("Start getSparkJobStatusB64")
#     try:
#         data_raw = request.get_json()
#     except Exception as e:
#         response = dict()
#         errMsg = 'request_error: ' + str(e)
#         errMsg = errMsg + ' ; request: {}'.format(request)
#         response['status'] = -1
#         response['errMsg'] = errMsg
#         return make_response(jsonify(response))

#     schema = jsonBase64Schema()
#     data = loadJson(data_raw, schema)
#     if data is None:
#         err_msg = "<p>Json file error '%s'</p>" % data_raw
#         return err_msg, 405
#     jsonBase64 = data["jsonBase64"]

#     jsonData = getJsonParser(jsonBase64)
#     print("Get jsonBase64 from UI: {0}".format(jsonBase64))
#     print(jsonData)

#     #print 'enter getSparkJobStatus_2'
#     schema = jobIDSchema()
#     #print 'enter getSparkJobStatus_3'
#     data = loadJson(jsonData, schema)
#     if data is None:
#         err_msg = "<p>Json file error '%s'</p>" % jsonData
#         return err_msg, 405
#     #print data
#     #print 'enter getSparkJobStatus_4'
#     jobID = data["applicationID"]
#     #print jobID
#     response = SparkJobManager.getSparkJobStatus(jobID)
#     #print 'enter getSparkJobStatus_5'
#     base64_return = encodeDic(response)
#     print("Return base64: {0}".format(base64_return))
#     print(response)
#     return make_response(jsonify({'jsonBase64': base64_return}))


# # update:20180625
# @app.route('/createProject', methods=['POST'])
# def createProject():
#     print("Start createProject")

#     ts0 = time.time()

#     response = dict()

#     response['celeryID'] = ''#str
#     response['status'] = ''#str (1: succeed, -1: fail )
#     response['errMsg'] = ''#str (spark:meta_ or celery:task.api)
#     response['projStep'] = 'createProject'#str
#     response['dbName'] = ''#str
#     response['tblName'] = ''#str

#     # decode base64
#     try:
#         data_raw = request.get_json()
#     except Exception as e:
#         errMsg = 'request_error: ' + str(e)
#         errMsg = errMsg + ' ; request: {}'.format(request)
#         response['status'] = -1
#         response['errMsg'] = errMsg
#         return make_response(jsonify(response))

#     schema = jsonBase64Schema()
#     data = loadJson(data_raw, schema)
#     if data is None:
#         err_msg = "<p>Json file error '%s'</p>" % data_raw
#         return err_msg, 405

#     jsonBase64 =  data["jsonBase64"]
#     print("Get jsonBase64 from UI: {0}".format(jsonBase64))
#     print(json.loads(base64.b64decode(jsonBase64)))

#     task = task_createProject.createProject_longTask.apply_async((jsonBase64,1))

#     if True:
#         state_ = "test"
#         while state_ != 'PROGRESS':
#             #####2018014, citc trace#####################################################
#             createProject_longTask_task = task_createProject.createProject_longTask.AsyncResult(task.id)
#             #########################################################################
#             state_ = createProject_longTask_task.state
#             #response['state'] = state_
#             response['celeryID'] = createProject_longTask_task.id
#             if state_ == 'PROGRESS':
#                 response['dbName'] = task.info.get('dbName').strip('\n')
#                 #response['tblName'] = task.info.get('tblName').strip('\n')
#                 response['status'] = '1'
#                 break

#             #####20180615, citc add#####################################################
#             if state_ == 'FAIL_CELERY':
#                 errMsg = task.info.get('errMsg')
#                 response['errMsg'] = errMsg
#                 response['status'] = '-1'
#                 break

#             #####2018014, citc add#####################################################
#             if state_ == 'FAIL_SPARK':
#                 #print 'fail_____'
#                 errMsg = task.info.get('errMsg')
#                 response['errMsg'] = errMsg
#                 response['status'] = '-1'
#                 break
#             #####2018014, citc add (end)#################################################
#             if state_ == states.SUCCESS:
#                 break
#             if state_ == states.FAILURE:
#                 #print 'fail_____'
#                 response['errMsg'] ='Celery job fail'
#                 response['status'] = '-1'
#                 break

#     ts1 = time.time()
#     response['time_async'] =str(ts1-ts0)
#     base64_return = encodeDic(response)
#     print("Return base64: {0}".format(base64_return))
#     print(response)
#     return make_response(jsonify({'jsonBase64':base64_return}))

# # update:20180625
# @app.route('/ExportFile', methods=['POST'])
# def ExportFile():
#     print("Start ExportFile")

#     ts0 = time.time()

#     response = dict()

#     response['celeryID'] = ''#str
#     response['status'] = ''#str (1: succeed, -1: fail )
#     response['errMsg'] = ''#str (spark:meta_ or celery:task.api)
#     response['projStep'] = 'export'#str (select, gen, join, distinct,single k checking,export,import)
#     response['dbName'] = ''#str
#     response['tblName'] = ''#str

#     # decode base64
#     try:
#         data_raw = request.get_json()
#     except Exception as e:
#         errMsg = 'request_error: ' + str(e)
#         errMsg = errMsg + ' ; request: {}'.format(request)
#         response['status'] = -1
#         response['errMsg'] = errMsg
#         return make_response(jsonify(response))

#     schema = jsonBase64Schema()
#     data = loadJson(data_raw, schema)
#     if data is None:
#         err_msg = "<p>Json file error '%s'</p>" % data_raw
#         return err_msg, 405

#     jsonBase64 =  data["jsonBase64"]
#     print("Get jsonBase64 from UI: {0}".format(jsonBase64))
#     print(json.loads(base64.b64decode(jsonBase64)))

#     task = task_export.export_longTask.apply_async((jsonBase64, 1))

#     if True:
#         state_ = "test"
#         while state_ != 'PROGRESS':
#             #####2018014, citc trace#####################################################
#             export_longTask_task = task_export.export_longTask.AsyncResult(task.id)
#             #########################################################################
#             state_ = export_longTask_task.state
#             #print(state_)
#             #response['state'] = state_
#             response['celeryID'] = export_longTask_task.id
#             if state_ == 'PROGRESS':
#                 response['dbName'] = task.info.get('dbName').strip('\n')
#                 response['tblName'] = task.info.get('tblName').strip('\n')
#                 response['sparkAppID'] = task.info.get('sparkAppID').strip('\n')
#                 response['status'] = '1'
#                 break

#             #####20180615, citc add#####################################################
#             if state_ == 'FAIL_CELERY':
#                 errMsg = task.info.get('errMsg')
#                 response['errMsg'] = errMsg
#                 response['status'] = '-1'
#                 break

#             #####2018014, citc add#####################################################
#             if state_ == 'FAIL_SPARK':
#                 #print 'fail_____'
#                 errMsg = task.info.get('errTable')
#                 response['errMsg'] = errMsg
#                 response['status'] = '-1'
#                 break
#             #####2018014, citc add (end)#################################################
#             if state_ == states.SUCCESS:
#                 break
#             if state_ == states.FAILURE:
#                 #print 'fail_____'
#                 response['errMsg'] ='Celery job fail'
#                 response['status'] = '-1'
#                 break

#     ts1 = time.time()
#     response['time_async'] = str(ts1-ts0)
#     base64_return = encodeDic(response)
#     print("Return base64: {0}".format(base64_return))
#     print(response)
#     return make_response(jsonify({'jsonBase64':base64_return}))


# #update:20180622
# @app.route('/getServerFolder', methods=['POST'])
# def getServerFolder():
#     print("Start getServerFolder")

#     #return json
#     response = dict()
#     response['status'] = 1

#     # get information
#     try:
#         data_raw = request.get_json()
#         schema = jsonBase64Schema()
#         data = loadJson(data_raw, schema)
#         if data is None:
#             err_msg = "<p>Json file error '%s'</p>" % data_raw
#             return err_msg, 405
#         jsonBase64 =  data["jsonBase64"]

#         jsonAll = getJsonParser(jsonBase64) # projID, projStep, projName
#         print("Get jsonBase64 from UI: {0}".format(jsonBase64))
#         print(jsonAll)

#         if isinstance(jsonAll, str):
#             errMsg = 'getJsonParer_error: ' + str(jsonAll)
#             response['status'] = -1
#             response['errMsg'] = errMsg
#             base64_return = encodeDic(response)
#             return make_response(jsonify({'jsonBase64': base64_return}))

#         projID = jsonAll['projID']
#         projStep = jsonAll['projStep']
#         projName = jsonAll['projName']
#     except Exception as e:
#         errMsg = 'getJsonParer_error: ' + str(e)
#         response['status'] = -1
#         response['errMsg'] = errMsg
#         base64_return = encodeDic(response)
#         return make_response(jsonify({'jsonBase64':base64_return}))

#     # check projStep
#     if projStep != 'getServerFolder':
#         errMsg = 'celery_import_error_projStep_is_not_import'
#         response['status'] = -1
#         response['errMsg'] = "Mysql_connect_error_" + errMsg
#         base64_return = encodeDic(response)
#         return make_response(jsonify({'jsonBase64':base64_return}))

#     # connect to mysql
#     try:
#         #combine commands
#         #serverPath = "/user/itribd/import"
#         #serverPath = "hdfs://Aquila-nn2.citc.local/user/gau/import"

#         type_ = 'local'
#         serverPath = getConfig().getImportPath(type_)
#         filePath = os.path.join(serverPath, projName, '*/*')
#         if type_ == 'hdfs':
#             cmdStr = 'hadoop fs -stat "%n" ' + filePath
#         else:
#             cmdStr = 'stat --format "%n" ' + filePath


#         ssh_for_bash = ssh_hdfs()
#         stdin, stdout, stderr = ssh_for_bash.callCommand_output(cmdStr, addPath=False)


#     except Exception as e:
#         errMsg = 'ssh_connect_error: ' + str(e)
#         response['status'] = -1
#         response['errMsg'] = errMsg
#         base64_return = encodeDic(response)
#         return make_response(jsonify({'jsonBase64':base64_return}))

#     # collect server folder
#     try:
#         folders = []
#         for line in stdout.readlines():
#             print(line)
#             folders.append(line.strip('\n'))
#             #folders.append(line[:-1])
#         response['folders'] = ';'.join(folders)


#     except Exception as e:
#         errMsg = 'collect_server_folder_error: ' + str(e)
#         response['status'] = -1
#         response['errMsg'] = "Mysql_connect_error_" + errMsg
#         base64_return = encodeDic(response)
#         return make_response(jsonify({'jsonBase64':base64_return}))

#     if len(response['folders']) == 0:
#         response['status'] = -1
#         response['errMsg'] = "Cannot find any files in this project"
#         base64_return = encodeDic(response)
#         return make_response(jsonify({'jsonBase64':base64_return}))

#     base64_return = encodeDic(response)
#     print("Return base64: {0}".format(base64_return))
#     print(response)
#     return make_response(jsonify({'jsonBase64':base64_return}))
#     #return make_response(jsonify(response))


# #update 20180615
# @app.route('/ImportFile', methods=['POST'])
# def ImportFile():
#     print("Start ImportFile")
#     ts0 = time.time()
#     try:
#         data_raw = request.get_json()
#     except Exception as e:
#         response = dict()
#         errMsg = 'request_error: ' + str(e)
#         errMsg = errMsg + ' ; request: {}'.format(request)
#         response['status'] = -1
#         response['errMsg'] = errMsg
#         return make_response(jsonify(response))

#     schema = jsonBase64Schema()
#     data = loadJson(data_raw, schema)
#     if data is None:
#         err_msg = "<p>Json file error '%s'</p>" % data_raw
#         return err_msg, 405

#     jsonBase64 =  data["jsonBase64"]
#     print("Get jsonBase64 from UI: {0}".format(jsonBase64))
#     print(json.loads(base64.b64decode(jsonBase64)))

#     task = task_import.import_longTask.apply_async((jsonBase64, 1))

#     response = dict()
#     response['sparkAppID'] = ''#str
#     response['celeryID'] = ''#str
#     response['status'] = ''#str (1: succeed, -1: fail )
#     response['errMsg'] = ''#str (spark:meta_ or celery:task.api)
#     response['projStep'] = 'import'#str (select, gen, join, distinct,single k checking,export,import)
#     response['dbName'] = ''#str
#     response['tblNames'] = ''#str


#     if True:
#         state_ = "test"
#         while state_ != 'PROGRESS':
#             #####2018014, citc trace#####################################################
#             import_longTask_task = task_import.import_longTask.AsyncResult(task.id)
#             #########################################################################
#             state_ = import_longTask_task.state
#             #response['state'] = state_
#             response['celeryID'] = import_longTask_task.id
#             if state_ == 'PROGRESS':
#                 if task.info.get('sparkAppID') is None:
#                     #response['err'] ='spark job fail'
#                     response['errMsg'] ='spark context fail'
#                     response['status'] = '-1'
#                     break

#                 response['sparkAppID'] = task.info.get('sparkAppID').strip('\n')
#                 response['dbName'] = task.info.get('dbName').strip('\n')
#                 response['tblNames'] = task.info.get('tblNames').strip('\n')
#                 response['status'] = '1'
#                 break

#             #####20180615, citc add#####################################################
#             if state_ == 'FAIL_CELERY':
#                 errMsg = task.info.get('errMsg')
#                 response['errMsg'] = errMsg
#                 response['status'] = '-1'
#                 break

#             #####2018014, citc add#####################################################
#             if state_ == 'SparkError':
#                 response['errMsg'] = task.info.get('errTable')
#                 response['sparkAppID'] = task.info.get('sparkAppID')
#                 response['status'] = '-1'
#                 break
#             #####2018014, citc add (end)#################################################
#             if state_ == states.SUCCESS:
#                 break

#             if state_ == states.FAILURE:
#                 #print 'fail_____'
#                 try:
#                     errMsg = task.info.get('errMsg')
#                     response['errMsg'] = errMsg
#                     response['status'] = '-1'
#                     break
#                 except Exception as e:
#                     response['errMsg'] = str(e)
#                     response['status'] = '-1'
#                     break

#     ts1 = time.time()
#     response['time_async'] = str(ts1-ts0)
#     base64_return = encodeDic(response)
#     print("Return base64: {0}".format(base64_return))
#     print(response)
#     return make_response(jsonify({'jsonBase64':base64_return}))


# #update:20180614
# @app.route('/checkTemplete', methods=['POST'])
# def checkTemplete():
#     print("Start checkTemplete")

#     #return json
#     response = dict()
#     response['status'] = 1
#     response['errMsg'] = None
#     try:
#         data_raw = request.get_json()
#     except Exception as e:
#         errMsg = 'request_error: ' + str(e)
#         errMsg = errMsg + ' ; request: {}'.format(request)
#         response['status'] = -1
#         response['errMsg'] = errMsg
#         print(errMsg)
#         return make_response(jsonify(response))
#     schema = jsonBase64Schema()
#     data = loadJson(data_raw, schema)
#     if data is None:
#         err_msg = "<p>Json file error '%s'</p>" % data_raw
#         print(err_msg)
#         return err_msg, 405
#     jsonBase64 =  data["jsonBase64"]

#     jsonAll = getJsonParser(jsonBase64)
#     print("Get jsonBase64 from UI: {0}".format(jsonBase64))
#     print(jsonAll)

#     # check mainInfo
#     schema = getCheckTempleteSchema()
#     data = loadJson(jsonAll['mainInfo'],schema) # return None if error
#     if data is None:
#         err_msg = "<p>Json file error '%s'</p>" % jsonAll['mainInfo']
#         print(err_msg)
#         return err_msg, 405

#     userRulePath = data['userRule']

#     #check if file exist
#     if (os.path.isfile(userRulePath)) == False:
#         response['status'] = -1
#         response['errMsg'] = 'celery_gen_error_file_not_found: '+userRulePath
#         return make_response(jsonify(response))

#     # get user rule
#     try:
#         autoGen, autoGenValue, level, userRule = getUserRule(userRulePath)
#     except Exception as e:
#         response['status'] = -1
#         response['errMsg'] = 'getUserRule error: ' + str(e)
#         print(response['errMsg'])
#         return make_response(jsonify(response))

#     if autoGen == 0:
#         response['status'] = -1
#         response['errMsg'] = 'celery_gen_error_getSqlString_getGenUdf: '+ autoGenValue
#         return make_response(jsonify(response))


#     # get replace path
#     try:
#         replacePath = getReplacePath(userRule, 0)
#     except Exception as e:
#         response['status'] = -1
#         response['errMsg'] = 'getReplacePath error: ' + str(e)
#         print(response['errMsg'])
#         return make_response(jsonify(response))


#     if replacePath[:18] == 'checkTemplete_error':
#         response['status'] = -1
#         response['errMsg'] = 'gen_error_getSqlString_getGenUdf_' + replacePath
#     else:
#         response['userRule'] = replacePath

#     base64_return = encodeDic(response)
#     print("Return base64: {0}".format(base64_return))
#     print(response)
#     return make_response(jsonify({'jsonBase64':base64_return}))

# #update:20180614
# @app.route('/Generalization_async', methods=['POST'])
# def Generalization_async():
#     print("Start Generalization_async")

#     ts0 = time.time()
#     try:
#         data_raw = request.get_json()
#     except Exception as e:
#         response = dict()
#         errMsg = 'request_error: ' + str(e)
#         errMsg = errMsg + ' ; request: {}'.format(request)
#         response['status'] = -1
#         response['errMsg'] = errMsg
#         return make_response(jsonify(response))

#     schema = jsonBase64Schema()
#     data = loadJson(data_raw, schema)
#     if data is None:
#         err_msg = "<p>Json file error '%s'</p>" % data_raw
#         return err_msg, 405

#     jsonBase64 = data["jsonBase64"]
#     print("Get jsonBase64 from UI: {0}".format(jsonBase64))
#     print(json.loads(base64.b64decode(jsonBase64)))

#     task = task_getGenTbl.generalization_longTask.apply_async((jsonBase64, 1))

#     response = dict()
#     response['sparkAppID'] = ''#str
#     response['celeryID'] = ''#str
#     response['status'] = ''#str (1: succeed, -1: fail )
#     response['errMsg'] = ''#str (spark:meta_ or celery:task.api)
#     response['projStep'] = 'gen'#str (select, gen, join, distinct,single k checking,export,import)
#     response['dbName'] = ''#str
#     response['tblName'] = ''#str

#     if True:
#         state_ = "test"
#         while state_ != 'PROGRESS':
#             #####2018014, citc trace#####################################################
#             generalization_longTask_task = task_getGenTbl.generalization_longTask.AsyncResult(task.id)
#             #########################################################################
#             state_ = generalization_longTask_task.state
#             #print state_
#             #response['state'] = state_
#             response['celeryID'] = generalization_longTask_task.id
#             #print(state_)
#             if state_ == 'PROGRESS':
#                 if task.info.get('sparkAppID') is None:
#                     #response['err'] ='spark job fail'
#                     response['errMsg'] ='spark context fail'
#                     response['status'] = '-1'
#                     break

#                 response['sparkAppID'] =task.info.get('sparkAppID').strip('\n')
#                 response['dbName'] = task.info.get('dbName').strip('\n')
#                 response['tblName'] = task.info.get('tblName').strip('\n')
#                 response['status'] = '1'
#                 print(response)
#                 break

#             #####2018014, citc add (end)#################################################
#             if state_ == states.SUCCESS:
#                 break

#             if state_ == 'FAIL_CELERY':
#                 errMsg = task.info.get('errMsg')
#                 response['errMsg'] = errMsg
#                 response['status'] = '-1'
#                 break

#             if state_ == 'FAIL_SPARK':
#                 #print 'fail_____'
#                 errMsg = task.info.get('errTable')
#                 response['errMsg'] = errMsg
#                 response['status'] = '-1'
#                 break

#             if state_ == states.FAILURE:
#                 #print 'fail_____'
#                 try:
#                     errMsg = task.info.get('errMsg')
#                     response['errMsg'] = errMsg
#                     break
#                 except Exception as e:
#                     response['errMsg'] ='Celery job fail: {0}'.format(str(e))
#                     break

#     ts1 = time.time()
#     response['time_async'] =str(ts1-ts0)
#     base64_return = encodeDic(response)
#     print("Return base64: {0}".format(base64_return))
#     print(response)
#     return make_response(jsonify({'jsonBase64':base64_return}))


# @app.route('/getDistinctData_async', methods=['POST'])
# def getDistinctData_async():
#     print("Start getDistinctData_async")

#     ########################################
#     jarFileName = '/app/sqljdbc4-2.0.jar'
#     #########################################

#     ts0 = time.time()
#     try:
#         input_ = request.get_json()
#         print(input_)
#         print('***request : '+str(request))
#         print(request.form.to_dict('records'))
#         print(request.args.to_dict('records'))

#     except Exception as e:
#         response = dict()
#         errMsg = 'request_error: ' + str(e)
#         errMsg = errMsg + ' ; request: {}'.format(request)
#         print(errMsg)
#         response['status'] = -1
#         response['errMsg'] = errMsg
#         return make_response(jsonify(response))

#     schema = jsonBase64Schema()
#     data = loadJson(input_, schema)

#     if data is None:
#         err_msg = "<p>Json file error</p>"
#         return err_msg, 405

#     jsonBase64__ = data["jsonBase64"]
#     print("Get jsonBase64 from UI: {0}".format(jsonBase64__))
#     print(json.loads(base64.b64decode(jsonBase64__)))

#     task = task_getDistinctData.getDistinctData_longTask.apply_async((jsonBase64__, jarFileName))

#     response = dict()
#     response['jobID'] = ''
#     response['sparkAppID'] = ''
#     response['celeryID'] = ''
#     response['status'] = ''
#     response['errMsg'] = ''
#     response['projStep'] = 'distinct'
#     response['dbName'] = ''
#     response['tblName'] = ''

#     if True:
#         state_ = "test"
#         while state_ != 'PROGRESS':
#             dis_longTask_task = task_getDistinctData.getDistinctData_longTask.AsyncResult(task.id)
#             #print dis_longTask_task
#             state_ = dis_longTask_task.state
#             #response['state'] = state_
#             response['celeryID'] = dis_longTask_task.id
#             #print(state_)
#             if state_ == 'PROGRESS':
#                 if task.info.get('sparkAppID') is None:
#                     response['errMsg'] ='spark job fail'
#                     response['status'] = '-1'
#                     break

#                 response['sparkAppID'] = task.info.get('sparkAppID').strip()
#                 response['jobID'] = task.info.get('jobName').strip()
#                 response['status'] = '1'
#                 response['dbName'] = task.info.get('dbName').strip()
#                 response['tblName'] = task.info.get('tblName').strip()
#                 response['outTblName'] = splitSymbol(task.info.get('outTblNames'))
#                 #response['cols'] = task.info.get('cols').strip()
#                 #print task.info
#                 #print(kcheck_longTask_task.backend)
#                 #self.update_state(state=states.PENDING)
#                 break
#             if state_ == states.SUCCESS:
#                 break
#             if state_ == states.FAILURE:
#                 response['errMsg'] ='celery job fail'
#                 break
#     #print(task.get(on_message=on_raw_message, propagate=False))
#     #return task.id#jsonify({}), 202, {'Location': url_for('taskstatus',   task_id=task.id)}
#     ts1 = time.time()
#     response['time_async'] = str(ts1-ts0)
#     base64_return = encodeDic(response)
#     print("Return base64: {0}".format(base64_return))
#     print(response)
#     return make_response(jsonify({'jsonBase64':base64_return}))



# @app.route('/getJoinData_async', methods=['POST'])
# def getJoinData_async():
#     print("Start getJoinData_async")

#     ########################################
#     jarFileName='/app/sqljdbc4-2.0.jar'
#     #########################################

#     ts0 = time.time()
#     app_ID = 99999

#     try:
#         input_ = request.get_json()
#         #print input_
#     except Exception as e:
#         response = dict()
#         errMsg = 'request_error: ' + str(e)
#         errMsg = errMsg + ' ; request: {}'.format(request)
#         response['status'] = -1
#         response['errMsg'] = errMsg
#         return make_response(jsonify(response))

#     schema = jsonBase64Schema()
#     data = loadJson(input_, schema)
#     if data is None:
#         err_msg = "<p>Json file error '%s'</p>" % app_ID
#         return err_msg, 405

#     jsonBase64__ = data["jsonBase64"]
#     print("Get jsonBase64 from UI: {0}".format(jsonBase64__))
#     print(json.loads(base64.b64decode(jsonBase64__)))

#     task = task_getJoinData.getJoinData_longTask.apply_async((jsonBase64__, jarFileName))

#     response = dict()
#     response['jobID'] = ''
#     response['sparkAppID'] = ''
#     response['celeryID'] = ''
#     response['status'] = ''
#     response['errMsg'] = ''
#     response['projStep'] = 'join'
#     response['dbName'] = ''
#     response['tblName'] = ''

#     if True:
#         state_ = "test"
#         while state_ != 'PROGRESS':
#             join_longTask_task = task_getJoinData.getJoinData_longTask.AsyncResult(task.id)
#             state_ = join_longTask_task.state
#             #response['state'] = state_
#             response['celeryID'] = join_longTask_task.id
#             #print(state_)
#             if state_ == 'PROGRESS':
#                 if task.info.get('sparkAppID') is None:
#                     response['errMsg'] ='spark job fail'
#                     response['status'] = '-1'
#                     break

#                 response['sparkAppID'] = task.info.get('sparkAppID').strip('\n')
#                 response['jobID'] = task.info.get('jobName').strip('\n')
#                 response['status'] = '1'
#                 response['dbName'] = splitSymbol(task.info.get('dbName'))
#                 response['tblName'] = splitSymbol(task.info.get('tblName'))
#                 response['outTblName'] = task.info.get('outTblName').strip('\n')
#                 print(response)
#                 #response['cols'] = splitSymbol(task.info.get('cols'))
#                 #print task.info
#                 #print(kcheck_longTask_task.backend)
#                 #self.update_state(state=states.PENDING)
#                 break
#             if state_ == states.SUCCESS:
#                 break
#             if state_ == states.FAILURE:
#                 response['errMsg'] ='celery job fail'
#                 break
#     #print(task.get(on_message=on_raw_message, propagate=False))
#     #return task.id#jsonify({}), 202, {'Location': url_for('taskstatus',   task_id=task.id)}
#     ts1 = time.time()
#     response['time_async'] =str(ts1-ts0)
#     base64_return = encodeDic(response)
#     print("Return base64: {0}".format(base64_return))
#     print(response)
#     return make_response(jsonify({'jsonBase64':base64_return}))



# @app.route('/kchecking_async', methods=['POST'])
# def kchecking_async():
#     print("Start kchecking_async")

#     ts0 = time.time()
#     app_ID=99999
#     try:
#         data_raw = request.get_json()
#         print(data_raw)
#     except Exception as e:
#         response = dict()
#         errMsg = 'request_error: ' + str(e)
#         errMsg = errMsg + ' ; request: {}'.format(request)
#         response['status'] = -1
#         response['errMsg'] = errMsg
#         return make_response(jsonify(response))

#     schema = jsonBase64Schema()
#     data = loadJson(data_raw, schema)
#     if data is None:
#         err_msg = "<p>Json file error '%s'</p>" % app_ID
#         return err_msg, 405

#     base64_ = data["jsonBase64"]
#     print("Get jsonBase64 from UI: {0}".format(base64_))
#     print(json.loads(base64.b64decode(base64_)))

#     task = task_getKchecking.kchecking_longTask.apply_async((base64_,1))
#     #############################################################################

#     response = dict()
#     #response['state'] = state
#     ##########################################
#     # Add 20180615############################

#     response['sparkAppID'] = ''
#     response['celeryID'] = ''
#     response['status'] = ''
#     response['errMsg'] = ''
#     response['projStep'] = 'kchecking'
#     response['dbName'] = ''
#     response['tblName'] = ''

#     if True:
#         state_ = "test"
#         while state_ != 'PROGRESS':
#             #####2018014, citc trace#####################################################
#             kchecking_longTask_task = task_getKchecking.kchecking_longTask.AsyncResult(task.id)
#             #########################################################################
#             state_ = kchecking_longTask_task.state
# #            print state_
#             response['state'] = state_
#             response['celeryID'] = kchecking_longTask_task.id
# #            print state_
#             if state_ == 'PROGRESS':
#                 if task.info.get('sparkAppID') is None:
#                     response['errMsg'] ='spark context fail'
#                     response['status'] = '-1'
#                     break

#                 response['sparkAppID'] = task.info.get('sparkAppID')[:-1]
#                 response['tblName'] = task.info.get('tblName')[:-1]
#                 response['dbName'] = task.info.get('dbName')[:-1]
#                 response['status'] = '1'
#                 response['finaltblName'] = task.info.get('finaltblName')[:-1]

#                 break

#             #####2018014, citc add#####################################################
#             if state_ == 'FAIL':
#                 #print 'fail_____'
#                 response['err'] ='spark job fail'
#                 break
#             #####2018014, citc add (end)#################################################
#             if state_ == states.SUCCESS:
#                 break
#             if state_ == states.FAILURE:
#                 #print 'fail_____'
#                 response['err'] ='celery job fail'
#                 break

#     ts1 = time.time()
#     response['time_async'] =str(ts1-ts0)
#     base64_return = encodeDic(response)
#     print("Return base64: {0}".format(base64_return))
#     print(response)
#     return make_response(jsonify({'jsonBase64': base64_return}))

# @app.route('/uidEnc_async', methods=['POST'])
# def uidEnc_async():
#     print("Start uidEnc_async")

#     ts0 = time.time()
#     app_ID=99999
#     data_raw = request.get_json()
#     print(data_raw)
#     schema = tableInfoSchema()

#     data = loadJson(data_raw, schema)
#     if data is None:
#         err_msg = "<p>Json file error '%s'</p>" % app_ID
#         return err_msg, 405

#     dbName =  data["dbName"]
#     tblName = data["tableName"]
#     colNames_=data["colNames"]
#     #####2018014, citc trace#####################################################
#     task = task_uid_enc.uidEnc_longTask.apply_async((dbName, tblName, colNames_))
#     #############################################################################

#     response = dict()

#     if True:
#         state_ = "test"
#         while state_ != 'PROGRESS':
#             #####2018014, citc trace#####################################################
#             kcheck_longTask_task = task_uid_enc.uidEnc_longTask.AsyncResult(task.id)
#             #########################################################################
#             state_ = kcheck_longTask_task.state
#             #print state_
#             #response['state'] = state_
#             response['celeryId'] = kcheck_longTask_task.id
#             #print state_
#             if state_ == 'PROGRESS':
#                 if task.info.get('jobID') is None:
#                     response['err'] ='spark job fail'
#                     break
#                 if task.info.get('kTable') is None:
#                     response['err'] ='spark job fail'
#                     break
#                 response['spark_jobID'] =task.info.get('jobID')
#                 response['kTable'] =task.info.get('kTable')
#                 #print task.info
#                 #print(kcheck_longTask_task.backend)
#                 #self.update_state(state=states.PENDING)
#                 break

#             #####2018014, citc add#####################################################
#             if state_ == 'FAIL':
#                 #print 'fail_____'
#                 err = task.info.get('err')
#                 response['err'] = err
#                 #response['err'] ='spark job fail'
#                 break
#             #####2018014, citc add (end)#################################################
#             if state_ == states.SUCCESS:
#                 break
#             if state_ == states.FAILURE:
#                 #print 'fail_____'
#                 response['err'] ='celery job fail'
#                 break

#     ts1 = time.time()
#     response['time_async'] =str(ts1-ts0)
#     print(response)
#     return make_response(jsonify(response))



# @app.route('/kcheck_async', methods=['POST'])
# def kcheck_async():
#     print("Start kcheck_async")

#     ########################################
#     jarFileName='/app/sqljdbc4-2.0.jar'
#     #########################################

#     ts0 = time.time()
#     app_ID=99999
#     data_raw = request.get_json()
#     print(data_raw)
#     schema = tableInfoSchema()
#     #dbName = fields.Str()
#     #tableName = fields.Str()
#     data = loadJson(data_raw, schema)
#     if data is None:
#         err_msg = "<p>Json file error '%s'</p>" % app_ID
#         return err_msg, 405

#     dbName =  data["dbName"]
#     tblName = data["tableName"]
#     colNames_=data["colNames"]
#     task = tasks.kcheck_longTask.apply_async((dbName, tblName, colNames_, jarFileName))

#     response = dict()
#     #response['state'] = state

#     if True:
#         state_ = "test"
#         while state_ != 'PROGRESS':
#             kcheck_longTask_task = tasks.kcheck_longTask.AsyncResult(task.id)
#             state_ = kcheck_longTask_task.state
#             #response['state'] = state_
#             response['celeryId'] = kcheck_longTask_task.id
#             #print state_
#             if state_ == 'PROGRESS':
#                 if task.info.get('jobID') is None:
#                     response['err'] ='spark job fail'
#                     break
#                 #if task.info.get('kTable') is None:
#                 #    response['err'] ='spark job fail'
#                     break
#                 response['spark_jobID'] =task.info.get('jobID')
#                 #response['kTable'] =task.info.get('kTable')
#                 #print task.info
#                 #print(kcheck_longTask_task.backend)
#                 #self.update_state(state=states.PENDING)
#                 break
#             if state_ == states.SUCCESS:
#                 break
#             if state_ == states.FAILURE:
#                 response['err'] ='celery job fail'
#                 break
#     #print(task.get(on_message=on_raw_message, propagate=False))
#     #return task.id#jsonify({}), 202, {'Location': url_for('taskstatus',   task_id=task.id)}
#     ts1 = time.time()
#     response['time_async'] =str(ts1-ts0)
#     print(response)
#     return make_response(jsonify(response))


# def on_raw_message(body):
#     print(body)


# @app.route('/park_task/<task_id>', methods=['GET'])
# def check_task_status(task_id):
#     print("Start check_task_status")

#     task = tasks.kcheck_longTask.AsyncResult(task_id)
#     state = task.state
#     response = dict()
#     response['state'] = state

#     if state == "PROGRESS":
#         if task.info.get('mainInfo') is not None:
#             response['mainInfo'] = task.info.get('mainInfo')

#     elif state == states.SUCCESS:
#         print('check_task_status___SUCCESS')
#         response['result'] = task.get()
#     elif state == states.FAILURE:
#         try:
#             response['error'] = task.info.get('error')
#         except Exception as e:
#             response['error'] = 'Unknown error occurred'

#     print(response.get('state'))
#     print(response)
#     return make_response(jsonify(response))