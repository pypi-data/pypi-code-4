import os
from os.path import dirname, abspath
import sys

### Kludge to get the django settings module into the path
sys.path.insert(0, dirname(__file__))
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'dev_qmpy.db.settings'

from models import *
from db import *
