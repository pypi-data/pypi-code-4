### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2012 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
import zope.app.wsgi

# import local packages
try:
    import psyco
    psyco.profile()
except:
    pass


def application_factory(global_conf):
    zope_conf = global_conf['zope_conf']
    app = zope.app.wsgi.getWSGIApplication(zope_conf)

    def wrapper(environ, start_response):
        vhost = ''
        vhost_skin = environ.get('HTTP_X_VHM_SKIN')
        if vhost_skin and \
           (not environ.get('CONTENT_TYPE', '').startswith('application/json')) and \
           (not environ.get('PATH_INFO', '').startswith('/++skin++')):
            vhost = '/++skin++' + vhost_skin
        url_scheme = environ.get('wsgi.url_scheme', 'http')
        vhost_root = environ.get('HTTP_X_VHM_ROOT', '')
        if (url_scheme == 'https') or (vhost_root and (vhost_root != '/')):
            # Standard virtual host URL rewriting
            # Also required for HTTPS connexions
            vhost += '%s/++vh++%s:%s:%s/++' % (vhost_root,
                                               url_scheme,
                                               environ.get('SERVER_NAME', ''),
                                               environ.get('SERVER_PORT', '80'))
        environ['PATH_INFO'] = vhost + environ['PATH_INFO']
        return app(environ, start_response)

    return wrapper
