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
        client=docker.DockerClient(base_url='tcp://140.96.178.108:2376', tls=tls_config)
        print(client.containers.list())        
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

    #def nappStatus(self):            
if __name__ == "__main__":

    checkContainersStatus_ = checkContainersStatus()
    container_dict_ = checkContainersStatus_.getDockerClient()

    print(container_dict_)
    #print(container_dict_.keys())

       