#
# Copyright (c) 2013
#   Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import Cookie
import datetime
import random
import uuid, base64

COILS_SESSION_COOKIE_NAME='OGOCOILSESSIONID'

def generate_session_cookie(request, session_id=None):
    if not session_id:
        session_id = '{0}.{1}.{2}.{3}.{4}'.format( uuid.uuid4().hex,
                                                   random.randint( 10000000 ),
                                                   self.request.server_name,
                                                   self.request.server_port,
                                                   self.request.client_address )
        session_id = base64.b64encode( session_id )

    expiration = datetime.datetime.now() + datetime.timedelta(days=1)
    cookie = Cookie.SimpleCookie()
    cookie[ COILS_SESSION_COOKIE_NAME ] = session_id
    cookie[ COILS_SESSION_COOKIE_NAME ][ 'domain'] = request.server_name
    cookie[ COILS_SESSION_COOKIE_NAME ][ 'path'] = "/"
    cookie[ COILS_SESSION_COOKIE_NAME ][ 'expires'] = expiration.strftime( "%a, %d-%b-%Y %H:%M:%S UTC" )
    return cookie

def get_session_id_from_request(request):
    session_id = None
    cookie_header = request.headers.get ( 'cookie', )
    if cookie_header:
        x = Cookie.SimpleCookie( cookie_header, )
        if COILS_SESSION_COOKIE_NAME in x:
            session_id = x[ COILS_SESSION_COOKIE_NAME ].value
    return session_id
