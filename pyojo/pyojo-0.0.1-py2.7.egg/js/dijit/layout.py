# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------
""" Page layout widgets.
"""

from ..dijit import Dijit


class ContentPane(Dijit):
    """ Simple panel.
    """
    
    require = ["dojo/ready", 
               "dijit/layout/ContentPane"]

    def add(self, target):
        #self.loc += "%s.addChild(%s);\n" % (target, self.name)
        return self.add_loc("%s.addChild(%s);" % (target, self.name))

    def select(self, target):
        return self.add_loc("%s.selectChild(%s);" % (target, self.name))



class BorderContainer(Dijit):
    """ A parent panel who contains other panels.
    """
    require = ["dojo/ready", 
               "dijit/layout/BorderContainer", 
               "dijit/layout/ContentPane"]

    
    def init(self):
        style = 'height: 100%; width: 100%;background-color:rgb(239, 239, 239);'
        self.member.update({'style': style, 'gutters': False})
        #self.panel(style="background-color:transparent")

    def panel(self, region="center", name=None, style=None, **kwargs):
        if name is None: 
            name = self.name+"_"+region
        if style is None: style = "padding:0px; margin:0px;"
        new =  ContentPane(name, 
                           region=region, 
                           style=style, 
                           **kwargs).new(False)
        self.loc += "%s.addChild(%s);" % (self.name, new)



class DijitPanelMixin(object):
    """ Provides the panel method for containers.
    """
    
    def init(self):
        self.member.update({'style':'height: 100%; width: 100%;'})


    def panel(self, name=None, title="", style=None, **kwargs):
        if style is None: style = "padding:0px; margin:0px;"
        new =  ContentPane(name, 
                           title=title, 
                           style=style, 
                           **kwargs).new(False)
        self.loc += "%s.addChild(%s);" % (self.name, new)





class AccordionContainer(DijitPanelMixin, Dijit):
    require = ["dojo/ready", 
               "dijit/layout/AccordionContainer", 
               "dijit/layout/ContentPane"]

    

class TabContainer(DijitPanelMixin, Dijit):
    require = ["dojo/ready", 
               "dijit/layout/TabContainer", 
               "dijit/layout/ContentPane"]

    

        


