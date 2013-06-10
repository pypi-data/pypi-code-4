#!/usr/bin/env python
# encoding: utf-8
'''
folder_exists.py
================

This sample demonstrate the FolderExistsAction custom action.

Examples::

    python folder_exists /tmp
    python folder_exists /foo/bar
    
'''

import argparse
import argparse_actions

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Custom Actions')
    parser.add_argument('directory', action=argparse_actions.FolderExistsAction)
    
    try:
        args = parser.parse_args()
        print 'Directory exists: {0}'.format(args.directory)
    except argparse_actions.NonFolderError as e:
        print 'Directory does not exist'
        print e
