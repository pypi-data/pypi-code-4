import sys
import argparse
import logging

from clover.closure.client import Client
from clover.command import Command
from clover.config.multiconfig import MultiDocConfig
from clover.closure.messageextractor import MessageExtractor

argparser = argparse.ArgumentParser()
argparser.add_argument('config')
argparser.add_argument('id')
argparser.add_argument('-p', '--project', default=None, help="The project id used for the id generator.")
argparser.add_argument('-o', '--output', default=None, help="An output file. Messages can be merged with -m.")
argparser.add_argument('-m', '--merge', default=False, help="Merge generated with output file.")
argparser.add_argument('-d', '--delete', default=False, action="store_true", help="Delete keys in output not in generated.")

try:
  from lxml import etree
  print("running with lxml.etree")
except ImportError:
  try:
    # Python 2.5
    import xml.etree.cElementTree as etree
    print("running with cElementTree on Python 2.5+")
  except ImportError:
    try:
      # Python 2.5
      import xml.etree.ElementTree as etree
      print("running with ElementTree on Python 2.5+")
    except ImportError:
      try:
        # normal cElementTree install
        import cElementTree as etree
        print("running with cElementTree")
      except ImportError:
        try:
          # normal ElementTree install
          import elementtree.ElementTree as etree
          print("running with ElementTree")
        except ImportError:
          print("Failed to import ElementTree from any known place")

from collections import OrderedDict

class Merger(object):
    delete = False
    
    def __init__(self):
        pass
    
    def merge(self, input, output):
        messages_map = OrderedDict()
        
        # parse input messages mapping ids to elements        
        dom = etree.fromstring(open(input).read())
        for msg in dom:
            messages_map[msg.get('id')] =  msg

        output = open(output).read()

        # parse output file, merge translations
        dom = etree.fromstring(output)
        old = {}
        updated = set()
        for node in dom:
            ids = node.get('id')
            old[ids] = node
            
            # existing messages should be updated
            if ids in messages_map:
                logging.debug('Updating %s', ids)
                new_node = messages_map[ids]
                node.set('desc',  new_node.get('desc'))
                node.set('name',  new_node.get('name'))
                
                for child in node:
                    node.remove(child)
                for child in new_node:
                    node.append(child)
                    
                updated.add(ids)
                del messages_map[ids]
                continue
        
        # add any new        
        for id, msg in messages_map.items():
            dom.append(msg)
        
        # delete any missing if requested
        if self.delete:
            removed = set(old.keys()) - updated
            # remove any old
            logging.debug('Removed %s', removed)
            
            for r in removed:
                dom.remove(old[r])
                    
        return etree.tostring(dom)

import operator

class Messages(Command):
    def start(self, args):
        parsed_args = argparser.parse_args(args)
        
        mdc = MultiDocConfig.from_file(parsed_args.config)
        config = mdc.get_config(parsed_args.id)
        
        if not config:
            print "Invalid config id:", parsed_args.id
            print "Available:", map(operator.methodcaller('get_id'), mdc.get_configs())
            sys.exit(-1)
            
        manifest = config.get_build_manifest() 
        
        client = Client()
        
        # TODO: improve error logging
        
        extractor = MessageExtractor(client, parsed_args.project)
        extractor.set_sources(manifest.get_sorted_deps())
        
        output = extractor.extract()
        
        if parsed_args.output:
            if parsed_args.merge:
                merger = Merger()
                merger.delete = parsed_args.delete
                output_data = merger.merge(output.filename, parsed_args.output)
            else:
                output_data = output.read()
                
            with open(parsed_args.output) as f:
                f.write(output_data)
        else:
            print output.read()
        
if __name__ == '__main__':
    Messages.run(sys.argv[1:])