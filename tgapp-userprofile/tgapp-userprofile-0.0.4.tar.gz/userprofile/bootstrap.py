# -*- coding: utf-8 -*-
"""Setup the userprofile application"""

from userprofile import model
from tgext.pluggable import app_model

def bootstrap(command, conf, vars):
    print 'Bootstrapping userprofile...'
