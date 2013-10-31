# -*- coding: utf-8 -*-
'''
Qiniu Resource Storage SDK for Python
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For detailed document, please see:
<https://github.com/qiniu/python-sdk/blob/develop/docs/README.md>
'''

import conf
conf.initcfgs(['./qiniu.conf', '~/.qbox/qiniu.conf', '/etc/qbox/qiniu.conf'])

from auth import qetag, qetags

from api import *

__version__ = conf.VERSION
__all__ = ['qetag', 'qetags', 'gen_url', 'Url', 'Bucket']
