from config_sql.connect_sql import ConnectSQL

def test_mysql(projName):
	try:
	    print('start connectToMysql to check project_name in mysql: {}'.format(projName))
	    check_conn = ConnectSQL()
	except Exception as e:
		print('connectToMysql fail: ' +str(e))


projName="SYN"
test_mysql(projName)

from config_sql.connect_sql import ConnectSQL

import os 

def main(projName,table,data):
    # Connect mysql
    print('########PID########, %s'%(os.getpid()))


    try:
        check_conn = ConnectSQL()
        print("Connect SQL")
    except Exception as e:
        print('connectToMysql fail: - %s:%s' %(type(e).__name__, e))
        return False


	
    #DROP DB(project NAME) for init
    #print("DROOOOOOOOOOOOOOP")
    #sqlStr = "DROP DATABASE {}".format(projName)
    #resultCheck = check_conn.doSqlCommand(sqlStr)
    #print(resultCheck)


    #create DB(project NAME) for init
    sqlStr = "create database if not exists {}".format(projName)
    resultCheck = check_conn.doSqlCommand(sqlStr)
    print(resultCheck)
    
    #check DB exist
    sqlStr = "SHOW DATABASES"
    resultCheck = check_conn.doSqlCommand(sqlStr)
    print(resultCheck)

    sqlStr = "create table if not exists {}.{}(`Pid` varchar(50) default {}, `Status` varchar(50) NOT NULL COMMENT 'status' default 'Initial table', `time` INT NOT NULL COMMENT 'percentage' default '0',`createtime` varchar(50))".format(projName,table,data['Pid']) 
    resultCheck = check_conn.doSqlCommand(sqlStr)
    print(resultCheck)

    #check TB exist
    sqlStr = "SHOW TABLES from {}".format(projName)
    resultCheck = check_conn.doSqlCommand(sqlStr)
    print(resultCheck)

    sqlStr = "DESC {}.{}".format(projName,table)
    resultCheck = check_conn.doSqlCommand(sqlStr)
    print(resultCheck)
    print("======DATA======",data)

    condisionSampleData = {}
    condisionSampleData["Pid"] = data['Pid']
    condisionSampleData["Status"] ='Initial table'
    condisionSampleData["time"] = '0'

    #condisionSampleData = {
        #'dbname': projName,
        #'tbname': table
    #    'data': data
    #}
    valueSampleData = data
    #valueSampleData = {
        #'dbname': projName,
        #'tbname': table,
        #'data': data
    #}

    resultSampleData = check_conn.updateValueMysql(projName,
                                             table,
                                             condisionSampleData,
                                             valueSampleData)
    if resultSampleData['result'] == 1:
        print("Update mysql succeed. {0}".format(resultSampleData['msg']))
    else:
        msg = resultSampleData['msg']
        print('insertSampleDataToMysql fail: ' + msg)

    #cursor.close()
    check_conn.close()

if __name__ == "__main__":
	data = {}
	data['Pid']='23'
	data['Status'] = 'GAN	'
	data['time'] = '1000'
	main('projAdult','GANStatus',data)