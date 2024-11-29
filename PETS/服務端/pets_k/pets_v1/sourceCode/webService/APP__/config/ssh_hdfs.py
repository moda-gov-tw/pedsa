import paramiko
from loginInfo import getConfig

class ssh_hdfs:

    def __init__(self):
        # keyPath is a private key (id_rsa)
        hdfsInfo = getConfig().getLoginHdfs()
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if(hdfsInfo.has_key('keyPath')):
            hostname_ = str(hdfsInfo['hostname'])
            user_ = str(hdfsInfo['user'])
            keyPath = str(hdfsInfo['keyPath'])
            port_ = str(hdfsInfo['port'])
            key_ = paramiko.RSAKey.from_private_key_file(keyPath)
            if port_ == '':
                ssh.connect(hostname=hostname_,
                            username=user_,
                            pkey=key_)
                self.ssh = ssh
            else:
                ssh.connect(hostname=hostname_,
                            port=port_,
                            username=user_,
                            pkey=key_)
                self.ssh = ssh

        else:
            hostname_ = str(hdfsInfo['hostname'])
            port_ = str(hdfsInfo['port'])
            user_ = str(hdfsInfo['user'])
            password_ = str(hdfsInfo['password'])
            if port_ == '':
                ssh.connect(hostname=hostname_,
                            port="5922",
                            username=user_,
                            password="citcw200@")
                self.ssh = ssh
            else:
                ssh.connect(hostname=hostname_,
                            port=port_,
                            username=user_,
                            password=password_)
                self.ssh = ssh

        '''
        hostname, user, keyPath = getConfig().getLoginHdfs()
        key_ = paramiko.RSAKey.from_private_key_file(keyPath)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=hostname,username=user,pkey=key_)
        self.ssh = ssh
        '''


    def callCommand_output(self, command, addPath=False):
        if not addPath:
            stdin,stdout,stderr = self.ssh.exec_command(command)
            return stdin,stdout,stderr
        else:
            PATH = getConfig().getSparkPath()
            commandNew = '''
            export PATH={0}
            
            export PYTHONIOENCODING=utf-8
            
            source .bashrc
        
            {1}
            '''.format(PATH, command)
            stdin,stdout,stderr = self.ssh.exec_command(commandNew)
            return stdin,stdout,stderr


    def callCommand_noOutput(self, command, addPath=False):
        if not addPath:
            stdin, stdout, stderr = self.ssh.exec_command(command)
        else:
            PATH = getConfig().getSparkPath()
            commandNew = '''
            export PATH={0}
            
            export PYTHONIOENCODING=utf-8

            source .bashrc

            {1}
            '''.format(PATH, command)
            stdin, stdout, stderr = self.ssh.exec_command(commandNew)


    def close(self):
        self.ssh.close()
