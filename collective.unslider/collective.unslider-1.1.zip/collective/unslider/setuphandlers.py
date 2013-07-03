from collective.grok import gs
from collective.unslider import MessageFactory as _

@gs.importstep(
    name=u'collective.unslider', 
    title=_('collective.unslider import handler'),
    description=_(''))
def setupVarious(context):
    if context.readDataFile('collective.unslider.marker.txt') is None:
        return
    portal = context.getSite()

    # do anything here
