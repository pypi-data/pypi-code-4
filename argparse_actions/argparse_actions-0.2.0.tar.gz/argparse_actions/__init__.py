'''
This module implements some reusable custom actions.
'''

import argparse
import os

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
        
