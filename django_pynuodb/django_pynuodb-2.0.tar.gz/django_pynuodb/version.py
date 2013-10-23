"""
Extracts the version of the NuoDB database
"""

import re

def get_version(connection):
    if hasattr(connection, 'server_version'):
        return connection.server_version
    else:
        cursor = connection.cursor()
        cursor.execute("SELECT geteffectiveplatformversion() FROM dual")
        ver = cursor.fetchone()[0]
        return ver
