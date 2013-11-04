from suds.client import Client as SudsClient

def delete_empties(dict_del):
    for k in dict_del.keys():
        if not dict_del[k]:
            del dict_del[k]

class Client(object):

    cascade            = None
    cascade_endpoint   = None
    cascade_auth       = None

    def __init__(self, cascade_endpoint, user_id, user_pwd):

        self.cascade_endpoint  = cascade_endpoint
        self.cascade           = SudsClient(cascade_endpoint)
        self.cascade_auth      = self.cascade.factory.create('authentication')

        self.cascade_auth.username = user_id
        self.cascade_auth.password = user_pwd

    def read(self, id, path, sitename, siteid, type):
        ident               = self.cascade.factory.create('identifier')
        ident.type          = type
        ident.id            = id
        ident.path.path     = path
        ident.path.siteId   = siteid
        ident.path.siteName = sitename

        result = self.cascade.service.read(self.cascade_auth, ident)

        return result.asset[type]

    def readFile(self, id, path, sitename, siteid):
        return self.read(id=id, path=path, sitename=sitename, siteid=siteid, type="file")


    def create(self, asset):
        result = self.cascade.service.create(self.cascade_auth, asset)
        return result

    def createFile(self, text, name, site, path):
        file = self.cascade.factory.create("file")
        file.parentFolderPath = path
        file.siteName = site
        file.name = name
        file.text = text

        createme = self.cascade.factory.create("asset")
        createme["file"] = file

        return self.create(asset=createme)

    def delete(self, id, path, sitename, siteid, type):
        ident               = self.cascade.factory.create('identifier')
        ident.type          = type
        ident.id            = id
        ident.path.path     = path
        ident.path.siteId   = siteid
        ident.path.siteName = sitename

        result = self.cascade.service.delete(self.cascade_auth, ident)

        return result

    def deleteFile(self, id, path, sitename, siteid):
        return self.delete(id=id, path=path, sitename=sitename, siteid=siteid, type="file")


    def edit(self, asset):
        result = self.cascade.service.edit(self.cascade_auth, asset)
        return result

    def editFile(self, text, name, site, path):
        file = self.cascade.factory.create("file")
        file.parentFolderPath = path
        file.path = path + name
        file.siteName = site
        file.name = name
        file.text = text

        editme = self.cascade.factory.create("asset")
        editme["file"] = file

        return self.edit(asset=editme)


    def publish(self, id, path, sitename, siteid, type):
        ident               = self.cascade.factory.create('identifier')
        ident.type          = type
        ident.id            = id
        ident.path.path     = path
        ident.path.siteId   = siteid
        ident.path.siteName = sitename

        result = self.cascade.service.publish(self.cascade_auth, ident)

        return result.asset[type]

    def publishFile(self, id, path, sitename, siteid):
        return self.publish(id=id, path=path, sitename=sitename, siteid=siteid, type="file")

