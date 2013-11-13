from collective.grok import gs
from collective.pdfexport import MessageFactory as _

@gs.importstep(
    name=u'collective.pdfexport', 
    title=_('collective.pdfexport import handler'),
    description=_(''))
def setupVarious(context):
    if context.readDataFile('collective.pdfexport.marker.txt') is None:
        return
    portal = context.getSite()

    # do anything here
