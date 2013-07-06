#####################################################################
# zopyx.authoring
# (C) 2011, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################


from zope.interface import Interface, implements

class IBeforePublishing(Interface):
    pass

class IAfterPublishing(Interface):
    pass

class IAfterOfficeImport(Interface):
    pass

class BeforePublishing(object):
    implements(IBeforePublishing)

    def __init__(self, conversion):
        self.conversion = conversion

class AfterPublishing(object):
    implements(IAfterPublishing)

    def __init__(self, conversion):
        self.conversion = conversion

class AfterOfficeImport(object):
    implements(IAfterOfficeImport)

    def __init__(self, import_folder):
        self.import_folder = import_folder

