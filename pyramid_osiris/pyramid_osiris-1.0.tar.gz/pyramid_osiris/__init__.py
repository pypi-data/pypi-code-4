from maxclient import MaxClient
from pyramid.exceptions import ConfigurationError
import pprint


class Connector(object):
    """ Provides API methods for accessing LDAP authentication information."""
    def __init__(self, registry, oauth_server, legacy_mode):
        self.registry = registry
        self.oauth_server = oauth_server
        self.legacy_mode = legacy_mode
        self.client = MaxClient(oauth_server=self.oauth_server)

    def authenticate(self, login, password):
        """ Given a username and a password, try to autheticate against Osiris
            server.
        """
        try:
            token = self.client.getToken(login, password)
            return [login, token]
        except AttributeError:
            return None


def osiris_setup(config, oauth_server, legacy_mode=False):
    """ Configurator method to set up an Osiris server. """
    vals = dict(oauth_server=oauth_server, legacy_mode=legacy_mode)

    def get_connector(request):
        registry = request.registry
        return Connector(registry, oauth_server, legacy_mode)

    config.set_request_property(get_connector, 'osiris_connector', reify=True)

    intr = config.introspectable(
        'pyramid_osiris setup',
        None,
        pprint.pformat(vals),
        'pyramid_osiris setup'
    )
    config.action('osiris-setup', None, introspectables=(intr,))


def get_osiris_connector(request):
    """ Return the Osiris connector attached to the request.  If
    :meth:`pyramid.config.Configurator.osiris_setup` was not called, using
    this function will raise an :exc:`pyramid.exceptions.ConfigurationError`."""
    connector = getattr(request, 'osiris_connector', None)
    if connector is None:
        raise ConfigurationError(
            'You must call Configurator.osiris_setup during setup '
            'to use an ldap connector')
    return connector


def includeme(config):
    """ Set up Configurator methods for pyramid_osiris """
    config.add_directive('osiris_setup', osiris_setup)
