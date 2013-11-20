# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from plone.memoize.view import memoize

class SearchEventsView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        results = self.results
        try:
            results_count = results.actual_result_count
        except AttributeError:
            results_count = len(results) # plone 3 probably
        if results_count==1:
            self.request.response.redirect(results[0].getURL(),
                                           status=302)
        return self.index()
    
    @property
    @memoize
    def results(self):
        context = self.context
        request = self.request
        use_types_blacklist = request.get('use_types_blacklist', True);
        use_navigation_root = request.get('use_navigation_root', True);

        return context.queryCatalog(REQUEST=request,
                                    use_types_blacklist=use_types_blacklist,
                                    use_navigation_root=use_navigation_root)

    def dateFromRequest(self):
        return self.request['end']['query'][0]

