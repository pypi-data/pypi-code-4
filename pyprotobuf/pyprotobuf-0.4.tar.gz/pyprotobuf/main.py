#!/bin/python
import sys
import pkg_resources
import os
import logging
import argparse

from pyprotobuf.nameresolve import NameResolveVisitor
from pyprotobuf.parser import ProtoParser
from pyprotobuf.commentresolver import CommentResolver

ENTRYPOINT = 'pyprotobuf.generators'

def main(args=None):
    
    generators = {}
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
        parser.add_argument('paths', nargs="+")
        args = parser.parse_args()
        
    logging.basicConfig(level=logging.INFO)
    format = args.format
        
    if format not in generators:
        raise Exception('Wrong format! Expected  {0} Got:'.format(', '.join(generator_names)))    
    
    generator_class = generators[format]
    
    out = []
    for path in args.paths:
       string = open(path).read()
       out.append(parse_and_generate(string, path, generator_class))
    
    return ''.join(out)
    
def parse_and_generate(string, path, generator_class):
    parser = ProtoParser()
    protonode = parser.parse_string(string)
    
    # so the generators know the path 
    protonode.filename = path

    # resolve name references between messages/etc
    name_resolver = NameResolveVisitor()
    name_resolver.visit(protonode)

    # associate comments with suceeding nodes 
    comment_resolver = CommentResolver()
    comment_resolver.visit(protonode)
    
    generator = generator_class()
    return generator.to_src(protonode)
 
def _main():
    sys.stdout.write(main())
    
if __name__ == '__main__':
    _main()
