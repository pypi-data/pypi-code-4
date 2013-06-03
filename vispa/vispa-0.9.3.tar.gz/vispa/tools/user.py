# -*- coding: utf-8 -*-

# imports
import cherrypy
import vispa
import os
from vispa.models.user import User
import logging

logger = logging.getLogger(__name__)

class UserTool(cherrypy.Tool):

    def __init__(self, redir_url):
        '''
        The user tool takes care of fetching the current
        logged in user to then associating it with
        the request.
        '''
        cherrypy.Tool.__init__(self, 'before_handler', self._fetch, priority=65)
        self.redir_path_nonuser = redir_url

    def _setup(self):
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach('before_finalize', self._cleanup, priority=35)

    def _fetch(self, path=None, reverse=False):
        '''
        Redirects a request dependent on 'reverse':
        False ->
            Redirect to 'path' or self.redir_path_nonuser when
            a non-user performed the request. The original requested
            path is stored as 'requested_path' in the session and may
            be used for redirection e.g. after a successful login.
        True ->
            Redirect to 'path' when a logged-in user
            performed the request. In this case, "path" should be set,
            otherwise the index page url is used.
        '''

        # to avoid loops, 'path' has to be set when reverse is True!
        # otherwise 'path' points to the index page
        if reverse and not path:
            path = ""

        # convert the path to inlcude our base path
        if path:
            # cut trailing slash to work with os.path.join
            path = path[1:] if path.startswith('/') else path
            path = os.path.join(vispa.url.dynamic('/'), path)

        # store if there should be a redirect at the end of this function
        redirect = False

        if 'user_id' not in cherrypy.session.keys():
            redirect = True
        else:
            uid = cherrypy.session['user_id'].decode('utf-8')
            user = User.get_by_id(cherrypy.request.db, uid)
            if not user:
                redirect = True
            else:
                # store the user object inside the request
                cherrypy.request.user = user
                # update the time of the last request
                User.update_last_request(cherrypy.request.db, uid)

        # redirect? depends on 'reverse'
        if (redirect and not reverse) or (not redirect and reverse):
            # store the requested path (w/o base) in the session
            # when reverse is False
            if not reverse:
                if not 'requested_path' in cherrypy.session.keys():
                    cherrypy.session['requested_path'] = cherrypy.request.path_info
                if not 'query_string' in cherrypy.session.keys():
                    cherrypy.session['query_string'] = cherrypy.request.query_string
            logger.debug("Redirect: %s or %s" % (path, self.redir_path_nonuser))
            raise cherrypy.HTTPRedirect(path or self.redir_path_nonuser)

    def _cleanup(self):
        cherrypy.request.user = None
