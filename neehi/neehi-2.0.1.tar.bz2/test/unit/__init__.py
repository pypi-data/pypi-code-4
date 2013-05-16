""" Constants used for tests in the neehi package.

Copyright 2012 Sean Robinson <seankrobinson@gmail.com>

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
3. Neither the name of the author nor the names of contributors may be used
   to endorse or promote products derived from this software without specific
   prior written permission.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA
OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

# REQ5_AUTH_* are the valid requests a client may use to initialize a
# connect to the SOCKS5 proxy.  The response from the SOCKS5 proxy should
# be one of RESP5_AUTH_*.
#
REQ5_AUTH_NOAUTH = b'\x05\x01\x00'        # Client cannot provide authentication
REQ5_AUTH_USERPASS = b'\x05\x02\x00\x02'  # Client supports username/password

# RESP5_AUTH_* are the two-byte response from the SOCKS5 proxy detailing
# which authentication methods are allowed.  This is in answer to the
# client query (i.e. REQ5_AUTH_*) giving the authentication method it
# wants to use.
#
RESP5_AUTH_BASIC = b'\x05\x02'         # Basic username/password authentication
RESP5_AUTH_EBADMSG = b'\x00\x00'       # Invalid data
RESP5_AUTH_EBADMSG2 = b'\x05\xF0'      # Another invalid data
RESP5_AUTH_NONE = b'\x05\x00'          # No authentication is required
RESP5_AUTH_NOTALLOWED = b'\x05\xFF'    # Not allowed

# REQ5_AUTHREQ_HEADER begins the authentication request with the SOCKS5
# proxy.  The remainder of the message is: one-byte for the username
# length, the username, one-byte of the password length, the password.
#
# So, an authentication request may look like: b'\x01\x04user\x08password'.
#
REQ5_AUTHREQ_HEADER = b'\x01'   # requesting username/password authentication

# RESP5_AUTHSTAT_* are the two-byte response from the SOCKS5 proxy
# approving or denying the authentication request from the client.
# These only come into play if RESP5_AUTH_BASIC is received and the
# client attempts to authenticate with a username and password.
#
RESP5_AUTHSTAT_EBADMSG = b'\x00\x00'   # Invalid data
RESP5_AUTHSTAT_FAIL = b'\x01\x01'      # Authentication failed
RESP5_AUTHSTAT_SUCCESS = b'\x01\x00'   # Authentication succeeded

# RESP5_REQCONN_* are the four-byte response from the SOCKS5 proxy
# detailing the success (and bound address location) or failure (and
# the reason) of the requested connection.
#
RESP5_REQCONN_EBADMSG = b'\x00\x00\x00\x01'       # Invalid data
RESP5_REQCONN_EBADMSG2 = b'\x05\x00\x00\xF0'       # Another invalid data
RESP5_REQCONN_FAILGEN = b'\x05\x01\x00\x00'       # general SOCKS server failure
RESP5_REQCONN_NOTALLOWED = b'\x05\x02\x00\x00'    # connection not allowed by ruleset
RESP5_REQCONN_ENETUNREACH = b'\x05\x03\x00\x00'   # Network unreachable
RESP5_REQCONN_EHOSTUNREACH = b'\x05\x04\x00\x00'  # Host unreachable
RESP5_REQCONN_ECONNREFUSED = b'\x05\x05\x00\x00'  # Connection refused
RESP5_REQCONN_TTLEXPIRED = b'\x05\x06\x00\x00'    # TTL expired
RESP5_REQCONN_ENOTSUP = b'\x05\x07\x00\x00'       # Command not supported
RESP5_REQCONN_EAFNOSUPPORT = b'\x05\x08\x00\x00'  # Address type not supported
RESP5_REQCONN_UNKNOWN = b'\x05\x09\x00\x00'       # Unknown error
RESP5_REQCONN_ADDRFIX = b'\x05\x00\x00\x01'       # Sucess: get the 4-byte bound address
RESP5_REQCONN_ADDRVAR = b'\x05\x00\x00\x03'       # Sucess: get the variable length bound address

# RESP4_REQCONN_* are the first two bytes of an eight-byte response
# -- bytes 3 and 4 are the bound port number
# -- bytes 5 through 8 are the bound address
#
# So, SOCKS4/4A responses should be built as a RESP4_REQCONN_* followed
# by six more bytes with port and address information.
#
RESP4_REQCONN_EBADMSG = b'\x01\x00'    # Invalid data
RESP4_REQCONN_IDCONN = b'\x00\x5C'     # request rejected: identd connect failed
RESP4_REQCONN_IDDIFF = b'\x00\x5D'     # request rejected: different user reported
RESP4_REQCONN_REJECT = b'\x00\x5B'     # request rejected or failed
RESP4_REQCONN_SUCCESS = b'\x00\x5A'    # Connection succeeded
RESP4_REQCONN_UNKNOWN = b'\x00\x5E'    # Unknown error

RESP4_EMPTY_ADDR = b'\x00' * 6         # Empty address and port

# RESPHTTP_* are the variable-length parts of HTTP responses from the
# HTTP proxy.  These are combined in different ways to test the success
# or failure of the requested connection.
#
RESPHTTP_EOL = b'\r\n'                   # End-of-line
RESPHTTP_MSGEND = b'\r\n\r\n'            # End of a valid HTTP response
RESPHTTP_STATUS_200 = b' 200 OK'         # HTTP success header
RESPHTTP_STATUS_404 = b' 404 Not Found'  # HTTP 404 error
RESPHTTP_STATUS_INVALID = b' WTF'        # HTTP success header
RESPHTTP_VER10 = b'HTTP/1.0'             # HTTP 1.0 header
RESPHTTP_VER11 = b'HTTP/1.1'             # HTTP 1.1 header
RESPHTTP_VERBAD = b'HTTP'                # HTTP 1.1 header

