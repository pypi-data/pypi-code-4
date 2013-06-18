#!/usr/bin/env python2

from webmarkupcontainer import WebMarkupContainer
from markupfromfile import MarkupFromFile
from lxml import etree

class Page(WebMarkupContainer, MarkupFromFile):
    """
    A top-level page. Knows how to render() its component hierarchy into an lxml.etree.Element tree
    """
    def render(self, context):
        tree = self.markupFromFile()
        head = tree.find('//head')
        self.renderHead(head)
        self.renderInto(tree, context)
        return tree

    def renderString(self):
        """Convenience function: render this page as a string"""
        return etree.tostring(self.render({}))
