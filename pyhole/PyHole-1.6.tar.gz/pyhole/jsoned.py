from pyhole import PyHole
import json

class PyHoleJsoned(PyHole):
    '''PyHole support for yaml that process every response with yaml.load function'''
    def get_response_wrapper(self):
        return json.loads
