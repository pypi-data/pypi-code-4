# -*- coding: utf-8 -*-

# imports
import cherrypy
from subprocess import call
from string import Template
from vispa.controller import AbstractController
from vispa.controller.filesystem import FSAjaxController
from vispa.models.user import User
from vispa.models.workspace import Workspace, WorkspaceState
from vispa.models.profile import Profile
from vispa.models.preference import VispaPreference, ExtensionPreference
from vispa.helpers import browser
import vispa
import logging
import json
import os

logger = logging.getLogger(__name__) 

class AjaxController(AbstractController):

    def __init__(self):
        AbstractController.__init__(self)
        self.fs = FSAjaxController()

    @cherrypy.expose
    @cherrypy.tools.user(on=False)
    @cherrypy.tools.workspace(on=False)
    def gettemplate(self, path, **kwargs):
        try:
            makotemplate = cherrypy.engine.publish('lookup_template', os.path.join('html', 'sites', path)).pop()
            return makotemplate.render(**kwargs)
        except Exception, e:
            return self.fail(msg=str(e), encode_json=True)

    @cherrypy.expose
    @cherrypy.tools.user(on=False)
    @cherrypy.tools.workspace(on=False)
    def login(self, username, password):
        db = cherrypy.request.db
        user = User.login(db, username, password)
        if isinstance(user, User):
            cherrypy.session['user_id'] = unicode(user.id)
            cherrypy.session['user_name'] = username
            return self.success(encode_json=True)
        else:
            return self.fail(msg=user, encode_json=True)

    @cherrypy.expose
    @cherrypy.tools.user(on=False)
    @cherrypy.tools.workspace(on=False)
    def register(self, username, email, password):
        db = cherrypy.request.db
        user = User.register(db, username, email, password)
        if isinstance(user, User):
            if User.is_active(cherrypy.request.db, user.id):
                cherrypy.session['user_id'] = unicode(user.id)
            if 'user.registration.hook' in cherrypy.config:
                cmd = []
                for arg in cherrypy.config['user.registration.hook']:
                    cmd.append(Template(arg).substitute(username=user.name, userid=user.id))
                call(cmd)
            return self.success(encode_json=True)
        else:
            return self.fail(msg=user, encode_json=True)

    @cherrypy.expose
    @cherrypy.tools.user(on=False)
    @cherrypy.tools.workspace(on=False)
    @cherrypy.tools.json_out()
    def forgot(self, username):
        User.forgot_password(cherrypy.request.db, username)
        return {'msg': 'Further instructions have been sent to your mail address!'}

    @cherrypy.expose
    @cherrypy.tools.user(on=False)
    @cherrypy.tools.workspace(on=False)
    @cherrypy.tools.json_out()
    def resetpassword(self, userhash, password, *args, **kwargs):
        user = User.get_by_hash(cherrypy.request.db, userhash)
        if not user:
            return self.fail()
        user.hash = None
        user.password = password
        if User.is_active(cherrypy.request.db, user.id):
            cherrypy.session['user_id'] = unicode(user.id)
            cherrypy.session['user_name'] = user.name
        return self.success()

    @cherrypy.expose
    @cherrypy.tools.workspace(on=False)
    @cherrypy.tools.profile()
    def setvispapreference(self, section, value=u'{}'):
        try:
            profile_id = self.get('profile_id')
            db = cherrypy.request.db
            # "use" the profile
            Profile.use(db, profile_id, agent=browser.client_agent())
            # change the preference section
            success = VispaPreference.set_value(db, profile_id, section, value)
            if not success:
                raise Exception('Could\'nt update preference section \'%s\'!' % section)
            return self.success(encode_json=True)
        except Exception, e:
            return self.fail(msg=str(e), encode_json=True)

    @cherrypy.expose
    @cherrypy.tools.workspace(on=False)
    @cherrypy.tools.profile()
    def setextensionpreference(self, key, value=u'{}'):
        try:
            profile_id = self.get('profile_id')
            db = cherrypy.request.db
            # "use" the profile
            Profile.use(db, profile_id, agent=browser.client_agent())
            # change the preference section
            success = ExtensionPreference.set_value(db, profile_id, key, value)
            if not success:
                raise Exception('Could\'nt update preference \'%s\'!' % key)
            return self.success(encode_json=True)
        except Exception, e:
            return self.fail(msg=str(e), encode_json=True)

    @cherrypy.expose
    @cherrypy.tools.user()
    @cherrypy.tools.workspace(on=False)
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.json_in()
    def addworkspace(self):
        try:
            if not vispa.config('rpc', 'allow_new_workspaces', True):
                raise Exception('No permission to add a new Workspace!')
            json = cherrypy.request.json
            db = self.get('db')
            user_id = self.get('user_id')
            name = json.get(u'name', '')
            if u'name' in json.keys():
                del json[u'name']

            # does the user already have a workspace with that name?
            workspaces = Workspace.get_user_workspaces(db, user_id)
            for workspace in workspaces:
                # case insensitive
                if name.lower() == workspace.name.lower():
                    logger.info('Workspace name \'%s\' already in use!' % workspace.name)
                    raise Exception('Workspace name \'%s\' already in use!' % workspace.name)

            # try to add the workspace
            workspace = Workspace.add(db, user_id, name, **json)
            if not isinstance(workspace, Workspace):
                logger.info('Workspace could not be added')
                raise Exception('Workspace could not be added!')
            logger.info('Added workspace')
            # get the data of the workspace and send them back
            data = self._platform.controller.workspace_data(workspace_id=workspace.id)
            return self.success(data=data, encode_json=True)
        except Exception, e:
            logger.warn(vispa.exception_string())
            return self.fail(msg=str(e), encode_json=True)

    @cherrypy.expose
    @cherrypy.tools.user()
    @cherrypy.tools.workspace(on=False)
    @cherrypy.tools.allow(methods=['POST'])
    def deleteworkspace(self, wid):
        try:
            db = cherrypy.request.db
            # is workspace owned by the user?
            workspace = Workspace.get_by_id(db, wid)
            if not isinstance(workspace, Workspace):
                raise Exception('Unknown Workspace!')
            if not workspace.user_id or workspace.user_id != self.get('user_id'):
                raise Exception('No permission to delete this Workspace!')
            # remove it
            success = Workspace.remove(db, wid)
            if not success:
                raise Exception('Couldn\'t remove this Workspace!')
            was_selected = False
            workspace_ids = self.get('workspace_ids')
            if workspace_ids and wid in workspace_ids:
                workspace_ids.remove(wid)
                was_selected = True
            return self.success({'was_selected': was_selected}, encode_json=True)
        except Exception, e:
            return self.fail(msg=str(e), encode_json=True)

    @cherrypy.expose
    @cherrypy.tools.user()
    @cherrypy.tools.workspace(on=False)
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.json_in()
    def setworkspacedata(self):
        try:
            json = cherrypy.request.json
            user_id = self.get('user_id')
            workspace_id = json[u'id']
            del json[u'id']
            # is workspace owned by the user?
            workspace = Workspace.get_by_id(cherrypy.request.db, workspace_id)
            if not isinstance(workspace, Workspace):
                raise Exception('Unknown workspace!')
            if not workspace.user_id or workspace.user_id != user_id:
                raise Exception('No permission!')
            # empty string means None
            for key in json:
                json[key] = json[key] or None
            success = Workspace.update(cherrypy.request.db, workspace_id, **json)
            if not success:
                raise Exception('Couldn\'t update the workspace data!')
            return self.success(encode_json=True)
        except Exception, e:
            return self.fail(msg=str(e), encode_json=True)

    @cherrypy.expose
    @cherrypy.tools.user()
    @cherrypy.tools.workspace(on=False)
    @cherrypy.tools.allow(methods=['POST'])
    def connectworkspace(self, wid, state=True, preload=True):
        try:
            db = cherrypy.request.db
            uid = self.get('user_id')
            # is workspace owned by the user?
            workspace = Workspace.get_by_id(db, wid)
            if not isinstance(workspace, Workspace):
                raise Exception('Unknown Workspace!')
            if workspace.user_id and workspace.user_id != uid:
                raise Exception('No permission to select this Workspace!')
            # update the session
            wids = cherrypy.session.get('workspace_ids', None)
            if not wids:
                wids = cherrypy.session['workspace_ids'] = []
            if wid in wids:
                wids.remove(wid)
            wids.insert(0, wid)
            # get state data
            state_data = None
            if self.convert(state, bool):
                state_data = WorkspaceState.get_state(db, wid, uid)
            # pre-load the fs which is a connection test at the same time
            if self.convert(preload, bool):
                self.get('fs', wid)
            return self.success(data=state_data, encode_json=True)
        except Exception, e:
            return self.fail(msg=str(e), encode_json=True)

    @cherrypy.expose
    @cherrypy.tools.user()
    @cherrypy.tools.allow(methods=['POST'])
    def updateworkspacestate(self, wid, state):
        try:
            db = cherrypy.request.db
            uid = self.get('user_id')
            success = WorkspaceState.update_state(db, wid, uid, json.loads(state))
            if not success:
                raise Exception('Unknown Workspace!')
            return self.success(encode_json=True)
        except Exception, e:
            return self.fail(msg=str(e), encode_json=True)

    @cherrypy.expose
    def localuser(self):
        local = cherrypy.request.local
        remote = cherrypy.request.remote
        socket_uid = vispa.Netstat.get_socket_owner(local.ip or local.name, local.port,
                               remote.ip or remote.name, remote.port)
        logger.info("Socket uid: %s" % socket_uid)
        server_uid = os.getuid()
        logger.info("Server uid: %s" % server_uid)
