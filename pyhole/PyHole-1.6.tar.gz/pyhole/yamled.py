from pyhole import PyHole
import yaml

class PyHoleYamled(PyHole):
    '''PyHole support for yaml that process every response with yaml.load function'''
    def get_response_wrapper(self):
        return yaml.load
