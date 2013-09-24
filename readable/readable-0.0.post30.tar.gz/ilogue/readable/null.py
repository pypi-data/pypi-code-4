from mock import Mock


class Null(object):

    def __init__(self, classname):
        self.classname = classname
        print('NullObject created for class: '+self.classname)

    def __getattr__(self, name):
        print('Attribute lookup on NullObject: '+self.classname+'.'+name)
        return Mock()
