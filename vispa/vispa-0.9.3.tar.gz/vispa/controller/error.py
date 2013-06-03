# -*- coding: utf-8 -*-

import vispa
import cherrypy


class ErrorController(object):
    ''' This class provides custom error-catching
        functions that are inserted into the cherrypy config.
    '''
    
    STATUSMAP = {'400': 'badrequest',
                 '401': 'unauthorized',
                 '403': 'forbidden',
                 '404': 'filenotfound',
                 '408': 'requesttimeout',
                 '500': 'internalservererror'}
    
    def __init__(self):
        # dynamic function setting
        for key, value in self.STATUSMAP.items():
            cherrypy.config.update({'error_page.%s' % key: self.__error})
            
            @cherrypy.expose
            @cherrypy.tools.render(template='%s.html' % key, subfolder='html/error')
            def func():
                return self.get_error_data()
            
            setattr(self, value, func)

    @cherrypy.expose
    def index(self, *args, **kwargs):
        base = vispa.url.base_static
        raise cherrypy.HTTPRedirect(base, status=301)

    def get_error_data(self):
        key = 'error_data'
        if key in cherrypy.session:
            data = cherrypy.session[key]
            del cherrypy.session[key]
            return data
        else:
            return {}

    def __error(self, status, message, traceback, version):
        cherrypy.session['error_data'] = {'status': status, 'message': message, 'traceback': traceback, 'version': version}
        page = self.STATUSMAP[status.split(' ')[0]]
        return '<html><head><meta http-equiv=\'refresh\' content=\'0;url=%serror/%s\' /></head></html>' % (vispa.url.dynamic('/'), page)