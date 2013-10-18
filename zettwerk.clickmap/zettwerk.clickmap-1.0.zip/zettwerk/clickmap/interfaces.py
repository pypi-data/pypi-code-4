from zope.interface import Interface
from zope import schema
from zettwerk.clickmap import clickmapMessageFactory as _


class IClickmapOutput(Interface):
    """ """

    output = schema.TextLine(title=_("Output"))
    
    
class IClickmapSettings(Interface):
    """ """

    enabled = schema.Bool(title=_(u"Enabled"),
                          description=_(u"Enable clickmap logging"),
                          )

    ## the followings two are only used to display some form widgets
    setup = schema.TextLine(title=_("Setup"))

    reset = schema.TextLine(title=_("Reset"))
    
    output_width = schema.Int(title=_(u"Output width in pixel"),
                              description=_(u"To unify the different client resolutions, the output gets transformed to this output width. Clicks outside this width are not logged."),
                              )
    
    right_align_threshold = schema.Int(title=_(u"Right align threshold"),
                                       description=_(u"By using a variable layout, the clickmap must know, where the right side of the page starts. This is only an approximated value."),
                          )
                              
    output_height = schema.Int(title=_(u"Output height in pixel"),
                               description=_(u"Clicks outside this height are not logged."),
                               )
    
    pages = schema.List(title=_(u"Pages"),
                        description=_(u"Select the pages, which should be logged"),
                        value_type=schema.Choice(__name__='page', title=_(u"Page"),
                                                 vocabulary="zettwerk.clickmap.ListPagesVocabulary",
                                                 )
                        )


class IClickmap(IClickmapSettings, IClickmapOutput):
    """ Mixin interface """
    pass
