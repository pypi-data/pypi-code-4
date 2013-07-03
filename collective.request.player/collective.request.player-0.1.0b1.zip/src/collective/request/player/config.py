""" It provides the package constants """

# Almost all parameters was copied from requests package.
# Details: https://github.com/kennethreitz/requests/blob/master/requests/sessions.py#LC235
ALLOWED_INPUT_PARAMS = {
    'method': 'GET',
    # The url (parameter) was substituted for path_info.
    # path_info example: '/Plone', '/www/@@requests_player'
    'path_info': '/Plone',
    'data': {},
    'headers': {},
    'cookies': {},
    'files': {},
    'auth': (),
    'allow_redirects': True,
    'proxies': {},
    'stream': False,
    'verify': False,
    'cert': (),
}
