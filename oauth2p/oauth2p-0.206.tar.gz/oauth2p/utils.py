import string

UNICODE_ASCII_CHARACTERS = (string.ascii_letters.decode('ascii') +
                            string.digits.decode('ascii'))


def generate_token_key(token, *args):
    """Returns token key for persistant storage.

    Keyword arguments:
    * token: token
    * type: token type (access_token, refresh_token)

    """
    return 'oauth2.' + '.'.join(str(arg) for arg in args if arg) + ':' + token
