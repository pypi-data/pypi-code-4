#-*- coding: utf-8 -*-
from deploy_class.globals import singleton, NotOveroadedError
import os
import subprocess
class AbstractExecuteInterface(object):
    def execute(self, *a):
        raise NotOveroadedError
    
    def set_cwd(self, cwd):
        self.cwd = cwd

@singleton
class ConsoleInterface(AbstractExecuteInterface):
    def __init__(self, cwd):
        self.cwd = cwd
    
    def execute(self, *a):
        string = 'cd %s;'%self.cwd
        for x in a:
            if x[-1] != ";":
                x += ";"
            string += x
        return subprocess.call(string, shell=True)
    

import paramiko
class SSHInterface(AbstractExecuteInterface):
    def __init__(self, user, password, host, home_folder, port=22):
        self.user, self.password, self.host, self.cwd, self.port = [user, password, host, home_folder, port]
        
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=host, username=user, password=password, port=port)
        self.transport = None

        self.init_transport()
    
    def init_transport(self):
        if not self.transport:
            self.transport = paramiko.Transport((self.host, self.port))
            self.transport.connect(username=self.user, password=self.password)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
    
    def execute(self, *a):
        s = 'cd '+self.cwd+";"
        for comm in a:
            if comm[-1]!=";":
                comm += ";"
                s += comm
        print s
        stdin, stdout, stderr = self.client.exec_command(s)
        return stdout.read() + stderr.read()
    
    def get_file(self, remote_path, local_path):
        self.init_transport()
        self.sftp.get(remote_path, local_path)
    
    def upload_file(self, local_path, remote_path):
        self.init_transport()
        self.sftp.put(local_path, remote_path)