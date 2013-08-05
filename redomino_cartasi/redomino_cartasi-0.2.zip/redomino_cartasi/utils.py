import sha
import re

from django.conf import settings

from redomino_cartasi import cartasiLogger as logger

def get_mac(code):
    """
    >>> code = ''.join(['ESE_WEB_00000001', '01234abcdefg01234567', '000000009', '978', '01.00', 'L', 'AUT', 'nome_cognome@tiscali.it', '228829EWDKLSDJD392132']) 
    >>> get_mac(code)
    '7A923F33473062F74EDC0CB05A7D1F7F611D5E3D'
                    
    """

    return sha.new(code).hexdigest().upper()

def transaction2order_id(transaction_id):
    """
    >>> transaction_id = 'T0000000000000000035'
    >>> transaction2order_id(transaction_id)
    '35'

    >>> transaction_id = 'T0000000000000000350'
    >>> transaction2order_id(transaction_id)
    '350'
    """
    regexp = '^T[^1-9]*([1-9][0-9]*)$'
    match = re.match(regexp, transaction_id)
    if match:
        return match.group(1)
    return ''

def log(msg):
    logger.info(msg)

def log_debug(msg):
    if settings.DEBUG:
        log(msg)

    
