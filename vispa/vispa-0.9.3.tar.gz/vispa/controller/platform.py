# -*- coding: utf-8 -*-

# imports
import vispa
from vispa.controller import AbstractController
from vispa.controller.ajax import AjaxController
from vispa.controller.filesystem import FSController
from vispa.controller.bus import BusController
from vispa.models.user import User
from vispa.models.workspace import Workspace
from vispa.models.profile import Profile
import cherrypy
import logging
import os

logger = logging.getLogger(__name__)


class PlatformController(AbstractController):

    def __init__(self):
        '''
        The Constructor. Members from other classes
        are added as pages for cherrypy URL mapping.
        '''
        AbstractController.__init__(self)
        self.ajax = AjaxController()
        self.fs = FSController()
        # self.error = ErrorController()
        self.extensions = AbstractController()
        self.bus = BusController()
        self.common_js = []
        self.common_css = []

    def add_common_js(self, filepath):
        self.common_js.append(filepath)

    def add_common_css(self, filepath):
        self.common_css.append(filepath)

    def mount_extension_controller(self, mountpoint, controller):
        if hasattr(self.extensions, mountpoint):
            logger.warning('Controller mountpoint already exists: %s' % mountpoint)
        else:
            logger.info('Mounting controller "%s"' % os.path.join(os.sep, mountpoint))
            setattr(self.extensions, mountpoint, controller)

    def requested_path(self, delete=True):
        path = ''
        if 'requested_path' in cherrypy.session.keys():
            path += cherrypy.session['requested_path']
            if delete:
                del cherrypy.session['requested_path']
        if 'query_string' in cherrypy.session.keys():
            if cherrypy.session['query_string']:
                path += '?' + cherrypy.session['query_string']
                if delete:
                    del cherrypy.session['query_string']
        return path

    def workspace_data(self, workspace_id=None, keys=None):
        keys = keys or ['id', 'user_id', 'name', 'host', 'login', 'key', 'basedir', 'command', 'created']
        user_id = self.get('user_id')
        workspace_data = {}
        workspaces = Workspace.get_user_workspaces(cherrypy.request.db, user_id)
        for workspace in workspaces:
            data = workspace.make_dict(keys=keys)
            if workspace_id == workspace.id:
                return data
            workspace_data[str(workspace.id)] = data
        return workspace_data

    @cherrypy.expose
    @cherrypy.tools.profile()
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.stats(page='index')
    @cherrypy.tools.render(template='sites/index.html')
    def index(self, *args, **kwargs):
        db = cherrypy.request.db
        username = cherrypy.request.user.name
        devmode = vispa.config('web', 'devmode', True)
        use_websockets = vispa.config('websockets', 'enabled', False)
        secure_websockets = vispa.config('websockets', 'secure', False)
        profile_id = self.get('profile_id')
        preferences = Profile.get_preferences(db, profile_id, parse_json=True)
        client_logging_enabled = vispa.config('web', 'client_logging_enabled', True)
        client_logging_level = vispa.config('web', 'client_logging_level', 'info')
        client_logging_ignore = vispa.config('web', 'client_logging_ignore', [])
        workspace_ids = self.get('workspace_ids')
        workspace_data = self.workspace_data()
        add_workspaces = vispa.config('rpc', 'allow_new_workspaces', True)
        data = {'devmode'          : devmode,
                'username'         : username,
                'common_js'        : self.common_js,
                'common_css'       : self.common_css,
                'use_websockets'   : use_websockets,
                'secure_websockets': secure_websockets,
                'workspace_ids'    : self.convert(workspace_ids, int),
                'workspace_data'   : workspace_data,
                'add_workspaces'   : add_workspaces,
                'profile_id'       : profile_id,
                'logging_enabled'  : client_logging_enabled,
                'logging_level'    : client_logging_level,
                'logging_ignore'   : client_logging_ignore}
        data.update(preferences)
        return data

    @cherrypy.expose
    @cherrypy.tools.workspace(on=False)
    @cherrypy.tools.profile()
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.stats(page='bootstrap')
    @cherrypy.tools.render(template='sites/bootstrap.html')
    def bootstrap(self, *args, **kwargs):
        return {}

    @cherrypy.expose
    @cherrypy.tools.workspace(on=False)
    @cherrypy.tools.user(reverse=True, path='/')
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.stats(page='login')
    @cherrypy.tools.render(template='sites/login.html')
    def login(self, *args, **kwargs):
        path = self.requested_path()
        welcome_text = vispa.config('web', 'welcome_text', '')
        login_text = vispa.config('web', 'login_text', '')
        registration_text = vispa.config('web', 'registration_text', '')
        forgot_text = vispa.config('web', 'forgot_text', '')
        use_forgot = vispa.config('web', 'use_forgot', False)
        return {'requested_path'   : path,
                'welcome_text'     : welcome_text,
                'login_text'       : login_text,
                'registration_text': registration_text,
                'forgot_text'      : forgot_text,
                'use_forgot'       : use_forgot}

    @cherrypy.expose
    @cherrypy.tools.user()
    @cherrypy.tools.workspace(on=False)
    def logout(self):
        vispa.fire_callback("user.logout", cherrypy.request.user)
        cherrypy.lib.sessions.expire()
        raise cherrypy.HTTPRedirect(vispa.url.dynamic('/'))

    @cherrypy.expose
    @cherrypy.tools.user(reverse=True)
    @cherrypy.tools.render(template='activate.html')
    def activate(self, hash, *args, **kwargs):
        user = User.activate(cherrypy.request.db, hash)
        if not isinstance(user, User):
            return self.success()
        else:
            return self.fail()

    @cherrypy.expose
    @cherrypy.tools.user(reverse=True)
    @cherrypy.tools.render(template='forgot.html')
    def forgot(self, hash, *args, **kwargs):
        user = User.get_by_hash(cherrypy.request.db, hash)
        if isinstance(user, User):
            return self.success({'hash': hash})
        else:
            return self.fail()

    @cherrypy.expose
    @cherrypy.tools.workspace(on=False)
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.stats(page='workspace')
    @cherrypy.tools.render(template='sites/workspace.html')
    def workspace(self, *args, **kwargs):
        path = self.requested_path()
        show_add_form = vispa.config('rpc', 'allow_new_workspaces', True)
        workspace_data = self.workspace_data()
        return {'requested_path': path,
                'show_add_form' : show_add_form,
                'workspace_data': workspace_data}

    @cherrypy.expose
    @cherrypy.tools.user()
    @cherrypy.tools.allow(methods=['GET'])
    def resetworkspace(self, *args, **kwargs):
        if 'workspace_id' in cherrypy.session.keys():
            del cherrypy.session['workspace_id']
        raise cherrypy.HTTPRedirect(vispa.url.dynamic('/'))
