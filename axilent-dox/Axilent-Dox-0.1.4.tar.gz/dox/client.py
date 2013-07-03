"""
Axilent Client functionality for Dox.
"""
from sharrock.client import HttpClient, ResourceClient, ServiceException
from dox.config import get_cfg
from dox.utils import slugify

def _get_resource(app,resource,library=True):
    """
    Gets a resource client.
    """
    cfg = get_cfg()
    apikey_setting = 'library_key' if library else 'api_key'
    return ResourceClient('%s/api/resource' % cfg.get('Connection','endpoint'),app,'beta3',resource,auth_user=cfg.get('Connection',apikey_setting))

def _get_client(app,library=True):
    """
    Gets a regular API client.
    """
    cfg = get_cfg()
    apikey_setting = 'library_key' if library else 'api_key'
    return HttpClient('%s/api' % cfg.get('Connection','endpoint'),app,'beta3',auth_user=cfg.get('Connection',apikey_setting))

def get_content_library_resource():
    """
    Gets a content library resource.
    """
    return _get_resource('axilent.library','content')

def get_library_client():
    """
    Gets the library API client.
    """
    return _get_client('axilent.library')

def ping_library():
    """
    Pings the library.
    """
    cfg = get_cfg()
    lib = get_library_client()
    lib.ping(project=cfg.get('Connection','project'),content_type=cfg.get('Connection','content_type'))

def get_content_api():
    """
    Gets the content API.
    """
    return _get_client('axilent.content',library=False)

def get_content_resource():
    """
    Gets the deployed content resource.
    """
    return _get_resource('axilent.content','content',library=False)

def get_content_keys():
    """
    Gets the keys for the conten type.
    """
    cfg = get_cfg()
    api = get_content_api()
    keys = api.getcontentkeys(content_type_slug=slugify(cfg.get('Connection','content_type')))
    return keys

def get_content_item(key):
    """
    Gets deployed content for the specified key.
    """
    cfg = get_cfg()
    resource = get_content_resource()
    return resource.get(params={'content_type_slug':slugify(cfg.get('Connection','content_type')),'content_key':key})
