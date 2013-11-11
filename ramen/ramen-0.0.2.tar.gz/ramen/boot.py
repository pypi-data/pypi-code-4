
from tornado import httpserver, ioloop, web
from ramen.urls import include
from ramen.decorators import asynchronize
import os
import gettext

class Bootstrap(object):

    def __init__(self, port, **settings):
        
        settings['template_path'] = os.path.join(os.getcwd(), 'templates')
        
        app = web.Application(include(r'^/', 'urls'), **settings)
        server = httpserver.HTTPServer(app)
        if settings['debug']:
            server.listen(port)
        else:
            server.bind(port)
            server.start(0)
        
        ioinst = ioloop.IOLoop.instance()
        
        app.asynchronize = asynchronize(ioinst)
        app.translators = self.install_translators()
        
        try:
            print 'Starting on 0.0.0.0:%s' % port
            ioinst.start()
        except:
            ioinst.stop()
    
    def install_translators(self):
        locale_path = os.path.join(os.getcwd(), 'locales')
        translators = {}
        
        if os.path.exists(locale_path) and os.path.isdir(locale_path):
            for lang in os.listdir(locale_path):
                lc_messages = os.path.join(locale_path, lang, 'LC_MESSAGES')
                if os.path.isdir(lc_messages) and os.path.isfile(os.path.join(lc_messages, 'messages.mo')):
                    try:
                        trans = gettext.translation('messages', os.path.join(os.getcwd(), 'locales'), [lang])
                        translators[lang] = trans
                    except:
                        print 'Translator fail on load %s' % os.path.join(lc_messages, 'messages.mo')
            
        return translators