################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id: views.py 2981 2011-03-16 10:54:12Z carsten $

from AccessControl import getSecurityManager
from BeautifulSoup import BeautifulSoup, Tag
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from .. import orgMessageFactory as _

class EmployeeView(BrowserView):
    """
    """

    def _cleanupHtml(self, html):
        """ Get hold of the main content of the HTML documents and strip
            of unwanted information.
        """

        soup = BeautifulSoup(html)
        div = soup.find('div', {'class' : 'documentContent'})
        for item in ( ('div', {'class' : 'documentByLine'}), 
                      ('div', {'class' : 'documentActions'}),
                      ('div', {'class' : 'reviewHistory'}),
                      ('h1', )):
            for e in div.findAll(*item):
                e.extract()
        return div.renderContents()

    def _canView(self, obj):
        user = getSecurityManager().getUser()
        return user.has_permission('View', obj)

