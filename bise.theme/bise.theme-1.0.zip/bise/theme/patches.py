# Patch Feedfeeder's extendedDateTime, to force creation of
# datetime objects with timezone information
# In some cases after parsing dates such as Mon, 01 Jul 2013 09:45:00 +0200
# The +0200 keeps as timezone information and Zope keeps giving
# weird ZODB errors and feedfolders and feeditems can't be removed

from DateTime import DateTime

#http://www.timeanddate.com/library/abbreviations/timezones/na/
alttzmap= dict( ndt=u'GMT-0230',
                adt=u'GMT-0300',
                edt=u'GMT-0400',
                cdt=u'GMT-0500',
                mdt=u'GMT-0600',
                pdt=u'GMT-0700',
                akdt=u'GMT-0800',
                hadt=u'GMT-0900')

def new_extendedDateTime(dt):
    """takes a very pragmatic approach to the timezone variants in feeds"""
    try:
        return DateTime(dt).toZone('UTC')
    except DateTime.SyntaxError:
        frags = dt.split()
        newtz = alttzmap.get(frags[-1].lower(), None)
        if newtz is None:
            raise
        frags[-1] = newtz
        newdt = ' '.join(frags)
        return DateTime(newdt).toZone('UTC')

import Products.feedfeeder.extendeddatetime
Products.feedfeeder.extendeddatetime.extendedDateTime = new_extendedDateTime
