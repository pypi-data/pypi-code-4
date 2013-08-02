from collective.grok import gs
from collective.qabank import MessageFactory as _

@gs.importstep(
    name=u'collective.qabank', 
    title=_('collective.qabank import handler'),
    description=_(''))
def setupVarious(context):
    if context.readDataFile('collective.qabank.marker.txt') is None:
        return
    portal = context.getSite()

    # do anything here
