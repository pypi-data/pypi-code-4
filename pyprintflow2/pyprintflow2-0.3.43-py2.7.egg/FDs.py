'''
Created on Sep 29, 2013

@author: "Colin Manning"
'''

import os

class FDs(object):
    '''
    A simple file data store
    '''

    FS_CONFIG = 'fs_config.json'
    FS_LOCK = '.lock'
    
    fs_root = None
    fs_id = None
    fs_id_path = None
    fs_config = None
    fs_config_file = None
    fs_lock_file = None
    ready = False

    def __init__(self, fs_root, fs_id):
        self.fs_id_path = os.path.join(fs_root, fs_id)
        if not os.path.exists(fs_root):
            os.makedirs(fs_root, mode=0o755)
        if not os.path.exists(self.fs_id_path):
            os.makedirs(self.fs_id_path, mode=0o755)
        self.fs_root = fs_root
        self.fs_config_file = os.path.join(self.fs_id_path, self.FS_CONFIG)
        self.fs_lock_file = os.path.join(self.fs_id_path, self.FS_LOCK)
        
    def terminate(self):
        fs_lock_file = os.path.join(self.fs_id_path, self.FS_LOCK)
        if os.path.exists(fs_lock_file):
            os.remove(fs_lock_file)
        
        
    def ensureDirectoryExists(self, path):
        if not os.path.exists(path):
            os.makedirs(path, mode=0o755)

    # strip the last 4 characters and use - spreads them out nicely
    def     getPathForId(self, oid):
        sid = str(oid)
        l = len(sid)
        return sid[l-4:l-2] + "/" + sid[l-2:]

    def add(self, path):
        # add a file to the file store and return the id
        if os.path.exists(path):
            path = self.getPathForId(1)
            
    def fetch(self, file_id):
        # find a file for a given id
        f = file_id
    
    def remove(self, file_id):
        # remove a file with a given id
        f = file_id