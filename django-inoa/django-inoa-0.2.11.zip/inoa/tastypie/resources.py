#coding:utf-8
from django.core.cache import cache
try:
    import tastypie
except ImportError:
    # TODO (lsantos): add this message to setup.py to be shown in the end of the installation.
    raise ImportError('If you want to use inoa.tastypie you MUST install django-tastypie too. Try the latest version at https://pypi.python.org/pypi/django-tastypie/')

from tastypie.utils import is_valid_jsonp_callback_value


class CachedSerializedResourceMixin(object):
    """
    Caches the serialized response from the tastypie Resource list and detail views.
    Uses the django original cache.
    """    
    def _get_response(self, method, request, **kwargs):
        """
        Generic view wrapper to cache the wrapped view's serialized response.
        """
        
        check_format = self.create_response(request, None)
        if check_format.content == self._meta.serializer.to_html(None):
            return check_format

        request_GET_original = request.GET
        request_GET_copy = request_GET_original.copy()
        request.GET = request_GET_copy
        desired_format = self.determine_format(request)
        if 'text/javascript' in desired_format:
            callback = request.GET.get('callback', 'callback')

            if not is_valid_jsonp_callback_value(callback):
                raise BadRequest('JSONP callback name is invalid.')
            request_GET_copy.pop('callback', 0)
            request_GET_copy['format'] = 'json'
        
        method = str(method)
        super_obj =  super(CachedSerializedResourceMixin, self)
        
        filters=''
        if len(request.GET):
            filters = '?' + ':'.join(list(reduce(lambda x, y: x + y, request_GET_copy.items())))

        cache_key = 'tastypie-' + super_obj.generate_cache_key(method + filters, **self.remove_api_resource_names(kwargs))
        serialized_response = cache.get(cache_key)

        if serialized_response is None:
            serialized_response = getattr(super_obj, 'get_%s' % method)(request, **kwargs)
            if getattr(self._meta, 'serialized_cache_timeout'):
                cache.set(cache_key, serialized_response, self._meta.serialized_cache_timeout)
            else:
                cache.set(cache_key, serialized_response)

        if 'text/javascript' in desired_format:
            content = serialized_response.content
            try:
                content = unicode(content)
            except UnicodeDecodeError:
                # content is byte string
                ascii_text = str(content).encode('string_escape')
                content = unicode(ascii_text)
            content = content.replace(u'\u2028', u'\\u2028').replace(u'\u2029', u'\\u2029') #TODO (lsantos): check if this line still is needed
            content = u'%s(%s)' % (callback, content)
            serialized_response.content = content.decode('string_escape')

        return serialized_response

    def get_list(self, request, **kwargs):
        """
        Cached wrapper for the tastypie.Resource.get_list.
        """
        return self._get_response('list', request, **kwargs)

    def get_detail(self, request, **kwargs):
        """
        Cached wrapper for the tastypie.Resource.get_detail.
        """
        return self._get_response('detail', request, **kwargs)
