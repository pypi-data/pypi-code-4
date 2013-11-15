"""This module provides the interfaces with authentcation server
"""
from werkzeug.wrappers import Response


def check_auth(ldap, username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    ld_server = ldap.get('ldap')
    # query = ldap.get('query') % dict(username=username)
    query = ldap.get('query') % username
    try:
        ld_server.simple_bind_s(query, password)
        return True
    except:
        return False


def authenticate():
    """Sends a 401 response that enables basic auth.
    """
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def is_authenticated(ldap, request):
    """Verify wether the request is authorized or not.
    """
    auth = request.authorization
    return auth and check_auth(ldap, auth.username, auth.password)
