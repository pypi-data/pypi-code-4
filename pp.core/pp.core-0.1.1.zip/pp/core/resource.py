################################################################
# pp.core - Produce & Publish
# (C) 2013, ZOPYX Limited, www.zopyx.com
################################################################

class Resource(object):

    def __init__(self, fslayer):
        self.fslayer = fslayer

    def list_resources(self, suffix=None):
        names = self.fslayer.listdir()
        if suffix:
            names = [name for name in names if name.endswith(suffix)]
        return names

    def read(self, name):
        with self.fslayer.open(name, 'rb') as fp:
            content = fp.read()
        return content
