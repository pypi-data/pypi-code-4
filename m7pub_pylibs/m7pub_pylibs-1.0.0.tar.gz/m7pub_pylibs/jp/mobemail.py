#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2009, MARIMORE Inc Tokyo, Japan.
# Contributed by 
#       Iqbal Abdullah <iqbal@marimore.co.jp>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:
#
#   *   Redistributions of source code must retain the above copyright notice, 
#       this list of conditions and the following disclaimer.
#   *   Redistributions in binary form must reproduce the above copyright notice, 
#       this list of conditions and the following disclaimer in the documentation 
#       and/or other materials provided with the distribution.
#   *   Neither the name of the MARIMORE Inc nor the names of its contributors 
#       may be used to endorse or promote products derived from this software 
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON 
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Utilities for JP mobile 
"""

__author__      = "Iqbal Abdullah <iqbal@marimore.co.jp>"
__date__        = "$LastChangedDate: 2011-01-15 11:22:39 +0900 (Sat, 15 Jan 2011) $"
__version__     = "$LastChangedRevision: 31 $"


JP_MOBILE_EMAIL_DOMAINS = {

    'DOCOMO': (
        'docomo.ne.jp', 
        'mopera.net', 
        'mopera.ne.jp', 
        'docomo.blackberry.com',
        'dwmail.jp',
    ),

    'KDDI': (
        'ezweb.ne.jp', 
    ),

    'SOFTBANK': (
        'softbank.ne.jp', 
        'i.softbank.jp', 
        't.vodafone.ne.jp', 
        'd.vodafone.ne.jp', 
        'h.vodafone.ne.jp', 
        'c.vodafone.ne.jp', 
        'k.vodafone.ne.jp', 
        'r.vodafone.ne.jp', 
        'n.vodafone.ne.jp', 
        's.vodafone.ne.jp', 
        'q.vodafone.ne.jp', 
        'jp-c.ne.jp', 
        'jp-d.ne.jp', 
        'jp-h.ne.jp', 
        'jp-k.ne.jp', 
        'jp-n.ne.jp', 
        'jp-r.ne.jp', 
        'jp-s.ne.jp', 
        'jp-t.ne.jp', 
        'jp-q.ne.jp', 
        'disney.ne.jp', 
    ),

    'EACCESS': (
        'emnet.ne.jp',
    ),

    'WILLCOM': (
        'willcom.com', 
        'pdx.ne.jp', 
        'di.pdx.ne.jp', 
        'dj.pdx.ne.jp', 
        'dk.pdx.ne.jp', 
        'wm.pdx.ne.jp', 
    ),


}
""" 
A dictionary of jp mobile email domains. The keys are the carrier names, and the
individual list members are email domain names for the carriers.
"""

def get_mobile_email_domains():
    """
    .. warning:: This function is DEPRECATED and is not maintained. If you require the carrier names as a dictionary, access *JP_MOBILE_EMAIL_DOMAINS* directly

    Returns a dictionary with lists of recognised domains for emails from mobile

    The dictionary will contain carrier names for keys, and a list of domain names for
    each carrier.

    Possible carrier names are:
        - DOCOMO
        - KDDI
        - SOFTBANK
        - EACCESS
        - WILLCOM
    """

    return { 
        'DOCOMO'    : JP_MOBILE_EMAIL_DOMAINS['DOCOMO'],
        'KDDI'      : JP_MOBILE_EMAIL_DOMAINS['KDDI'],
        'SOFTBANK'  : JP_MOBILE_EMAIL_DOMAINS['SOFTBANK'],
        'WILLCOM'   : JP_MOBILE_EMAIL_DOMAINS['WILLCOM'],
        'EACCESS'   : JP_MOBILE_EMAIL_DOMAINS['EACCESS'],
    }


def get_mobile_carrier(domain):
    """
    Returns the name of the carrier if *domain* is a mobile JP domain, and
    returns None if it's not.
    """

    for carrier in JP_MOBILE_EMAIL_DOMAINS.keys():
        if domain in JP_MOBILE_EMAIL_DOMAINS[carrier]:
            return carrier

    return None


if __name__ == '__main__':

    print get_mobile_email_domains()
    print get_mobile_carrier("docomo.ne.jp")
    print get_mobile_carrier("i.softbank.jp")
    print get_mobile_carrier("yahoo.co.jp")
