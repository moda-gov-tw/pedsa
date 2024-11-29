#!/usr/bin/python
# -*- coding: utf-8 -*-


import json
import sys
import os

#print("12345")

def readJson():

    data=""
    tmpStr1=""

    with open('/run/secrets/ahcitcww') as in_file:
    	tmpStr1 = in_file.readline()
    	tmpStr1 = tmpStr1.strip()
    	#print(tmpStr1)
    	if len(tmpStr1) < 3:
    		sys.exit("process_appsetting error")

    
    with open('/app/appsettings.json') as json_file:
            #json_file = json_file.replace("'", '"')
            #json_file = json_file.replace("u", "")
	    data = json.load(json_file)
	    tmpStr=data['ConnectionStrings']["DefaultConnection"]
	    print(tmpStr)
	    outList = tmpStr.split(";")
	    outStr=""
	    for item in tmpStr.split(";"):

	    	if "pwd=" in item:
	    		item = "pwd=" + tmpStr1
	        #print (item)
	        outStr= outStr+item+";"
	    outStr = outStr.rstrip(';');
	    #print (outStr)	
	    data['ConnectionStrings']["DefaultConnection"] = outStr
	    json_file.close()
    try:
       os.remove('/app/appsettings.json')   
    except Exception as e:
       print("rm appsettings.json error")


    with open('/app/appsettings.json', "w") as json_file:

      	data = json.dumps(data, indent=4, separators=(',', ': '), ensure_ascii=False, encoding='utf8') 
    	
    	try:
    		#json.dump(data, json_file, indent=4, separators=(',', ': '),ensure_ascii=False, encoding='utf8')
    		json_file.write(data)
    		json_file.close()
    		print(data)
        except Exception as e:
            print('update deid pwd error: %s', str(e))

            return 
    

if __name__ == "__main__":

	readJson()
  
