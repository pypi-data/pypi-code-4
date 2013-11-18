#!/usr/bin/env python

"""Consts: Various constants used between each subpart are stored here

All settings passed in via the enviroment must be prefexied with IGOR
"""
import os

environ = lambda x: os.environ.get(defaults['APP_NAME'].upper() + "_" + x)
join = lambda *args: os.path.join(defaults['CONFIG_DIR'], *args)

defaults = {}
defaults['APP_NAME'] = "igor"
defaults['CONFIG_DIR'] = os.path.join('/etc', defaults['APP_NAME'])
defaults['CONFIG'] = join(defaults['APP_NAME'] + '.conf')
defaults['LOG_DIR'] = join('log')

def get_setting(name, cmdline, config):
    return cmdline or       \
           environ(name) or \
           config or        \
           defaults[name]

if __name__ == "__main__":
    for name, val in defaults.items():
        if name.isupper():
            print "{:<20}{}".format(name + ":", val)
