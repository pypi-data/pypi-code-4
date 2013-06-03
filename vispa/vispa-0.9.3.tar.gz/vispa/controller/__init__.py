# -*- coding: utf-8 -*-

# imports
import vispa
from vispa.models.workspace import Workspace
import cherrypy
import uuid
import json
import os
import inspect
 
class StaticController(object):

    def __init__(self, path):
        self._cp_config = {
           'tools.staticdir.on': True,
           'tools.staticdir.dir': path,
           'tools.db.on': False,
           'tools.user.on': False,
           'tools.workspace.on': False,
           'tools.etags.on': True,
           'tools.sessions.on': False,
           'tools.expires.on': True,
           'tools.expires.force': True,
           'tools.expires.secs': 3600*24*365
        }


class AbstractController(object):

    def __init__(self, mount_static = True):
        self._object_cache = {}
        if mount_static:
            self.mount_static()

    def mount_static(self, path = None, url = 'static'):
        if path and not os.path.isabs(path):
            os.path.join(os.path.dirname(inspect.getabsfile(self.__class__)), path)
        elif not path:
            path = os.path.join(os.path.dirname(inspect.getabsfile(self.__class__)), 'static')
            
        setattr(self, url, StaticController(path))


    def success(self, data=None, encode_json=None, set_header=True, **kwargs):
        # data is the default key, when using this method with 1 argument
        # like "success(<somedata>, encode_json=...)"
        if data is not None:
            kwargs["data"] = data

        # no encoding when encode_json is None
        if encode_json is None:
            result = {"success": True}
            result.update(kwargs)
            return result
        # explicitly not json encoded, return a dict
        elif not encode_json:
            result = {"success": True}
            for key, value in kwargs.items():
                # 'value' may be a json encoded string, e.g. '{"foo": "bar"}', try to load it
                try:
                    result[key] = json.loads(value)
                except Exception, e:
                    result[key] = value
            return result
        # explicitly json encoded, return a string
        else:
            data = ['"success": true']
            for key, value in kwargs.items():
                if isinstance(value, (str, unicode)) and value[0]+value[-1] in ["{}", "[]"]:
                    data.append('"%s": %s' % (key, value))
                else:
                    data.append(json.dumps({key: value})[1:-1])
            if set_header:
                cherrypy.response.headers["Content-Type"] = "application/json"
            return '{%s}' % ", ".join(data)

    def fail(self, msg=None, encode_json=False, set_header=True):
        if encode_json and set_header:
            cherrypy.response.headers['Content-Type'] = 'application/json'
        result = {'success': False}
        if msg:
            result.update({'msg': msg})
        return result if not encode_json else json.dumps(result)

    # a little helper
    def get(self, key, *args):
        key = key.lower()
        try:
            if key == 'session_id':
                return cherrypy.session.id
            elif key == 'user_id':
                return cherrypy.request.user.id
            elif key == 'user_name':
                return cherrypy.request.user.name
            elif key == 'db':
                return cherrypy.request.db
            elif key == 'workspace_ids':
                return cherrypy.session.get('workspace_ids', None)
            elif key == 'workspace':
                if len(args) == 0:
                    return cherrypy.request.workspace
                else:
                    return Workspace.get_by_id(cherrypy.request.db, int(args[0]))
            elif key == 'profile_id':
                return cherrypy.session.get('profile_id', None)
            elif key == 'profile':
                return cherrypy.request.profile
            elif key == 'fs':
                workspace = cherrypy.request.workspace if len(args) == 0 else args[0]
                return vispa.rpc.get(cherrypy.request.user, workspace, 'vispa.remote.filesystem.FileSystem')
        except:
            vispa.log_exception()
            return None
        return None

    # a little unicode helper
    def convert(self, value, flag):
        # convet lists, tuples and dicts by pseudo recursion
        if isinstance(value, list):
            return map(lambda elem: self.convert(elem, flag), value)
        elif isinstance(value, tuple):
            return tuple(map(lambda elem: self.convert(elem, flag), value))
        elif isinstance(value, dict):
            keys = map(lambda elem: str(elem), value.keys())
            values = map(lambda elem: self.convert(elem, flag), value.values())
            return dict(zip(keys, values))

        # string
        if flag == str:
            return str(value)
        # boolean
        if flag == bool:
            value = str(value).lower()
            if value == 'true':
                return True
            elif value == 'false':
                return False
            else:
                raise Exception("TypeError: boolean conversion expects 'true' or 'false'!")
        # integer
        if flag == int:
            try:
                return int(value)
            except:
                raise Exception('TypeError: conversion to integer received bad argument!')
        # float
        if flag == float:
            try:
                return float(value)
            except:
                raise Exception('TypeError: conversion to float received bad argument!')
        # error case
        raise Exception('TypeError: conversion with unknown type flag!')

    def cache(self, workspace_id, key):
        _key = (cherrypy.request.user.id, workspace_id, key)
        if _key in self._object_cache:
            return self._object_cache[_key]
        else:
            return None

    def set_cache(self, workspace_id, item, key=str(uuid.uuid4())):
        _key = (cherrypy.request.user.id, workspace_id, key)
        self._object_cache[_key] = item
        return key
