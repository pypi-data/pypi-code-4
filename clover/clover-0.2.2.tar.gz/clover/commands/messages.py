# http://www.gnu.org/software/gettext/manual/html_node/gettext_9.html#PO-Files

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
argparser.add_argument('-s', '--sources', default=False, action="store_true", help="Include sources.")
argparser.add_argument('-P', '--pot', default=False, action="store_true", help="Output pot file.")





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

    sources = True

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

def clean_output(output_data, include_sources=True):
    dom = etree.fromstring(output_data)

    for node in dom:
        if not include_sources:
            node.attrib.pop('source')

    return etree.tostring(dom)


def transform_to_pot(output_data):
    """
    #: modules/user/views_handler_filter_user_name.inc:29
    msgid "Enter a comma separated list of user names."
    msgstr ""

    :param output_data:
    :return:
    """
    string = []
    dom = etree.fromstring(output_data)

    seen = set()

    for node in dom:

        if not node.text:
            logging.warning('Invalid message %s', node)
            continue

        id =  node.get('id')

        if id in seen:
            continue

        seen.add(id)

        # preserve and encode the id/name
        id = '%s___%s' % (node.get('name'), node.get('id'))

        message = node.text.encode('string_escape')

        string.append('#: %s:0\n' % node.get('source'))
        string.append('msgid "%s"\n' % id)
        string.append('msgstr "%s"\n\n' % message)

    return ''.join(string)

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
        
        if parsed_args.output and parsed_args.merge:
            # output file and merge option enabled
            merger = Merger()
            merger.delete = parsed_args.delete
            output_data = merger.merge(output.filename, parsed_args.output)
        else:
            output_data = output.read()

        if not parsed_args.pot:
            output_data = clean_output(output_data, include_sources=parsed_args.sources)

        if parsed_args.pot:
            output_data = transform_to_pot(output_data)


        if parsed_args.output:
            with open(parsed_args.output, 'w') as f:
                f.write(output_data)
        else:
            print output_data



        
if __name__ == '__main__':
    Messages.run(sys.argv[1:])