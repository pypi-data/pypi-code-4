#coding:utf-8
from django.core.cache import cache


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
        
        method = str(method)
        super_obj =  super(CachedSerializedResourceMixin, self)
        
        filters=''
        if hasattr(request, 'GET') and len(request.GET):
            filters = '?' + ':'.join(list(reduce(lambda x, y: x + y, request.GET.items())))

        cache_key = 'tastypie-' + super_obj.generate_cache_key(method + filters, **self.remove_api_resource_names(kwargs))
        serialized_response = cache.get(cache_key)

        if serialized_response is None:
            serialized_response = getattr(super_obj, 'get_%s' % method)(request, **kwargs)
            if getattr(self._meta, 'serialized_cache_timeout'):
                cache.set(cache_key, serialized_response, self._meta.serialized_cache_timeout)
            else:
                cache.set(cache_key, serialized_response)
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