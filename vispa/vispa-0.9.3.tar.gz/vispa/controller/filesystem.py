# -*- coding: utf-8 -*-

# imports
import vispa
import cherrypy
import os
import json
from vispa.controller import AbstractController
import xmlrpclib


class FSController(AbstractController):

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def getfile(self, path, download=None, rnd=None):
        try:
            if not download or str(download).lower() not in ['true', '1', 'yes']:
                download = False
            else:
                download = True
            data, contenttype, isbrowserfile = self.handleDownload(str(path))
            cherrypy.response.headers['Content-Type'] = contenttype
            if download or not isbrowserfile:
                cherrypy.response.headers[
                    'Content-Disposition'] = 'attachment; filename=%s' % path.split('/')[-1]
            return data
        except Exception, e:
            cherrypy.session['error_data'] = {'status': 404,
                                              'message': str(e), 'traceback': '', 'version': ''}
            raise cherrypy.HTTPRedirect(
                vispa.url.dynamic(os.path.join('error/filenotfound')))

    def handleDownload(self, path):
        self.get('fs')
        if not fs.exists(path, 'file'):
            raise Exception('The file \'%s\' does not exist' % path)

        content = fs.get_file_content(path)
        data = xmlrpclib.Binary(
            content).data  # TODO: remove xmlrpclib dependency

        # get the content type depending on the file extension
        ext = path.split('.')[-1]
        mimetype = fs.get_mime_type(path)
        if mimetype is None:
            raise Exception(
                'The file extension \'%s\' is not supported by this server' % ext)

        return data, mimetype, fs.is_browser_file(path)


class FSAjaxController(AbstractController):

    @cherrypy.expose
    def exists(self, path, type=None):
        try:
            fs = self.get('fs')
            path = str(path)
            type = str(type) if type else type
            target_type = fs.exists(path, type=type)
            if target_type:
                return self.success(type=target_type, encode_json=True)
            else:
                return self.fail(encode_json=True)
        except:
            return self.fail(encode_json=True)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST', 'GET'])
    def filelist(self, path, deep=False, filter=[], reverse=False):
        try:
            fs = self.get('fs')

            cherrypy.session.save()
            cherrypy.session.loaded = False

            deep = self.convert(deep, bool)
            reverse = self.convert(reverse, bool)

            # get the files with the filter
            files = fs.get_file_list(path, deep=deep, filter=filter, reverse=reverse, encode_json=True)

            return self.success(files, encode_json=True)
        except Exception, e:
            vispa.log_exception()
            return self.fail(msg='Couldn\'t load files: %s' % str(e), encode_json=True)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST', 'GET'])
    @cherrypy.tools.json_out()
    def createfolder(self, path, name):
        try:
            fs = self.get('fs')
            fs.create_folder(str(path), str(name))
            return self.success()
        except Exception, e:
            return self.fail(msg='Couldn\'t create the folder: %s' % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.json_out()
    def createfile(self, path, name):
        try:
            fs = self.get('fs')
            fs.create_file(str(path), str(name))
            return self.success()
        except Exception, e:
            return self.fail(msg='Couldn\'t create the file: %s' % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.json_out()
    def renamefolder(self, path, name):
        try:
            fs = self.get('fs')
            fs.rename_folder(str(path), str(name))
            return self.success()
        except Exception, e:
            return self.fail(msg='Couldn\'t rename the folder: %s' % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.json_out()
    def renamefile(self, path, name):
        try:
            fs = self.get('fs')
            fs.rename_file(str(path), str(name))
            return self.success()
        except Exception, e:
            return self.fail(msg='Couldn\'t rename the file: %s' % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.json_out()
    def remove(self, path):
        try:
            fs = self.get('fs')
            # 'path' can be a unicode/string or list of unicodes/strings
            # so convert it with the convert function
            fs.remove(path)
            return self.success()
        except Exception, e:
            return self.fail(msg='Couldn\'t remove the file(s): %s' % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST', 'GET'])
    @cherrypy.tools.json_out()
    def compress(self, path, paths, name):
        try:
            fs = self.get('fs')
            # 'paths' can be a unicode/string or list of unicodes/strings
            # so convert it with the convert function
            paths = json.loads(paths)
            fs.compress(path, paths, name)
            return self.success()
        except Exception, e:
            return self.fail(msg='Couldn\'t compress the file(s): %s' % str(e))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST', 'GET'])
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def paste(self, path, paths, cut):
        try:
            fs = self.get('fs')
            paths = json.loads(paths)
            # 'paths' can be a unicode/string or list of unicodes/strings
            # so convert it with the convert function
            fs.paste(path, paths, self.convert(cut, bool))
            return self.success()
        except Exception, e:
            action = 'cut' if self.convert(cut, bool) else 'copy'
            return self.fail(msg='Couldn\'t %s the file(s): %s' % (action, str(e)))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.json_out()
    def upload(self, *args, **kwargs):
        # the html5 uploader provides following kwargs:
        # index, type, name, size, uploadedfiles[]
        # Since "uploadedfiles[]" ends with "[]"-brackets
        # we have to use kwargs instead of args
        try:
            # extract the path
            path = str(kwargs['path'])

            # prepare the parts
            parts = kwargs['uploadedfiles[]']
            # force parrts to be a list
            if not isinstance(parts, list):
                parts = [parts]

            # upload
            self.handleUpload(path, parts)

            return self.success()
        except Exception, e:
            return self.fail(msg='Couldn\'t upload the file(s): %s' % str(e))

    def handleUpload(self, path, parts):
        fs = self.get('fs')
        for part in parts:
            f = part.file
            name = str(part.filename)

            # check mime type, i.e. get the content type depending on the file
            # extension
            mimetype = fs.get_mime_type(name)
            if mimetype is None:
                ext = name.split('.')[-1]
                raise Exception(
                    'The file extension \'%s\' is not supported by this server' % ext)

            # save the content using the fs
            fs.save_file_content(os.path.join(path, name), xmlrpclib.Binary(f), force=True)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_out()
    def isbrowserfile(self, path):
        try:
            fs = self.get('fs')
            is_bf = fs.is_browser_file(str(path))
            if is_bf:
                return self.success()
            else:
                return self.fail()
        except Exception, e:
            return self.fail()

    @cherrypy.expose
    def getsuggestions(self, path, length=10, append_hidden=True):
        try:
            fs = self.get('fs')
            length = length or 1
            suggestions = fs.get_suggestions(path, length=int(
                length), append_hidden=self.convert(append_hidden, bool), encode_json=True)
            return self.success(suggestions=suggestions, encode_json=True)
        except Exception, e:
            return self.fail(msg=str(e), encode_json=True)
