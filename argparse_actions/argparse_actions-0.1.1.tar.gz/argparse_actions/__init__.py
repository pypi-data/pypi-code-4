'''
This module implements some reusable custom actions.
'''

import argparse
import os

class NonFolderError(Exception):
    'Raised when we expect a folder (directory) and did not get one'
    pass

class VerifyFolderAction(argparse.Action):
    '''
    Custom action: verify the argument to be a folder (directory). If
    not, raise a NonFolderError exception.
    '''
    def __call__(self, parser, namespace, values, option_string=None):
        # Verify if src is actually a folder
        if not os.path.isdir(values):
            message = 'ERROR: {0} is not a folder'.format(values)
            raise NonFolderError(message)
        
        # Remove the trailing slashes
        values = values.rstrip(os.sep)
        
        # Add the attribute
        setattr(namespace, self.dest, values)
        
