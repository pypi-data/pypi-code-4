# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from collective.cmisbrowser.errors import CMISConnectorError
from collective.cmisbrowser.cmis.api import CMISZopeAPI
from Products.Five import BrowserView


class CMISQueryView(BrowserView):
    """CMIS Query view
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.results = []
        self.feedback = u''

    def update(self):
        browser = self.context.getBrowser()
        if browser is not None:
            try:
                api = CMISZopeAPI(browser)
                self.results = api.query(self.context.query)
            except CMISConnectorError:
                self.feedback = u'Connector error.'
        else:
            self.feedback = u'Browser not configured.'
        return self.results
