# -*- coding: utf-8 -*-

import cherrypy

from vispa import AbstractExtension
from vispa.controller import AbstractController
import vispa.rpc

class CodeEditorController(AbstractController):

    @cherrypy.expose
    def getcontent(self, path):
        try:
            fs = self.get("fs")
            content = fs.get_file_content(str(path))
            mtime = fs.get_mtime(str(path))
            return self.success(content=content, mtime=int(mtime), encode_json=True)
        except Exception, e:
            return self.fail(msg="Couldn\"t load the file content: %s" % str(e), encode_json=True)

    @cherrypy.expose
    def savecontent(self, path, content):
        try:
            fs = self.get("fs")
            success = fs.save_file_content(str(path), content)
            if not success:
                raise Exception("file already exists")
            mtime = fs.get_mtime(path)
            return self.success(mtime=mtime, encode_json=True)
        except Exception, e:
            return self.fail(msg="Couldn\"t save the file content: %s" % str(e), encode_json=True)

    @cherrypy.expose
    def checkmtime(self, path, mtime):
        try:
            fs = self.get("fs")
            new_mtime = fs.get_mtime(path)
            return self.success(check=int(mtime) == new_mtime, encode_json=True)
        except Exception, e:
            return self.fail(msg="Couldn\"t check the mtime: %s" % str(e), encode_json=True)

class CodeEditorExtension(AbstractExtension):

    def get_name(self):
        return 'codeeditor'

    def dependencies(self):
        return []

    def setup(self, extensionList): 
        self.controller(CodeEditorController())
        self.js('js/extension.js')
        self.js('js/editor.js')
        self.css('css/styles.css')
        self.remote()
