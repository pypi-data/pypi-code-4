"""
Utilities for Dox
"""
import unicodedata
import re

def slugify(value):
    """
    Makes slug-friendly string.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)