################################################################
# pp.core - Produce & Publish
# (C) 2013, ZOPYX Limited, www.zopyx.com
################################################################

import mechanize
from dropbox import session
from dropboxfs import DropboxFS
import fs.wrapfs

DROPBOX_ACCESS_TYPE = 'dropbox'

class DropboxFSWrapper(fs.wrapfs.WrapFS):
    """ A wrapper for a DropboxFS in order to sandbox
        all Filesystem operations below a certain
        subpath since the DropboxFS core implementation
        does not support FS sandboxing.
    """

    def __init__(self, fs, prefix='wrapper'):
        super(DropboxFSWrapper, self).__init__(fs)
        self.prefix = prefix
    
    def _encode(self, path):
        return self.prefix + '/' + path

    def _decode(self, path):
        if path.startswith('/'):
            return path.replace('/' + self.prefix + '/', '')
        else:
            return path.replace(self.prefix + '/', '')

def dropboxfs_factory(app_key, app_secret, username, password):

    sess = session.DropboxSession(app_key,
                                  app_secret,
                                  DROPBOX_ACCESS_TYPE)
    request_token = sess.obtain_request_token()
    url = sess.build_authorize_url(request_token)

    # Emulate automatic login
    br = mechanize.Browser()
    page = br.open(url)
    br.select_form(nr=0)
    br.form['login_email'] = username
    br.form['login_password'] = password
    br.submit()
    response = br.response().read()

    br.select_form(nr=0)
    br.submit()
    response = br.response().read()

    # successful login
    access_token = sess.obtain_access_token(request_token)

    fs = DropboxFS(app_key,
                   app_secret,
                   DROPBOX_ACCESS_TYPE, 
                   access_token.key, 
                   access_token.secret)
    return DropboxFSWrapper(fs)
