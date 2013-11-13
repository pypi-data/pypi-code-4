#-*- coding: utf-8 -*-
from deploy_class.globals import singleton, NotOveroadedError
import os
import subprocess
from deploy_class.globals import bcolors

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
    
def threadize(func):
    import threading
    def _c(*a, **k):
        thread = threading.Thread(target = func, args = a, kwargs = k)
        thread.start()
    return _c

import paramiko

class SSHInterface(AbstractExecuteInterface):
    def __init__(self, user, password, host, home_folder, port=22):
        self.user, self.password, self.host, self.cwd, self.port = [user, password, host, home_folder, port]
        
        self.is_connected = False

    @threadize
    def connect(self):
        if self.is_connected == True:
            return
        print bcolors.OKGREEN, "Start connect to ssh server", bcolors.ENDC
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=self.host, username=self.user, password=self.password, port=self.port)
        self.transport = None

        self.init_transport()
        self.is_connected = True
        print bcolors.OKGREEN, "Connected", bcolors.ENDC
    
    def _waiting_for_connect(self):
        import time
        while not self.is_connected:
            time.sleep(1)
            print bcolors.WARNING, "Waiting for ssh...", bcolors.ENDC

    def init_transport(self):
        if not self.transport:
            self.transport = paramiko.Transport((self.host, self.port))
            self.transport.connect(username=self.user, password=self.password)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
    
    def execute(self, *a):
        self._waiting_for_connect()
        s = 'cd '+self.cwd+";"
        for comm in a:
            if comm[-1]!=";":
                comm += ";"
                s += comm
        print s
        stdin, stdout, stderr = self.client.exec_command(s)
        return stdout.read() + stderr.read()
    
    def get_file(self, remote_path, local_path):
        self._waiting_for_connect()
        self.sftp.get(remote_path, local_path)
    
    def upload_file(self, local_path, remote_path):
        self._waiting_for_connect()
        self.sftp.put(local_path, remote_path)