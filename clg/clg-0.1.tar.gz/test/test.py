#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os.path as path
ROOT = path.dirname(__file__)
sys.path.append(path.join(ROOT, '..'))
import clg

def main():
#    command = clg.CommandLine(path.join(ROOT, 'basic.yml'), 'yaml')
#    command = clg.commandLine(path.join(ROOT, 'test.yml'), 'yaml')
    command = clg.CommandLine(path.join(ROOT, 'kvm_options.yml'), 'yaml')
    command.parse()

if __name__ == '__main__':
    main()
