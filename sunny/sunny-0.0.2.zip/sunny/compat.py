"""
The purpose of this module is to try to keep compatibility between
Python versions.
"""

import sys

if sys.version_info >= (3, ):
    from urllib.parse import urljoin
elif sys.version_info >= (2, ):
    from urlparse import urljoin
