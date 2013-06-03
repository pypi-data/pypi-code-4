# -*- coding: utf-8 -*-

# imports
import cherrypy
from os.path import join
import vispa
from vispa.helpers import browser
from vispa.models.stats import AccessStats, PageStats

class StatsTool(cherrypy.Tool):

    def __init__(self):
        cherrypy.Tool.__init__(self, 'before_handler', self._record, priority=90)

    def _record(self, page=None):
        AccessStats.click(cherrypy.request.db, unicode(browser.client_ip()), unicode(browser.client_agent()))
        if page:
            PageStats.click(cherrypy.request.db, unicode(page))
