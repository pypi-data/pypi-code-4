# -*- coding: utf-8 -*-
#
# Copyright (c) 2013, Alexander Vyushkov
# All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


from M2Crypto import RSA, DSA
import hashlib, time, base64
import urllib

class Authpubtkt(object):
    filename = None
    pub_key = None

    def __init__(self, filename=None, pub_key=None):
        if filename:
            self.filename = file
            pub_key = DSA.load_pub_key(filename)

        if pub_key is None:
            raise ValueError("Please specify filename or public key")
        if not isinstance(pub_key, RSA.RSA_pub) and not isinstance(pub_key, DSA.DSA_pub):
            raise ValueError('Unknown key type: %s' % type(pub_key))
        self.pub_key = pub_key


    def verify_ticket_signature(self, data, sig):
        """Verify ticket signature. """
        signature = base64.b64decode(sig)
        digest = hashlib.sha1(data).digest()
        if isinstance(self.pub_key, RSA.RSA_pub):
            try:
                self.pub_key.verify(digest, signature, 'sha1')
            except RSA.RSAError:
                return False
            return True
        if isinstance(self.pub_key, DSA.DSA_pub):
            return self.pub_key.verify_asn1(digest, signature)
        # Unknown key type
        return False

    def verify_cookie(self, cookie):
         # Authentication tickets to be processed by mod_auth_pubtkt are composed of key/value pairs, with keys and values separated by '=' and
        # individual key/value pairs separated by semicolons (';'). Last key is signature:
        #
        # sig (required)
        # a Base64 encoded RSA or DSA signature over the SHA-1 digest of the content of the ticket up to (but not including) the semicolon before 'sig'
        # RSA: raw result; DSA: DER encoded sequence of two integers – see Dss-Sig-Value in RFC 2459
        # must be the last item in the ticket string
        # Here's an example of how a real (DSA) ticket looks:
        #
        # uid=mkasper;cip=192.168.200.163;validuntil=1201383542;tokens=foo,bar;udata=mydata;
        # sig=MC0CFDkCxODPml+cEvAuO+o5w7jcvv/UAhUAg/Z2vSIjpRhIDhvu7UXQLuQwSCF=

        data = cookie.rsplit(";",1)[0]
        signature = cookie.rsplit(";",1)[1][4:] # Skip "sig="

        if not self.verify_ticket_signature(data, signature):
            return None

        data = data.split(";")
        ticket_keys = dict()
        for item in data:
            ticket_keys[item.split("=")[0]] = item.split("=")[1]

        try:
            if ticket_keys['validuntil'] < time.time():
                # Ticket expired
                return None
        except KeyError:
            # No expiration time
            return None

        # Ticket is valid
        return ticket_keys
