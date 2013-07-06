from zope.i18nmessageid import MessageFactory
from collective.plonetruegallery.utils import createSettingsFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from collective.plonetruegallery.browser.views.display import BaseDisplayType
from collective.plonetruegallery.interfaces import IBaseSettings
from zope import schema

_ = MessageFactory('collective.ptg.bootstrapcarousel')

class IBootstrapcarouselDisplaySettings(IBaseSettings):
    bc_width = schema.TextLine(
            title=_(u"label_bc_width",
                default=u"Width of the carousel in pixels or percentage"),
            default=u"100%")
    bc_height = schema.TextLine(
            title=_(u"label_bc_height",
                default=u"Height of the carousel in pixels or percentage"),
            default=u"480px")
    bc_interval = schema.Int(
            title=_(u"label_bc_interval",
                default=u"The amount of time to delay between automatically cycling an item"),
            default=5000)

class BootstrapcarouselDisplayType(BaseDisplayType):

    name = u"bootstrapcarousel"
    schema = IBootstrapcarouselDisplaySettings
    description = _(u"label_bc_display_type",
            default=u"Boostrap Carousel")

    def javascript(self):
        return u"""
    <script type="text/javascript"
    src="%(portal_url)s/++resource++ptg.bootstrapcarousel/bootstrap.min.js">
    </script>
    <script type="text/javascript">
    $(document).ready(function(){
        $('.carousel').carousel({
            interval: %(interval)i,
            pause: "hover",
        })
    });
    </script>
    """ % {
            'portal_url': self.portal_url,
            'interval': self.settings.bc_interval,
            }

    def css(self):
        img_width="100%"
        img_height= self.settings.bc_height
        caption_width="51%"
        inner_item_width="100%"

        return u"""
    <link rel="stylesheet" type="text/css"
    href="%(portal_url)s/++resource++ptg.bootstrapcarousel/bootstrap.min.css" />
    <style type="text/css">
    #bootstrapcarousel {
        width:%(width)s;
        height:%(height)s;
        line-height: 25px !important;
    }
    #bootstrapcarousel .carousel-inner,
    .carousel-inner item,
    .carousel-inner item-inner{
        height:auto;
    }
    #bootstrapcarousel img {
        width:%(img_width)s;
        height:%(img_height)s;
    }
    a.carousel-control {
        border-radius: 35px 35px 35px 35px;
        font-size: 55px;
        height: 35px;
        line-height: 20px;
        width: 35px;
    }
    #bootstrapcarousel .bootstrapcarousel-caption {
        background: none repeat scroll 0 0 rgba(0, 0, 0, 0.25);
        float: right;
        padding: 25px;
        position: absolute;
        right: 0;
        top: 10px;
        width: %(caption_width)s;
    }
    #bootstrapcarousel h1 {
         color: rgb(255,255,255);
         font-size: 34px;
         font-weight: normal;
    }
    #bootstrapcarousel .item-inner {
        background-color: rgba(0, 0, 0, 0.1);
        display: block;
        position: relative;
        width: %(inner_item_width)s;
    }
    </style>
    """ % {
            'portal_url': self.portal_url,
            'width': self.settings.bc_width,
            'height': self.settings.bc_height,
            'img_width': img_width,
            'img_height': img_height,
            'caption_width': caption_width,
            'inner_item_width': inner_item_width,
            }

BootstrapcarouselSettings = createSettingsFactory(BootstrapcarouselDisplayType.schema)
