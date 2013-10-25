import urlparse

class UriBuilder(object):

    def __init__(self, providerRootUrl):
        self.root = providerRootUrl

    def forDoi(self, doi):
        doiBase = urlparse.urljoin(self.root, 'doi/')
        return urlparse.urljoin(doiBase, doi)

    def forUser(self, uid):
        userBase = urlparse.urljoin(self.root, 'users/')
        return urlparse.urljoin(userBase, uid)
