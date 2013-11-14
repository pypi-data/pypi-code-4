#! /usr/bin/env python
# -*- coding: UTF-8 -*-

# Enable logging
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s')

# Change the import paths to use the project local code
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Actual example program
from webalerts import App
from webalerts.sites.clien import Clien

app = App()
try:
    # Try to load config.yaml if exist
    app.from_yaml('config.yaml')
except IOError:
    # If not, ask the user
    from getpass import getpass
    print ('To reduce typing, edit config.yaml.sample and save it as config.yaml '
           'in your current working directory.')
    email_addr = raw_input('Email Address (leave blank to turn off email notification): ')
    use_gmail = email_addr and raw_input("""Select SMTP server to use to send emails:
        1. Gmail (Gmail account required)
        2. localhost
    (default 2): """) == '1'
    email_config = email_addr and {
        'class': 'webalerts.notifications.email.EmailNotification',
        'to_addrs': [email_addr],
    }
    if use_gmail:
        email_config.update({
            'host': 'smtp.gmail.com',
            'port': 587,
            'secure': True,
            'username': raw_input('Gmail Username: '),
            'password': getpass('Gmail Password: '),
        })
    app.config.update({
        'patterns': [u'네요'],
        'check_interval': 1,
        'notify_interval': 1,
        'sites': {
            'clien': {
                'class': 'webalerts.sites.clien.Clien',
                'board_ids': ['park'],
            },
        },
        'notifications': {
            'console': {
                'class': 'webalerts.notifications.console.ConsoleNotification',
            },
            'email': email_config,
        },
    })
app.run()
