import os
import configparser 
import subprocess
# from subprocess import Popen, PIPE

def main():
    ###scp from PET-hadooop: 將遠端的檔案保留時間與權限複製到本地端
    projName = 'adult'
    runcode = os.system('apt install sshpass')

    try:
        #file_ = 'config/Hadoop_information.txt'
        #config = configparser.ConfigParser()
        #config.read(file_)
        ip = '34.81.71.21' #config.get('Hadoop_information', 'ip') 
        port = '22' #config.get('Hadoop_information', 'port') 
        from_path = '/home/ubuntu/PETS/pets_join/citc_v2/sourceCode/hadoop/final_project/syn/input/'

        to_path = '/home/ubuntu/PETS/pets_join/citc_v2/sourceCode/hadoop/final_project/syn/output/'

        
        #config.get('Hadoop_information', 'out_path')  
        print(ip)
        print(port)
        print(to_path)
        folderForSynthetic = "folderForSynthetic"
        project_path = "/app/app/devp/"+folderForSynthetic+"/"+projName+'/'
        synData_path = project_path+"synProcess/synthetic/"
        exportData_path = project_path+'output/'
        # cmd = 'echo "citcw200@" | scp -o StrictHostKeyChecking=no -P ' + port + ' -r hadoop@' + ip + ':/home/hadoop/proj_/final_project/syn/input/'+projName+'/ user_upload_folder/'+projName+'/'
        # cmd = 'echo "citcw200@" | scp -o StrictHostKeyChecking=no -P 6922 -r hadoop@140.96.178.108:/home/hadoop/proj_/data/output/'+projName+'/ /app/app/devp/user_upload_folder/'+projName+'/'
        #cmd = 'sshpass -p "iclw200@" scp -o StrictHostKeyChecking=no -P ' + port + ' -r privacy@' + ip +':'+from_path+projName+' /app/app/devp/user_upload_folder/'
        cmd = 'sshpass -p "iclw200@" scp -o StrictHostKeyChecking=no -P ' + port + ' -r '+exportData_path+' privacy@' + ip +':'+to_path
        #to_path_proj = to_path+projName+"/"

        #cmd = f'sshpass -p "citcw200@" scp -o StrictHostKeyChecking=no -P {port} -r {exportData_path} privacy@{ip}:{to_path_proj}'
        #proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("cmd is {0}".format(str(cmd)))
        # runcode = os.system(cmd)
        proc = subprocess.run(cmd, shell=True,check=True, universal_newlines=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~FINISH')
    except Exception as e:
        
        print('to PETs hadoop error : ',str(e))

main()
