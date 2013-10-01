# coding: utf-8
from search_statistic import settings, cache, cache_key
from search_statistic.models import Visit, SearchQuery
from search_statistic.utils.search_engine import all_engines
from search_statistic.utils.visits import flush_visits_in_thread


class CollectStatisticMiddleware(object):

    def process_request(self, request):
        request.search_statistic = {}

        search_query = None
        search_engine = None

        for engine in all_engines():
            search_query = engine.extract_query(request)
            if search_query:
                search_engine = engine.get_key()
                break

        if search_query and search_engine:
            if settings['REDIS_CACHE_SIZE'] != 1 and cache:
                request.search_statistic['visit'] = {
                    'path': request.path,
                    'search_engine': search_engine,
                    'query': search_query
                }
            else:
                request.search_statistic['visit'] = Visit(
                    path=request.path,
                    search_engine=search_engine,
                    query=SearchQuery.objects.get_or_create(
                        query=search_query,
                        defaults={
                            'confirm': settings['default_query_confirm']
                        }
                    )[0]
                )

    def process_response(self, request, response):
        if response.status_code < 400:
            if hasattr(request, 'search_statistic') and 'visit' in request.search_statistic:
                if settings['REDIS_CACHE_SIZE'] != 1 and cache:
                    pk = cache.incr(cache_key('visit_id'))
                    pks_set_key = cache_key("visits_pks")
                    visit_key = cache_key("visit:{}".format(pk))
                    cache.sadd(pks_set_key, pk)
                    cache.hmset(visit_key, request.search_statistic['visit'])

                    if settings['REDIS_CACHE_SIZE'] > 1:
                        if cache.scard(pks_set_key) >= settings['REDIS_CACHE_SIZE']:
                            flush_visits_in_thread()
                else:
                    visit = request.search_statistic.get('visit')
                    if visit:
                        visit.save()
        if response.status_code in settings['REMOVE_ON_STATUS']:
            Visit.objects.filter(path=request.path).delete()
        return response