'''
This module implements some reusable custom actions.
'''

import argparse
import os

__all__ = [
    'NonFolderError',
    'FolderExistsAction',
    'FolderCreateAction',
]

class NonFolderError(Exception):
    'Raised when we expect a folder (directory) and did not get one'
    pass

class FolderExistsAction(argparse.Action):
    '''
    Custom action: verify the argument to be a folder (directory). If
    not, raise a NonFolderError exception.
    
    The action will strip off trailing slashes from the folder's name.
    '''
    
    def verify_folder_existence(self, folder_name):
        '''
        Return folder_name if exists. Throw NonFolderError if not.
        '''
        if not os.path.isdir(folder_name):
            message = 'ERROR: {0} is not a folder'.format(folder_name)
            raise NonFolderError(message)
        
        folder_name = folder_name.rstrip(os.sep)
        return folder_name
            
    def __call__(self, parser, namespace, values, option_string=None):
        if type(values) == list:
            folders = map(self.verify_folder_existence, values)
        else:
            folders = self.verify_folder_existence(values)
            
        # Add the attribute
        setattr(namespace, self.dest, folders)
        
# ======================================================================

class FolderCreateAction(argparse.Action):
    '''
    Custom action: create a new folder if not exist. If the folder
    already exists, do nothing.
    
    The action will strip off trailing slashes from the folder's name.
    '''

    def create_folder(self, folder_name):
        '''
        Create a new directory if not exist. The action might throw
        OSError, along with other kinds of exception
        '''
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
            
        folder_name = folder_name.rstrip(os.sep)
        return folder_name
        
    def __call__(self, parser, namespace, values, option_string=None):
        if type(values) == list:
            folders = map(self.create_folder, values)
        else:
            folders = self.create_folder(values)
            
        # Add the attribute
        setattr(namespace, self.dest, folders)
