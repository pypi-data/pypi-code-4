#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
appli_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
def get_dev_path():
    return os.path.join(os.path.dirname(__file__), '..')
def get_root_app():
    package_path = os.path.dirname(__file__)
    if os.path.exists(os.path.join(package_path, 'data')):
        return package_path
    return get_dev_path()

def get_share_dir():
    return os.path.join(get_root_app(), 'share')
