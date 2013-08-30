import logging

import facepy

from zope.interface import Interface
from zope.interface.declarations import classImplements

log = logging.getLogger(__name__)


def includeme(config):
    config.add_request_method(request_get_application_graph_api, 'graph_api',
                              reify=True)


def request_get_application_graph_api(request):
    return get_application_graph_api(request.registry)


def get_application_graph_api(registry):
    graph_api = registry.queryUtility(IGraphAPI, name='application_graph_api')

    if graph_api is None:
        log.debug('Create GraphAPI with facebook application token')

        app_id = registry.settings['facebook.app_id']
        secret_key = registry.settings['facebook.secret_key']
        app_token = facepy.get_application_access_token(app_id, secret_key)
        graph_api = facepy.GraphAPI(app_token)
        registry.registerUtility(graph_api, name='application_graph_api')

    return graph_api


class IGraphAPI(Interface):
    pass


classImplements(facepy.GraphAPI, IGraphAPI)
