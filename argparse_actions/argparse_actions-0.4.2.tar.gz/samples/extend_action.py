#!/usr/bin/env python
# encoding: utf-8
'''
extend_action.py
================

This sample demonstrates how to extend the existing custom action to 
add functionality. In this example, we will extend the 
ProperIpFormatAction class to accept 'localhost' as a proper IP address.

Examples::

    python extend_action.py 10.0.1.2
    python extend_action.py localhost
    
'''

import argparse
import argparse_actions

class IpAndLocalhostAction(argparse_actions.ProperIpFormatAction):
    def __call__(self, parser, namespace, values, option_string=None):
        # Do our check: allow for 'localhost'
        if values == 'localhost':
            setattr(namespace, self.dest, values)
        else:
            # Super class to perform its check
            parent = super(IpAndLocalhostAction, self)
            parent.__call__(parser, namespace, values, option_string)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Custom Actions')
    parser.add_argument('ip', action=IpAndLocalhostAction)
    
    try:
        args = parser.parse_args()
        print 'IP is valid: {0}'.format(args.ip)
    except argparse_actions.InvalidIp as e:
        print e 
