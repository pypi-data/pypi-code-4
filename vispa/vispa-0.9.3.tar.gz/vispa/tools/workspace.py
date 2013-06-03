# -*- coding: utf-8 -*-

# imports
import cherrypy
import vispa
from vispa.models.workspace import Workspace
import logging

logger = logging.getLogger(__name__)

class WorkspaceTool(cherrypy.Tool):

    def __init__(self, redir_url):
        cherrypy.Tool.__init__(self, "before_handler", self._fetch, priority=70)
        self.redir_path_noworkspace = redir_url

    def _setup(self):
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach("before_finalize", self._cleanup, priority=30)

    def _fetch(self, path=None):
        request = cherrypy.request
        db = cherrypy.request.db
        session = cherrypy.session

        # is at least one workspace connected?
        wids = session.get("workspace_ids", [])
        wid = request.private_params.get("_wid", None)

        if not isinstance(wids, (list, tuple)) or not len(wids):
            wid = wid or vispa.config("rpc", "default_workspace_id", None)
            if wid:
                session["workspace_ids"] = [wid]
                logger.debug('Workspace: %s' % wid)
            else:
                # no workspace found => redirect
                logger.debug('No Workspace found!')
                raise cherrypy.HTTPRedirect(path or self.redir_path_noworkspace)

        if wid:
            workspace = Workspace.get_by_id(db, wid)
            if isinstance(workspace, Workspace):
                request.workspace = workspace

    def _cleanup(self):
        pass
