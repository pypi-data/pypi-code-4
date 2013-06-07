#!/usr/bin/env python
# encoding: utf-8
'''
proper_ip.py
================

This sample demonstrate the ProperIpFormatAction custom action.

Examples::

    python proper_ip.py 10.0.1.2
    python proper_ip.py 10.0.1.256
    
'''

import argparse
import argparse_actions

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Custom Actions')
    parser.add_argument('ip', action=argparse_actions.ProperIpFormatAction)
    
    try:
        args = parser.parse_args()
        print 'IP is properly formatted: {0}'.format(args.ip)
    except argparse_actions.InvalidIp as e:
        print 'IP is invalid: {0}'.format(e.ip)
        # This will display similar output:
        # print e 
