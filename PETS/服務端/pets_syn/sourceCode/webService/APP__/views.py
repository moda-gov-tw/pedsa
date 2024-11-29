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
from flask import escape  
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
    response = {}

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

    try:
        data = loadJson(data_raw, schema) ##from curl
    except Exception as e:
        errMsg = 'Json file error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))    

    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return make_response(jsonify({"status": -1, "errMsg": err_msg}), 405)


    jsonBase64__ = data.get("jsonBase64")
    if not jsonBase64__:
        response['status'] = -1
        response['errMsg'] = "Missing 'jsonBase64' in input data"
        return make_response(jsonify(response))

    #####task#####################################################
    task = task_deleteProject.deleteProject_longTask.apply_async((jsonBase64__,1)) 
    #############################################################################
    if True:        
        state_ =  "test"
        while state_ != 'PROGRESS':
            ##########################################################
            deleteProject_longTask_task = task_deleteProject.deleteProject_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = escape(str(deleteProject_longTask_task.state))
            response['celeyId'] =  escape(deleteProject_longTask_task.id)

            if state_ == 'PROGRESS':
                state_ = 'SUCCESS'
                response['PID'] =escape(task.info.get('PID'))
                response['userID'] = escape(task.info.get('userID'))
                response['projStep']=escape(task.info.get('projStep'))
                response['projID'] = escape(task.info.get('projID'))
                response['projName']=escape(task.info.get('projName'))
                response['stateno'] = '1'
                break;
                
            #####FAIL#####################################################
            if state_ == 'FAIL':
                response['projStep']='Delete Project'
                try : 
                    response['stateno'] = escape(task.info.get('stateno'))
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    response['ERRMSG']=  escape(task.info.get('Msg'))
                except Exception as e:
                    response['ERRMSG']= "UNKNOWN"
                break;
            #####SUCESS#################################################
            if state_ == states.SUCCESS:
                state_ == 'FAIL'
                response['projStep']='Delete Project'
                try : 
                    response['stateno'] = escape(task.info.get('stateno'))
                except Exception as e:
                    response['stateno'] = '-3'
                try:
                    response['ERRMSG']=  escape(task.info.get('Msg'))
                except Exception as e:
                    response['ERRMSG']= "UNKNOWN"
                break;    
            if state_ == states.FAILURE:
                print ('fail_')
                response['projStep']='Delete Project'
                response['err'] ='celery job fail -- '
                break;  

    ts1 = time.time()
    response['STATE'] = str(state_)
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response))

#2020316:reset project
@app.route('/resetProject_async', methods=['POST'])
def resetProject_async():
    print("Start resetProject_async")
    ts0 = time.time()
    app_ID=99999
    response = {}

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
    try:
        data = loadJson(data_raw, schema) ##from curl
    except Exception as e:
        errMsg = 'Json file error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))    

    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return make_response(jsonify({"status": -1, "errMsg": err_msg}), 405)


    jsonBase64__ = data.get("jsonBase64")
    if not jsonBase64__:
        response['status'] = -1
        response['errMsg'] = "Missing 'jsonBase64' in input data"
        return make_response(jsonify(response))
    #####task#####################################################
    task = task_resetProject.resetProject_longTask.apply_async((jsonBase64__,1)) 
    #############################################################################

    if True:        
        state_ = "test"
        while state_ != 'PROGRESS':
            ##########################################################
            resetProject_longTask_task = task_resetProject.resetProject_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = escape(str(resetProject_longTask_task.state))
            response['celeyId'] =  escape(resetProject_longTask_task.id)

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
    response = {}

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

    try:
        data = loadJson(data_raw, schema) ##1128from curl
    except Exception as e:
        errMsg = 'Json file error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))

    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return make_response(jsonify({"status": -1, "errMsg": err_msg}), 405)


    jsonBase64__ = data.get("jsonBase64")
    if not jsonBase64__:
        response['status'] = -1
        response['errMsg'] = "Missing 'jsonBase64' in input data"
        return make_response(jsonify(response))
    #####20181121, citc trace#####################################################
   #task = task_getGenerationData.getGenerationData_longTask.apply_async((projName, fileName, colNames_, keyName_)) #1224:pei
    
    task = task_killProcess.killProcess_longTask.apply_async((jsonBase64__,1),queue='hipri', routing_key='hipri:killProcess') #20191016
    #############################################################################

    if True:        
        state_ = "test"
        while state_ != 'PROGRESS':
            #####20181121, citc trace#####################################################
            killProcess_longTask_task = task_killProcess.killProcess_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = escape(str(killProcess_longTask_task.state))
            response['celeyId'] = escape(killProcess_longTask_task.id)
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
    response = {}

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

    try:
        data = loadJson(data_raw, schema)
    except Exception as e:
        errMsg = 'Json file error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))

    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return make_response(jsonify({"status": -1, "errMsg": err_msg}), 405)


    jsonBase64__ = data.get("jsonBase64")
    if not jsonBase64__:
        response['status'] = -1
        response['errMsg'] = "Missing 'jsonBase64' in input data"
        return make_response(jsonify(response))

    #####20181121, citc trace#####################################################
   #task = task_getGenerationData.getGenerationData_longTask.apply_async((projName, fileName, colNames_, keyName_)) #1224:pei
    
    task = task_createFolder.createFolder_longTask.apply_async((jsonBase64__,1)) #20191016
    #############################################################################

    if True:        
        state_ = "test"
        while state_ != 'PROGRESS':
            #####20181121, citc trace#####################################################
            createFolder_longTask_task = task_createFolder.createFolder_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = escape(str(createFolder_longTask_task.state))
            response['celeyId'] = escape(createFolder_longTask_task.id)
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
    response = {}

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

    try:
        data = loadJson(data_raw, schema) ##1128from curl
    except Exception as e:
        response = dict()
        errMsg = 'Json file error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))

    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return make_response(jsonify({"status": -1, "errMsg": err_msg}), 405)

    jsonBase64__ = data.get("jsonBase64")
    if not jsonBase64__:
        response['status'] = -1
        response['errMsg'] = "Missing 'jsonBase64' in input data"
        return make_response(jsonify(response))
    
    try:
        task = task_getFolder.getFolder_longTask.apply_async((jsonBase64__,1)) #20191016
    except Exception as e:
        response['status'] = -1
        response['errMsg'] = "Task initiation error: " + str(e)
        return make_response(jsonify(response))
    #############################################################################

    if True:        
        state_ = "test"
        while state_ != 'PROGRESS':
            #####20181121, citc trace#####################################################
            getFolder_longTask_task = task_getFolder.getFolder_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = escape(str(getFolder_longTask_task.state))
            print (state_)
            #response['state'] = state_
            response['celeyId'] = escape(getFolder_longTask_task.id)
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
    response = {}

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

    try:
        data = loadJson(data_raw, schema)
    except Exception as e:
        errMsg = 'Json file error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))

    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return make_response(jsonify({"status": -1, "errMsg": err_msg}), 405)


    jsonBase64__ = data.get("jsonBase64")
    if not jsonBase64__:
        response['status'] = -1
        response['errMsg'] = "Missing 'jsonBase64' in input data"
        return make_response(jsonify(response))
    #####20181121, citc trace#####################################################
    task = task_preview.preview_longTask.apply_async((jsonBase64__,1)) #20191016
    #############################################################################
    if True:        
        state_ = "test"
        while state_ != 'PROGRESS':
            #####20181121, citc trace#####################################################
            preview_longTask_task = task_preview.preview_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = escape(str(preview_longTask_task.state))
            response['celeyId'] = escape(preview_longTask_task.id)
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
    response = {}

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

    try:
        data = loadJson(data_raw, schema)
    except Exception as e:
        errMsg = 'Json file error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))

    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return make_response(jsonify({"status": -1, "errMsg": err_msg}), 405)


    jsonBase64__ = data.get("jsonBase64")
    if not jsonBase64__:
        response['status'] = -1
        response['errMsg'] = "Missing 'jsonBase64' in input data"
        return make_response(jsonify(response))
    #####20181121, citc trace#####################################################   
    task = task_PETs_preview.PETs_preview_longTask.apply_async((jsonBase64__,1)) #20191016
    #############################################################################
    if True:        
        state_ = "test"
        while state_ != 'PROGRESS':
            #####20181121, citc trace#####################################################
            preview_longTask_task = task_PETs_preview.PETs_preview_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = escape(str(preview_longTask_task.state))
            response['celeyId'] = escape(preview_longTask_task.id)
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
    response = {}

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

    try:
        data = loadJson(data_raw, schema)
    except Exception as e:
        errMsg = 'Json file error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))

    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return make_response(jsonify({"status": -1, "errMsg": err_msg}), 405)

    jsonBase64__ = data.get("jsonBase64")
    if not jsonBase64__:
        response['status'] = -1
        response['errMsg'] = "Missing 'jsonBase64' in input data"
        return make_response(jsonify(response))
    
    #############################################################################
    task = task_getGenerationData.getGenerationData_longTask.apply_async((jsonBase64__,1)) #1224:pei
    #############################################################################

    if True:        
        state_ = "test"
        while state_ != 'PROGRESS':
            #####20181121, citc trace#####################################################
            genData_longTask_task = task_getGenerationData.getGenerationData_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = escape(str(genData_longTask_task.state))
            response['celeyId'] = escape(genData_longTask_task.id)
            #print state_
            if state_ == 'PROGRESS':
                response['PID'] =task.info.get('PID')
                response['userID'] = task.info.get('userID')
                response['projStep']=task.info.get('projStep')
                response['projID'] = task.info.get('projID')
                response['stateno'] = '1'
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
    ts1 = time.time()
    response['STATE'] = state_
    response['time_async'] =str(ts1-ts0)
    return make_response(jsonify(response)) 

@app.route('/MLutility_async', methods=['POST'])
def MLutility_async():
    print("Start MLutility_async")
    ts0 = time.time()
    app_ID=99999
    response = {}

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

    try:
        data = loadJson(data_raw, schema)
    except Exception as e:
        errMsg = 'Json file error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))

    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return make_response(jsonify({"status": -1, "errMsg": err_msg}), 405)


    jsonBase64__ = data.get("jsonBase64")
    if not jsonBase64__:
        response['status'] = -1
        response['errMsg'] = "Missing 'jsonBase64' in input data"
        return make_response(jsonify(response))

    #####20181121, citc trace#####################################################
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
            state_ = escape(str(MLutility_longTask_task.state))
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
    ts1 = time.time()
    response['time_async'] =str(ts1-ts0)
    response['STATE'] = state_
    return make_response(jsonify(response))

@app.route('/exportData_async', methods=['POST'])
def exportData_async():
    print("Start exportData_async")
    ts0 = time.time()
    app_ID=99999
    response = {}

    try:
        data_raw = request.get_json()
    except Exception as e:
        response = dict()
        errMsg = 'Request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = '-1'
        response['errMsg'] = errMsg
        return make_response(jsonify(response))


    schema = jsonBase64Schema()#genDataInfoSchema()

    try:
        data = loadJson(data_raw, schema)
    except Exception as e:
        errMsg = 'Json file error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))

    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return make_response(jsonify({"status": -1, "errMsg": err_msg}), 405)


    jsonBase64__ = data.get("jsonBase64")
    if not jsonBase64__:
        response['status'] = -1
        response['errMsg'] = "Missing 'jsonBase64' in input data"
        return make_response(jsonify(response))

    #################################
    task = task_exportData.exportData_longTask.apply_async((jsonBase64__,1)) #1224:pei
    #############################################################################

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####20181121, citc trace#####################################################
            exportData_longTask_task = task_exportData.exportData_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = escape(str(exportData_longTask_task.state))

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

########################################
#PETs_exportData_async:20231124
@app.route('/PETs_exportData_async', methods=['POST'])
def PETs_exportData_async():
    print("Start PETs_exportData_async")
    ts0 = time.time()
    app_ID=99999
    response = {}

    try:
        data_raw = request.get_json()
    except Exception as e:
        response = dict()
        errMsg = 'Request_error: ' + str(e)
        errMsg = errMsg + ' ; request: {}'.format(request)
        response['status'] = '-1'
        response['errMsg'] = errMsg
        return make_response(jsonify(response))


    schema = jsonBase64Schema()#genDataInfoSchema()
    try:
        data = loadJson(data_raw, schema)
    except Exception as e:
        errMsg = 'Json file error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))

    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return make_response(jsonify({"status": -1, "errMsg": err_msg}), 405)



    jsonBase64__ = data.get("jsonBase64")
    if not jsonBase64__:
        response['status'] = -1
        response['errMsg'] = "Missing 'jsonBase64' in input data"
        return make_response(jsonify(response))

    #################################
    task = task_PETs_exportData.PETs_exportData_longTask.apply_async((jsonBase64__,1)) #1224:pei
    #############################################################################

    if True:
        state_ = "test"
        while state_ != 'PROGRESS':
            #####20181121, citc trace#####################################################
            exportData_longTask_task = task_PETs_exportData.PETs_exportData_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = escape(str(exportData_longTask_task.state))
            if state_ == 'PROGRESS':
                response['PID'] = task.info.get('PID')
                response['celeryId'] = task.info.get('celeryId')
                response['projName'] = task.info.get('projName')
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
    response = {}

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

    try:
        data = loadJson(data_raw, schema)
    except Exception as e:
        errMsg = 'Json file error: ' + str(e)
        response['status'] = -1
        response['errMsg'] = errMsg
        return make_response(jsonify(response))

    if data is None:
        err_msg = "<p>Json file error '%s'</p>" % (app_ID)
        return make_response(jsonify({"status": -1, "errMsg": err_msg}), 405)

    jsonBase64__ = data.get("jsonBase64")
    if not jsonBase64__:
        response['status'] = -1
        response['errMsg'] = "Missing 'jsonBase64' in input data"
        return make_response(jsonify(response))
    #################################   
    task = task_PETs_MLutility.PETs_MLutility_longTask.apply_async((jsonBase64__,1)) 
    #############################################################################
    if True:        
        state_ = "test"
        while state_ != 'PROGRESS':
            #####20181121, citc trace#####################################################
            MLutility_longTask_task = task_PETs_MLutility.PETs_MLutility_longTask.AsyncResult(task.id)
            #########################################################################
            state_ = escape(str(MLutility_longTask_task.state))
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
    ts1 = time.time()
    response['time_async'] =str(ts1-ts0)
    response['STATE'] = state_
    return make_response(jsonify(response))