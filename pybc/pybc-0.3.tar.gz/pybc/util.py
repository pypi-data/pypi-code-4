"""
util.py: PyBC utility functions. 

Contains functions for converting among bytestrings (strings that are just
arrays of bytes), strings (strings that are actaul character data) and other
basic types.

"""

import base64
import binascii
import time

def bytes2string(bytestring):
    """
    Encode the given byte string as a text string. Returns the encoded string.
    
    """
    
    return base64.b64encode(bytestring)
    
def string2bytes(string):
    """
    Decode the given printable string into a byte string. Returns the decoded
    bytes.
    
    """
    
    return base64.b64decode(string)

def bytes2hex(bytestring):
    """
    Encode the given bytestring as hex.
    
    """
    
    return "".join("{:02x}".format(ord(char)) for char in bytestring)
    
def bytes2long(s):
    """
    Decode a Python long integer (bigint) from a string of bytes.
    
    See http://bugs.python.org/issue923643
    
    """
    return long(binascii.hexlify(s), 16)

def long2bytes(n):
    """
    Encode a Python long integer (bigint) as a string of bytes.
    
    See http://bugs.python.org/issue923643
    
    """
    
    hexstring = "%x" % n
    
    if len(hexstring) % 2 != 0:
        # Pad to even length, big-endian.
        hexstring = "0" + hexstring
    
    return binascii.unhexlify(hexstring)

def time2string(seconds):
    """
    Given a seconds since epock int, return a UTC time string.
    
    """
    
    return time.strftime("%d %b %Y %H:%M:%S", time.gmtime(seconds))

