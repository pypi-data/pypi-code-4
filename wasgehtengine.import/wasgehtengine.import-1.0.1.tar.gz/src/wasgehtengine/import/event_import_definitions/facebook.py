# -*- coding: utf-8 -*-
from lxml import etree
import re
from datetime import datetime
from datetime import timedelta
from urlparse import urljoin
from importlib import import_module
SemanticsMatcher = import_module('wasgehtengine.import.semanticsmatcher').SemanticsMatcher
from lxml.html import html5parser

def parse_hidden_elements(node):
    hidden_elem_seq = node.xpath('//h:code/comment()', namespaces={'h': 'http://www.w3.org/1999/xhtml'})
    
    if len(hidden_elem_seq) == 0:
        return None
    
    hidden_elems_string = '<body>'
    
    for hidden_elem_comment in hidden_elem_seq:  
        hidden_elems_string += etree.tostring(hidden_elem_comment)[5:-4]
        
    
    hidden_elems_string += '</body>'

    parsed_hidden_elems = html5parser.fromstring(hidden_elems_string)
    
    return parsed_hidden_elems 

class FacebookEventlinksParser(SemanticsMatcher):
        
    def event_node_iter(self):       
        return self.html_xpath(parse_hidden_elements(self.tree), '//h:table[@class ="uiGrid eventsGrid"]')
        
    def process_event_node(self, item, event_node):
        
        rel_url = self.html_xpath(event_node, './/h:a[1]/@href')[0]
        abs_url = urljoin(item['page_url'], rel_url)
        item['page_url'] = abs_url

class FacebookEventParser(SemanticsMatcher):
        
    def event_node_iter(self):
        #print(etree.tostring(self.tree))
        return [self.tree]
        
    def process_event_node(self, item, event_node):
        parsed_hidden_elem_title = parse_hidden_elements(event_node)
        parsed_hidden_elem_details = parse_hidden_elements(event_node)
        
        item['title'] = self.html_xpath_text(parsed_hidden_elem_title, './/h:div[@itemprop="summary"]')
        item['description'] =  self.collect_texts(parsed_hidden_elem_details, './/h:span[@itemprop="description"]')
        
        period_string = self.html_xpath(parsed_hidden_elem_details, './/h:div[@itemprop = "startDate"]/@content')[0]
        item['start_datetime'] = datetime.strptime(period_string[:19], '%Y-%m-%dT%H:%M:%S') + timedelta(hours=9)
        #endtime = (datetime.strptime(period_string[20:], '%H:%M') + timedelta(hours=9)).time()
        #item['end_datetime'] = self.calculate_enddatetime(item['start_datetime'], endtime)
        item['end_datetime'] = None