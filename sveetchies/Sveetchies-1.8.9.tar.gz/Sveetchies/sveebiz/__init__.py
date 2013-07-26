# -*- coding: utf-8 -*-
"""
Utility to create contracts/estimates.

For now, for estimates generation, only pdf format supported.

Values for options defined here are defaults values used for each option not defined
in the user's config file. Config file is an INI type file, readable by ConfigParser.
``config.sample`` is an example.

User's config file contains every option used by the generators to fill in documents.
It is designed to include all fixed user's info. The file must be located in
``~/.sveebiz/config`` or in ``/etc/sveebiz.conf``.

For now, the only real interface that uses the this module is in ``extensions_r2p.py``.
This is an extension to give for RST2PDF (it is in fact an extention for
ReStructuredText, used within RST2PDF ). See ``extensions_r2p.py``'help for
more details.

Another usage interface in CLI is in ``estimate.py``, but no not proceed to the ReST
output of the document, neither PDF not HTML.
"""
DEFAULT_CONFIG = {
    'identity': {
        'civility':None,
        'first_name':None,
        'last_name':None,
        'adress':None,
        'town':None,
        'zipcode':None,
        'structure_name':None,
        'email':None,
        'phone_number':None,
        'mobile_number':None,
    },
    'fees': {
        'base':'155',
        'evolution':'150',
        'corrective':'140',
    },
    'software': {},
}
