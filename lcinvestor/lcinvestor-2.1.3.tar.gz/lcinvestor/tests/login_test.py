#!/usr/bin/env python
#
# Runs tests against the LendingClub.com using your username and password.
#

import sys
import os

sys.path.insert(0, '.')
sys.path.insert(0, '../')
sys.path.insert(0, '../../')
import lcinvestor
from lcinvestor.settings import Settings

"""
Setup
"""
base_dir = os.path.dirname(os.path.realpath(__file__))
app_dir = os.path.join(base_dir, '.login_test')

settings = Settings(settings_dir=app_dir, verbose=True)
investor = lcinvestor.AutoInvestor(settings=settings, verbose=True)

investor.settings.get_auth_settings()
investor.settings.save()

"""
Test login
"""
if investor.authenticate():
    print 'Login successful!'
else:
    print 'Login failed!'
