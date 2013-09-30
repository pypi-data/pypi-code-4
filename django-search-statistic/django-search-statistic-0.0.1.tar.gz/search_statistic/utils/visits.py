# coding: utf-8
from django.db.models import Model
from search_statistic import settings, cache, cache_key
from search_statistic.models import SearchQuery, Visit

import cPickle
import threading


def visit_object(request, obj):
    visit = getattr(request, 'search_statistic', {}).get('visit')
    if visit:
        if isinstance(obj, Model):
            content_type = obj.__class__
            object_pk = obj.pk
        else:
            content_type = obj
            object_pk = None
        content_type = cPickle.dumps(content_type)

        if settings['REDIS_CACHE_SIZE'] != 1 and cache:
            visit['content_type'] = content_type
            visit['object_pk'] = object_pk
        else:
            visit.content_type = content_type
            visit.object_pk = object_pk


def flush_visits():
    queries = {}
    query_visits = {}
    visits = []

    pks_key = cache_key("visits_pks")
    all_pks = cache.smembers(pks_key)
    waste_pks = []
    for pk in all_pks:
        visit_key = cache_key("visit:{}".format(pk))
        visit = cache.hgetall(visit_key)
        if visit:
            waste_pks.append(pk)
            q, p, e = visit['query'], visit['path'], visit['search_engine']
            if q not in queries:
                queries[q] = None
            if q not in query_visits:
                query_visits[q] = {}
            if p not in query_visits[q]:
                query_visits[q][p] = {}
            if e not in query_visits[q][p]:
                query_visits[q][p][e] = Visit(
                    search_engine=e,
                    path=p,
                    content_type=visit.get('content_type'),
                    object_pk=visit.get('object_pk'),
                    amount=0
                )
            query_visits[q][p][e].amount += 1
            if query_visits.get('content_type'):
                query_visits[q][p].content_type = visit['content_type']
                query_visits[q][p].object_pk = visit.get(object_pk)

    for q in queries:
        queries[q] = SearchQuery.objects.get_or_create(
            query=q,
            defaults={
                'confirm': settings['default_query_confirm']
            }
        )[0]
        for p, ev in query_visits[q].iteritems():
            for e, v in query_visits[q][p].iteritems():
                v.query = queries[q]
                visits.append(v)
    Visit.objects.bulk_create(visits)
    cache.srem(pks_key, *waste_pks)
    cache.delete(*[cache_key('visit:{}'.format(pk)) for pk in waste_pks])


def flush_visits_in_thread():
    t = threading.Thread(target=flush_visits)
    t.start()