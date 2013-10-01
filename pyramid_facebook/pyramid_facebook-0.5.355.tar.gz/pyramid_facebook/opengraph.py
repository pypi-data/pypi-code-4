import posixpath

from zope.interface import Interface, Attribute
from pyramid.view import view_config
from pyramid.traversal import resource_path_tuple
from pyramid.httpexceptions import HTTPMethodNotAllowed


def includeme(config):
    config.add_directive('add_opengraph_collection', add_collection)
    config.scan('.opengraph')


class IResource(Interface):
    """Interface used to configure a view for all OpenGraph objects."""

    prefixes = Attribute('Extra OpenGraph prefixes')
    properties = Attribute('Dictionary of properties-values')


def add_collection(config, cls, pattern):
    """Add route and resource factory for a collection of objects.

    Interface for the collection:

        __name__ and __parent__ attributes set to None

        __init__(self, request)

        __getitem__(self, key)
            Returns an object implementing IResource.
    """
    # note that cls.__name__ is the Python class attribute, e.g.
    # 'VirtualGoodCollection', not the Pyramid instance attribute
    # that is used for URI generation, e.g. 'packs'
    namespace = config.registry.settings['facebook.namespace']
    pattern = posixpath.join(namespace, pattern, '{object_id}')

    config.add_route(name='opengraph_%s' % cls.__name__.lower(),
                     pattern=pattern,
                     traverse='/{object_id}',
                     factory=cls,
                     use_global_views=True)


@view_config(context=IResource,
             request_method='GET',
             renderer='pyramid_facebook:templates/opengraph_object.mako')
def show_opengraph_object(context, request):
    # TODO support redirect_url
    resource_path = resource_path_tuple(context)[1:]
    og_url = request.current_route_url(traverse=resource_path,
                                       _query=request.GET)
    # TODO make the update conditional
    context.properties.update({
        'fb:app_id': request.registry.settings['facebook.app_id'],
        'og:url': og_url,
    })
    return {'prefixes': context.prefixes,
            'properties': context.properties}


@view_config(context=IResource)
def default_opengraph_object(context, request):
    raise HTTPMethodNotAllowed()
