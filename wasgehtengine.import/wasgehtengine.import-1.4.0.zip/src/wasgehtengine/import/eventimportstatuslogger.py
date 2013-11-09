from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from transmogrify.pathsorter.treeserializer import TreeSerializer
from datetime import datetime

import logging

class EventImportStatusLogger(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = TreeSerializer(transmogrifier, name, options, previous)
        self.context = transmogrifier.context
        self.logger = logging.getLogger(name)
        self.count = 0;

        self.response = options.get('response','')

    def __iter__(self):
        for item in self.previous:
            
            if 'ignore' in item and item['ignore'] == True:
                
                item['_path'] = '/eventimportstatus/' + item['venue'].to_path.split('/')[-1]
                
                now = datetime.now()
                
                item['creators'] = ['event-importer']
                item['transitions'] = ["publish"]
                item['title'] = '"' + item['venue'].to_object.title + '" event import status'
                item['last_run'] = now
                
                pytransform_errors = item.get('pytransform_errors', [])
                xmlparser_errors = item.get('xmlparser_errors', [])
                htmlparser_errors = item.get('htmlparser_errors', [])
                eventlinksparser_errors = item.get('eventlinksparser_errors', [])
                xsltransform_errors = item.get('xsltransform_errors', [])
                
                item['all_errors'] = ''.join(pytransform_errors + xmlparser_errors + htmlparser_errors + eventlinksparser_errors + xsltransform_errors)
                
                if len(item['all_errors']) == 0:
                    item['last_successful_run'] = now
                
                if self.count > 0:
                    item['last_run_with_events_imported'] = now
                    
                item['imported_events_count'] = self.count
                
                yield item
                continue
            
            self.count += 1
            yield item
