#!/usr/bin/env python

from __future__ import print_function

def install_requirements(requirements, verbose=True):
    import os, pip
    pip_args = list()
    if verbose:
        print('Installing requirements: ' + str(requirements))
        pip_args.append( '--verbose' )
    proxy = os.environ['http_proxy']
    if proxy:
        if verbose:
            print('http_proxy=' + proxy)
        pip_args.append('--proxy')
        pip_args.append(proxy)
    pip_args.append('install')
    for req in requirements:
        pip_args.append( req )
    pip.main(initial_args = pip_args)
