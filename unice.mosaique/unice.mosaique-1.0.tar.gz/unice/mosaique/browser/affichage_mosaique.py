from Products.Five import BrowserView

from collective.contentleadimage.config import IMAGE_FIELD_NAME
from collective.contentleadimage.config import IMAGE_CAPTION_FIELD_NAME
from zope.component import getMultiAdapter
from Acquisition import aq_inner

class AffichageMosaique(BrowserView):

    def itemDetails(self, item):

        image = None
        if hasattr(item, 'tag'):
            image = item.tag(scale='large', css_class='')
        leadimage = self.contentLeadImage(item)
        if leadimage:
            image = leadimage

        return {'type': item.portal_type, 'image': image, 'date': self.eventDate(item), 'location': self.eventLocation(item)}

    def contentLeadImage(self, item, css_class=''):
        context = aq_inner(item)
        field = context.getField(IMAGE_FIELD_NAME)
        titlef = context.getField(IMAGE_CAPTION_FIELD_NAME)
        if titlef is not None:
            title = titlef.get(context)
        else:
            title = ''
        if field is not None:
            if field.get_size(context) != 0:
                return field.tag(context, scale='large', css_class=css_class, title=title)
        return None


    def eventDate(self, item):
        if not item.portal_type == 'Event': return None

        plone = getMultiAdapter((self.context, self.request), name="plone")
        item_startdate = plone.toLocalizedTime(item.start())
        item_enddate = plone.toLocalizedTime(item.end())
        item_samedate = item.end() - item.start() < 1
        return item_startdate if item_samedate else '%s - %s' % (item_startdate, item_enddate)

    def eventLocation(self, item):
        if not item.portal_type == 'Event': return None
        return item.location if item.location else None
