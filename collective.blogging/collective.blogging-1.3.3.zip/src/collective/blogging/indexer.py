from plone.indexer import indexer

from collective.blogging.interfaces import IEntryMarker, IBlogMarker

@indexer(IEntryMarker)
def year(obj):
    date = obj.getEffectiveDate() or obj.created()
    if date:
        return date.year()

@indexer(IEntryMarker)
def month(obj):
    date = obj.getEffectiveDate() or obj.created()
    if date:
        result = str(date.month())
        return (len(result) < 2) and ("0%s" % result) or result

@indexer(IBlogMarker)
def blogged(obj):
    return True

            
