#/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os.path import dirname, abspath
import sys

### Kludge to get the django settings module into the path
INSTALL_PATH = dirname(__file__)
sys.path.insert(-1, INSTALL_PATH)
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'qmpy.db.settings'

from models import *
