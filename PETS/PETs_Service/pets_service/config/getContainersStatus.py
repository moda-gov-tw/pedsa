#!/usr/bin/python
# -*- coding: utf-8 -*-

import docker
import json

import os


class checkContainersStatus:
    def __init__(self):
	    print('-----checkContainersStatus-------------')

    def getDockerClient(self):

        os.system('chmod 600 /key.pem')
        os.system('chmod 644 /ca.pem')
        os.system('chmod 644 /cert.pem')

        tls_config = docker.tls.TLSConfig(
            client_cert=('/cert.pem', '/key.pem'),
            ca_cert="/ca.pem",
            verify="/ca.pem"
        )
        #in petsStartup.sh
        #MONITOR_IP=34.81.71.21，改程式
        #sed -i "s/tcp://34.81.253.109:2376', tls=tls_config)
        #tcp://34.81.253.109:2376', tls=tls_config)
        client=docker.DockerClient(base_url='tcp://34.81.253.109:2376', tls=tls_config)
        #print(client.containers.list())        
        result_list=[]

        ##container_dict={}


        for container in client.containers.list(all=True):

            ##container_dict[container.name]=container.status
            container_dict={}
            container_dict["container_name"]=container.name
            container_dict["container_status"]=container.status
            result_list.append(container_dict)
 
        return result_list
        ##return container_dict
        #PETSHadoop_nodemaster

    def getHadoopMode(self):

        os.system('chmod 600 /key.pem')
        os.system('chmod 644 /ca.pem')
        os.system('chmod 644 /cert.pem')

        tls_config = docker.tls.TLSConfig(
            client_cert=('/cert.pem', '/key.pem'),
            ca_cert="/ca.pem",
            verify="/ca.pem"
        )
        #in petsStartup.sh
        #MONITOR_IP=34.81.71.21，改程式
        #sed -i "s/tcp://34.81.253.109:2376', tls=tls_config)
        #tcp://34.81.253.109:2376', tls=tls_config)
        client=docker.DockerClient(base_url='tcp://34.81.253.109:2376', tls=tls_config)
        #print(client.containers.list())        
        result_list=[]

        #hadoop_mode_dict={}


        for container in client.containers.list(all=True):

            if("_nodemaster" in container.name):
                #print(container.name)
                container_ = client.containers.get(container.name)
                ExecResult = container_.exec_run("hadoop dfsadmin -safemode get", stream=False, demux=False)
                output=ExecResult.output.decode('utf-8')
                #print(output)
                #print(ExecResult.exit_code)
                if "Safe mode is OFF" in output:
                    #print("hadoop - Safe mode is OFF ")
                    hadoop_mode_dict={}
                    hadoop_mode_dict["container_name"]=container.name
                    hadoop_mode_dict["hadoop_safe_mode"]="OFF"
                    result_list.append(hadoop_mode_dict)
                else:
                    container_.exec_run("hadoop dfsadmin -safemode leave", stream=False, demux=False)
                    ExecResult = container_.exec_run("hadoop dfsadmin -safemode get", stream=False, demux=False)
                    output=ExecResult.output.decode('utf-8')
                    #print(output) 
                    if "Safe mode is ON" in output:
                        hadoop_mode_dict={}
                        hadoop_mode_dict["container_name"]=container.name
                        hadoop_mode_dict["hadoop_safe_mode"]="ON, system resource encountered an err"
                        result_list.append(hadoop_mode_dict)
                    else:
                        hadoop_mode_dict={}
                        hadoop_mode_dict["container_name"]=container.name
                        hadoop_mode_dict["hadoop_mode"]="OFF"
                        result_list.append(hadoop_mode_dict)
                            
        return result_list
    def getYarnNodes(self):

        os.system('chmod 600 /key.pem')
        os.system('chmod 644 /ca.pem')
        os.system('chmod 644 /cert.pem')

        tls_config = docker.tls.TLSConfig(
            client_cert=('/cert.pem', '/key.pem'),
            ca_cert="/ca.pem",
            verify="/ca.pem"
        )
        #in petsStartup.sh
        #MONITOR_IP=34.81.71.21，改程式
        #sed -i "s/tcp://34.81.253.109:2376', tls=tls_config)
        #tcp://34.81.253.109:2376', tls=tls_config)
        client=docker.DockerClient(base_url='tcp://34.81.253.109:2376', tls=tls_config)
        #print(client.containers.list())        
        result_list=[]

        #hadoop_mode_dict={}


        for container in client.containers.list(all=True):

            if("_nodemaster" in container.name):
                #print(container.name)
                container_ = client.containers.get(container.name)
                ExecResult = container_.exec_run("yarn node -list", stream=False, demux=False)
                output=ExecResult.output.decode('utf-8')
                #print(output)

                lines=output.split("\n")
                for line in lines:
                    #print("#####")
                    #print(line)
                    if "Total Nodes:" in line:
                        lline=line.split(":")
                        yarn_node_dict={}
                        yarn_node_dict["container_name"]=container.name
                        #lline[1]="0"
                        if("0" in lline[1]):
                            yarn_node_dict["yarn_node_numer"]=lline[1]+", yarn system encountered an err"
                        else:
                            yarn_node_dict["yarn_node_numer"]=lline[1]
                              
                        result_list.append(yarn_node_dict)
        return result_list

#Live datanodes (1):
    def getHadoopDataNodes(self):

        os.system('chmod 600 /key.pem')
        os.system('chmod 644 /ca.pem')
        os.system('chmod 644 /cert.pem')

        tls_config = docker.tls.TLSConfig(
            client_cert=('/cert.pem', '/key.pem'),
            ca_cert="/ca.pem",
            verify="/ca.pem"
        )
        #in petsStartup.sh
        #MONITOR_IP=34.81.71.21，改程式
        #sed -i "s/tcp://34.81.253.109:2376', tls=tls_config)
        #tcp://34.81.253.109:2376', tls=tls_config)
        client=docker.DockerClient(base_url='tcp://34.81.253.109:2376', tls=tls_config)
        #print(client.containers.list())        
        result_list=[]

        #hadoop_mode_dict={}


        for container in client.containers.list(all=True):
 
            if("_nodemaster" in container.name):
                #print(container.name)
                container_ = client.containers.get(container.name)
                ExecResult = container_.exec_run("hdfs dfsadmin -report", stream=False, demux=False)
                output=ExecResult.output.decode('utf-8')
                #print(output)

                lines=output.split("\n")
                
                for line in lines:
                    #print("#####")
                    #print(line)
                    #Live datanodes (1):
                    if "Live datanodes " in line:
                        #print("####")
                        #print(line)
                        lline=line.split("(")
                        #print(lline)
                        #print(lline[0])
                        #print(lline[1])
                        llline=lline[1].split(")")
                        #print(llline)
                        hadoop_node_dict={}
                        hadoop_node_dict["container_name"]=container.name
                        #lline[1]="0"
                        if("0" in llline[1]):
                            hadoop_node_dict["datanode_numer"]=llline[0]+", hadoop system encountered an err"
                        else:
                            hadoop_node_dict["datanode_numer"]=llline[0]
                              
                        result_list.append(hadoop_node_dict)
        return result_list
                
    def getYarnApplications(self):

            os.system('chmod 600 /key.pem')
            os.system('chmod 644 /ca.pem')
            os.system('chmod 644 /cert.pem')

            tls_config = docker.tls.TLSConfig(
                client_cert=('/cert.pem', '/key.pem'),
                ca_cert="/ca.pem",
                verify="/ca.pem"
            )
            #in petsStartup.sh
            #MONITOR_IP=34.81.71.21，改程式
            #sed -i "s/tcp://34.81.253.109:2376', tls=tls_config)
            #tcp://34.81.253.109:2376', tls=tls_config)
            client=docker.DockerClient(base_url='tcp://34.81.253.109:2376', tls=tls_config)
            #print(client.containers.list())        
            result_list=[]

            #hadoop_mode_dict={}

            total_app_num=""
            for container in client.containers.list(all=True):

                if("_nodemaster" in container.name):
                    #print(container.name)
                    container_ = client.containers.get(container.name)
                    ExecResult = container_.exec_run("yarn application -list", stream=False, demux=False)
                    output=ExecResult.output.decode('utf-8')
                    #print(output)
                    lines=output.split("\n") #\n
                    #print(lines)
                    yarn_app_dict={}
                    yarn_app_dict["container_name"]=container.name
                    id_list=[]
                    name_list=[]
                    for line in lines:

                        #yarn_app_dict={}
                        #yarn_app_dict["container_name"]=container.name
                        
             
                        if "Total number of applications" in line:
                            line_in_line=line.split(":")
                            #line_in_line=line_in_line[-1].split("\n")
                            #['0', '                Application-Id\t    Application-Name\t    Application-Type\t      User\t     Queue\t             State\t       Final-State\t       Progress\t                       Tracking-URL', '']
                            #print(line_in_line)
                            #print("###############")
                            total_app_num=line_in_line[-1].strip()
                            #print(total_app_num)
                            #print("###############")
                            
                            #yarn_app_dict["container_name"]=container.name
                            #yarn_app_dict["total_app_num"]=total_app_num
                        
                           
                        if "application_" in line:
                            line_in_line1=line.split("\t")
                            #print("------dddd----")
                            #print(line_in_line1)
                            appID=line_in_line1[0].strip()
                            #print(appID)
                            id_list.append(appID) 
                            appName=line_in_line1[1].strip()
                            #print(appName)
                            name_list.append(appName) 

                                
                    yarn_app_dict["total_app_num"]=total_app_num
                    yarn_app_dict["yarn_applicationID_list"]=id_list
                    yarn_app_dict["yarn_applicationNAME_list"]=name_list
                    result_list.append(yarn_app_dict)
            return result_list

#Total number of applications (application-types: [] and states: [SUBMITTED, ACCEPTED, RUNNING]):2
#                Application-Id      Application-Name        Application-Type          User           Queue                   State             Final-State             Progress                        Tracking-URL
#application_1705390146149_0002      getKchecking_one                   SPARK        hadoop         default                ACCEPTED               UNDEFINED                   0%                                 N/A
#application_1705390146149_0001                   gen                   SPARK        hadoop         default                 RUNNING               UNDEFINED                  10%             http://nodemasterS:4040

    def rmYarnApplications(self, appID):

            os.system('chmod 600 /key.pem')
            os.system('chmod 644 /ca.pem')
            os.system('chmod 644 /cert.pem')

            tls_config = docker.tls.TLSConfig(
                client_cert=('/cert.pem', '/key.pem'),
                ca_cert="/ca.pem",
                verify="/ca.pem"
            )
            #in petsStartup.sh
            #MONITOR_IP=34.81.71.21，改程式
            #sed -i "s/tcp://34.81.253.109:2376', tls=tls_config)
            #tcp://34.81.253.109:2376', tls=tls_config)
            client=docker.DockerClient(base_url='tcp://34.81.253.109:2376', tls=tls_config)
            #print(client.containers.list())        
            result_list=[]

            #hadoop_mode_dict={}

            total_app_num=""
            for container in client.containers.list(all=True):

                if("_nodemaster" in container.name):
                    #print(container.name)
                    container_ = client.containers.get(container.name)
                    ExecResult = container_.exec_run("yarn application -list", stream=False, demux=False)
                    output=ExecResult.output.decode('utf-8')
                    #print(output)
                    lines=output.split("\n") #\n
                    #print(lines)
                    yarn_app_dict={}
                    yarn_app_dict["container_name"]=container.name
                    id_list=[]
                    name_list=[]
                    for line in lines:

                        #yarn_app_dict={}
                        #yarn_app_dict["container_name"]=container.name
                        
             
                        if "Total number of applications" in line:
                            line_in_line=line.split(":")
                            #line_in_line=line_in_line[-1].split("\n")
                            #['0', '                Application-Id\t    Application-Name\t    Application-Type\t      User\t     Queue\t             State\t       Final-State\t       Progress\t                       Tracking-URL', '']
                            #print(line_in_line)
                            #print("###############")
                            total_app_num=line_in_line[-1].strip()
                            #print(total_app_num)
                            #print("###############")
                            
                            #yarn_app_dict["container_name"]=container.name
                            #yarn_app_dict["total_app_num"]=total_app_num
                        
                           
                        if "application_" in line:
                            line_in_line1=line.split("\t")
                            #print("------dddd----")
                            #print(line_in_line1)
                            appID=line_in_line1[0].strip()
                            #print(appID)
                            id_list.append(appID) 
                            appName=line_in_line1[1].strip()
                            #print(appName)
                            name_list.append(appName) 

                                
                    yarn_app_dict["total_app_num"]=total_app_num
                    yarn_app_dict["yarn_applicationID_list"]=id_list
                    if appID not in id_list:
                        yarn_app_dict["rm_result"]=appID+" not found"
                    else:
                        #yarn application -kill app_123
                        ExecResult1 = container_.exec_run("yarn application -kill "+appID, stream=False, demux=False)
                        output1=ExecResult1.output.decode('utf-8')
                        

                        yarn_app_dict["rm_result"]=output1 
                    yarn_app_dict["rm_applicationID"]=appID
                    result_list.append(yarn_app_dict)
            return result_list

                   

    #def nappStatus(self):            
if __name__ == "__main__":

    checkContainersStatus_ = checkContainersStatus()

    #container_dict_ = checkContainersStatus_.getDockerClient()
    #print(container_dict_)
    #print("----------------------")
    #hadoop_mode_dict_=checkContainersStatus_.getHadoopMode()
    #print(hadoop_mode_dict_)
    #print("----------------------")
    #yarn_node_dict_=checkContainersStatus_.getYarnNodes()
    #print(yarn_node_dict_)
    #print("---------getHadoopDataNodes-------------")
    #hadoop_data_node_dict_=checkContainersStatus_.getHadoopDataNodes()
    #print(hadoop_data_node_dict_)
    

    print("----------------------")
    rm_appliation_list_dict_=checkContainersStatus_.rmYarnApplications("app_id")
    print(rm_appliation_list_dict_)
    


    #getHadoopApplications


       