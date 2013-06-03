################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id$

import urllib
from cgi import escape

from interfaces import IVBBView
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from plone.memoize.instance import memoize

class ImageView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    # TODO: eventuell nicht default image sonder im schema nach dem ersten image suchen ?
    def tag(self,fieldid=None,scale=None, height=None, width=None, alt=None,css_class=None, title=None, **kwargs):
        """ tag
        """
        if fieldid is None:
            fieldid = 'image'
        field = self.context.getField(fieldid)
        image = field.getScale(self.context, scale=scale)
        if image:
            img_width, img_height = field.getSize(self.context, scale=scale)
        else:
            img_height=0
            img_width=0

        if height is None:
            height=img_height
        if width is None:
            width=img_width

        url = self.context.absolute_url()
        url+= '/image_' + fieldid
        if scale:
            url+= '_' + scale

        values = {
            'src' : url,
            'alt' : escape(alt and alt or self.context.Title(), 1),
            'title' : escape(title and title or self.context.Title(), 1),
            'height' : height,
            'width' : width,
        }

        result = '<img src="%(src)s" alt="%(alt)s" title="%(title)s" '\
            'height="%(height)s" width="%(width)s"' % values

        if css_class is not None:
            result = '%s class="%s"' % (result, css_class)

        for key, value in kwargs.items():
            if value:
                result = '%s %s="%s"' % (result, key, value)

        return '%s />' % result
        # return self.context.getField('image').tag(self.context , **kwargs)

    def getImageSize(self, fieldid=None, scale=None):
        """ image size """
        if fieldid is None:
            fieldid = 'image'
        field = self.context.getField(fieldid)
        return field.getSize(self.context,scale=scale)

    def getReferenceImage(self, fieldid=None):
        """ return referenced Image """
        return self.context.getImageReference()

