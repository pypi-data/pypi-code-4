#!/bin/python
import sys
import pkg_resources
import os
import logging
import argparse


from pyprotobuf.compiler import Compiler

import pyprotobuf.generators.closurelib
import pyprotobuf.generators.protorpc
import pyprotobuf.generators.externs

ENTRYPOINT = 'pyprotobuf.generators'

GENERATORS = {
    'closure': pyprotobuf.generators.closurelib,
    'python': pyprotobuf.generators.protorpc,
    'externs':  pyprotobuf.generators.externs
}


def main(args=None):
    
    generators = {}

    # include default generators
    for name, module in GENERATORS.items():
        generators[name] = getattr(module, '__generator__', None)

    # search for entrypoints defined in setup.py or extended with plugins
    # generator modules are defined in [pyprotobuf.generators]
    # generator module must have a __generator__ symbol pointing to a generator class
    for entrypoint in pkg_resources.iter_entry_points(ENTRYPOINT):
         module = entrypoint.load()
         generators[entrypoint.name] = getattr(module, '__generator__', None)


    generator_names = generators.keys()
    
    if args is None:
        parser = argparse.ArgumentParser()
        parser.add_argument('--format', choices=generator_names, dest='format', default='externs')
        parser.add_argument('--debug', '-d', default=False, action='store_true')
        parser.add_argument('paths', nargs="+")
        args = parser.parse_args()

    level = logging.INFO

    if getattr(args, 'debug'):
        level = logging.DEBUG

    logging.basicConfig(level=level)
    format = args.format
        
    if format not in generators:
        raise Exception('Wrong format! Expected  {0} Got:'.format(', '.join(generator_names)))    
    
    generator_class = generators[format]
    
    out = []
    for path in args.paths:
       path = os.path.abspath(path)
       string = open(path).read()
       out.append(parse_and_generate(string, path, generator_class))
    
    return ''.join(out)
    
def parse_and_generate(string, path, generator_class):
    compiler = Compiler(generator_class)
    return compiler.compile_string(path, string)

 
def _main():
    sys.stdout.write(main())
    
if __name__ == '__main__':
    _main()
