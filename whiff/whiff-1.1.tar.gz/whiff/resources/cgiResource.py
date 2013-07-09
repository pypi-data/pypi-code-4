"""
Store and provide CGI parameters from the request.

This provides only get access

  [] --> list of all parameter names
  [None] --> dictionary of all parameter names to lists of values.
      The first value for "name" is at R["name"][0]
  ["name"] --> list of DICTIONARIES corresponding to the field storage for "name".
      find the first value for the field at R[0]["value"]
"""

import types
from cgi import FieldStorage
from whiff import gateway
import StringIO

class CgiFinder:
    def __init__(self, fs=None):
        self.fs = fs
    def localize(self, env):
        fp = env.get("wsgi.input")
        if fp is None:
            fp = StringIO.StringIO()
        fs = FieldStorage(fp, environ=env)
        return CgiFinder(fs)
    def get(self, pathlist):
        if not pathlist:
            # return the names list
            return self.fs.keys()
        assert len(pathlist)==1, "get requires only the cgi parameter name"
        name = pathlist[0]
        if name is None:
            # return dict of names-->values
            result = {}
            for field in self.fs.keys():
                result[field] = self.fs.getlist(field)
            return result
        elif name in self.fs:
            # return list detail info dictionary for name
            stuff = self.fs[name]
            if type(stuff) is not types.ListType: # arggh!
                stuff = [stuff]
            result = [ {
                "name": name,
                "value": s.value, # xxx if this is a big file, it will read all of it.
                "filename": s.filename,
                "list": s.list,
                "type": s.type,
                "file": s.file,
                "type_options": s.type_options,
                "disposition": s.disposition,
                "headers": s.headers,
                } for s in stuff ]
            return result
        else:
            return [] # no parameters matching name
