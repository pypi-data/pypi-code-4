""" Echo StreamServer API

This is a Python version of the Echo StreamServer API.
http://aboutecho.com/developers/index.html

    feeds - Feeds API
    items - Items API
    kvs   - Key-Value Store API
    users - User API

Most API methods raise the echo.StreamServerError exception.
This indicates a server-side error, or malformed request.
"""

__version__ = "0.83"
__author__ = "Andrew Droffner"

# Import Public APIs: modules and packages
# ======================================================================
import feeds, items, kvs, users
from echo.core_api import Account, StreamServerError

# Import EQL Query Builder:
# ======================================================================
import eql

