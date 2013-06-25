# -*- coding: utf-8 -*-
from lxml import etree
import re
from datetime import datetime
from datetime import date
from datetime import time
from datetime import timedelta

# TODO improve name
class SemanticsMatcher(object):
    ns = {'h': 'http://www.w3.org/1999/xhtml'}
    
    def __init__(self, base_item, tree):
        self.base_item = base_item
        self.tree = tree
    
    def html_xpath(self, node, expr):
        return node.xpath(expr, namespaces=self.ns)
    
    def html_xpath_text(self, node, expr):
        nodes = node.xpath(expr, namespaces=self.ns)
        if nodes:
            return nodes[0].text
        else:
            return ""
    
    def html_find(self, node, expr):
        return node.find(expr, namespaces=self.ns)
    
    def html_find_text(self, node, expr):
        return unicode(self.html_find(node, expr).text)
    
    def collect_texts(self, node, expr):
        return ''.join(self.html_xpath(node, expr + '/descendant-or-self::text()'))
    
    def calculate_enddatetime(self, startdatetime, endtime):
        at_same_day = datetime.combine(startdatetime.date(), endtime)
        
        if at_same_day > startdatetime:
            return at_same_day
        else:
            return datetime.combine(startdatetime.date() + timedelta(1), endtime)
    
    # TODO Are these substring functions not part of standard python libraries???
    def substring_before(self, s, substring):
        try:
            return s[:s.index(substring)]
        except ValueError:
            return ""
        
    def substring_after(self, s, substring):
        try:
            start = s.index( substring ) + len( substring )
            return s[start:]
        except ValueError:
            return ""
        
    def substring_between(self, s, first, last):
        return self.substring_before(self.substring_after(s, first), last)
    
    def next_possible_date(self, month, day):
        this_year = datetime.today().replace(month=month).replace(day=day)
        
        if this_year > datetime.today():
            return this_year
        
        return (datetime.today() + timedelta(365)).replace(month=month).replace(day=day)
            
    # abstract method
    def event_node_iter(self):
        pass
    
    # abstract method
    def process_event_node(self, item, event_node):
        pass
    
    def __iter__(self):
        for event_node in self.event_node_iter():
            item = self.base_item.copy()
            self.process_event_node(item, event_node)
            yield item