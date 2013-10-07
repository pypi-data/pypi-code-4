from zope.app.container.interfaces import IObjectAddedEvent
from five import grok
from plone.directives import dexterity, form


from plone.namedfile.interfaces import IImageScaleTraversable


# Interface class; used to define content-type schema.
class ISection(form.Schema, IImageScaleTraversable):
    """
    Section of the factsheet
    """


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.
class Section(dexterity.Container):
    grok.implements(ISection)
    # Add your class methods and properties here


@grok.subscribe(ISection, IObjectAddedEvent)
def exclude_from_nav(context, event):
    context.exclude_from_nav = True
