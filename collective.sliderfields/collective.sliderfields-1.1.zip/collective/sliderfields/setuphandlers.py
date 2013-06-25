from collective.grok import gs
from collective.sliderfields import MessageFactory as _

@gs.importstep(
    name=u'collective.sliderfields', 
    title=_('collective.sliderfields import handler'),
    description=_(''))
def setupVarious(context):
    if context.readDataFile('collective.sliderfields.marker.txt') is None:
        return
    portal = context.getSite()

    # do anything here
