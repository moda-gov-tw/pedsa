# -*- coding: utf-8 -*-

from MyLib.connect_sql import ConnectSQL



text1 = 'test_content_2020011701 with spark-submit\n'
text2 = 'test_content_2020011702 with spark-submit\n'

conn = ConnectSQL()
dbName = 'DeIdService'
tblName = 'T_Project_RiskTable'
columns = 'project_id,project_name,dbname,r1,r2,r3,r4,r5,rs1,rs2,rs3,rs4,rs5'
conditions = 16,'getRisk_test1','adult_file1',1,2,3,4,5,'*','*','**','***','*'

conn.cursor.execute("set names utf8")

#OK
sqlStr = "INSERT INTO {}.{} ".format(dbName, tblName)
sqlStr = sqlStr + " ({})  values".format(columns)
sqlStr = sqlStr + " {}".format(conditions)

conn.cursor.execute(sqlStr)
conn.connection.commit()


f = open("/home/hadoop/proj_/longTaskDir/risk_core/test_report.txt",'wb')
f.write(text1.encode('utf-8'))
f.write(text2.encode('utf-8'))
f.close()





