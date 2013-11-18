#!/usr/bin/env python
# encoding: utf-8
"""
cliauth.py

Django External Authenticator for apache2 mod-auth-external

Created by Sergio Campos on 2012-01-10.
"""

import sys
from optparse import make_option

from django.core.management.base import BaseCommand

try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
else:
    User = get_user_model()


class Command(BaseCommand, object):
    """Django External Authenticator for apache2 mod-auth-external"""

    help = __doc__

    option_list = BaseCommand.option_list + (
        make_option(
            '-g', 
            '--group-check', 
            dest='groupcheck',
            action='store_true',
            default=False,
            help='Check if a user belongs to a group.'),
    )

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
   

    def auth(self):
        username = sys.stdin.readline().strip()
        password = sys.stdin.readline().strip()

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            sys.exit(1)
        
        if not user.check_password(password):
            sys.exit(1)
        
        # If returning 0 the password matches
  
    
    def groupcheck(self):
        username = sys.stdin.readline().strip()
        group = sys.stdin.readline().strip()
        
        try:
            user = User.objects.get(username=username, groups__name=group)
        except User.DoesNotExist:
            sys.exit(1)
        
        # If returning 0 the the user belongs to the group 
        
     
    def handle(self, *args, **options):
        """Main command method."""
     
        if options.get('groupcheck'):
            self.groupcheck()
        else:
            self.auth()

