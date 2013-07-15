import logging
from Products.Five import BrowserView
from Solgema.EnvironmentViewlets.viewlets.common import BackgroundViewlet

LOG = logging.getLogger('SEV')

class SolgemaEnvironmentViewletsCSS(BrowserView):

    def backgroundsList(self):
        viewlet = BackgroundViewlet(self.context, self.request, self)
        viewlet.update()
        return viewlet.backgroundsList()

    def backgroundClass(self):
        backgrounds = self.backgroundsList()
        if not backgrounds:
            return ''
        background = backgrounds[0]
        cssClass = background['cssClass']
        out = 'body {\n'
        out += '    background-image:url('+background['url']+') !important;\n'
        out += '    background-position:'+background['align']+' top !important;\n'
        out += '    background-repeat:'+background['repeat']+' !important;\n'
        if 'backgroundExtend' in cssClass:
            out += '    background-size:100% auto !important;\n'
        if 'backgroundFixed' in cssClass:
            out += '    background-attachment:fixed !important;\n'
            
        out += '}\n'
        return out

    def __call__(self):
        return"""
#portal-bandeau,
#solgema-portal-footer {
    clear:both;
    position:relative;
}

#inner-portal-bandeau,
#inner-solgema-portal-footer {
    overflow:hidden;
    position:relative;
    width:100%;
}

.carousel-banner {
    position:absolute;
    width:inherit;
    top:0;
    left:0;
}

#portal-printlogo {
    display:none;
}

#solgemabandeau {
    clear:both;
    position:relative;
}

#solgemaprintfooter {
    display:none;
    clear:both;
    bottom:0;
    right:0;
    float:left;
    width:100%;
}

#solgemabackground {
    position:absolute;
    top:0;
    left:0;
    z-index:0;
    width:100%;
    display:none;
}
.backgroundRepeat {
    background-repeat:repeat;
}
.backgroundFixed {
    background-attachment:fixed !important;
}
.backgroundExtend {
    background-size:100% auto !important;
}
.bandeau_image {
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.5) inset;
}
#solgemabackground .bandeau_image {
    box-shadow: none;
}
"""+self.backgroundClass()
