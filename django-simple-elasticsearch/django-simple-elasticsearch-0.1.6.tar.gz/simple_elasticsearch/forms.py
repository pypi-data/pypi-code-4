from django import forms
from django.conf import settings
from django.core.paginator import Paginator, Page, EmptyPage
from django.http import Http404
from django.utils import six
from pyelasticsearch import ElasticSearch


class ESPaginator(Paginator):
    """
    Override Django's built-in Paginator class to take in a count/total number of items;
    ElasticSearch provides the total as a part of the query results, so we can minimize hits.

    Also change `page()` method to use custom ESPage class (see below).
    """
    def __init__(self, *args, **kwargs):
        count = kwargs.pop('count', None)
        super(ESPaginator, self).__init__(*args, **kwargs)
        self._count = count

    def page(self, number):
        "Returns a Page object for the given 1-based page number."
        number = self.validate_number(number)
        return ESPage(self.object_list, number, self)


class ESPage(Page):
    def __getitem__(self, index):
        if not isinstance(index, (slice,) + six.integer_types):
            raise TypeError
        obj = self.object_list[index]
        return obj.get('_source', obj)


class ESSearchForm(forms.Form):
    def get_index(self):
        # return the ES index name (or multiple comma-separated) you want to target, or None if you don't want to target an index
        raise NotImplementedError

    def get_type(self):
        # return the ES type name (or multiple comma-separated) you want to target, or None if you don't want to target a type
        raise NotImplementedError

    def prepare_query(self, count, page=1, page_size=10, **kwargs):
        # `count` is a boolean indicating whether we want to simply get
        # the count of matchin docs or the actual results
        raise NotImplementedError

    def _get_results(self, count, **kwargs):
        self.is_valid()
        es = kwargs.pop('es', ElasticSearch(settings.ES_CONNECTION_URL))

        try:
            page_size = int(kwargs.pop('page_size', 20))
        except (ValueError, TypeError):
            page_size = 20
        try:
            page = int(kwargs.pop('page', 1))
        except (ValueError, TypeError):
            page = 1

        query = self.prepare_query(count, page, page_size, **kwargs)
        if type(query) in (list, tuple):
            msearch_data = u''
            for q in query:
                data = {'index': self.get_index(), 'type': self.get_type()}
                if 'routing' in kwargs:
                    data['routing'] = kwargs.get('routing')

                # if we want to retrieve search counts, we tweak things a little
                if count:
                    data['search_type'] = 'count'

                msearch_data += es._encode_json(data) + '\n'
                msearch_data += es._encode_json(q) + '\n'

            responses = es.send_request(
                'POST',
                ['_msearch'],
                msearch_data,
                encode_body=False
            )

            results = []
            if not count:
                return responses.get('responses', [])
            else:
                for response in responses.get('responses', []):
                    hit_stats = response.pop('hits', {})
                    total = hit_stats.get('total', 0)
                    results.append(total)

            return results

        elif not count:
            query_params = {}
            if 'routing' in kwargs:
                query_params['routing'] = kwargs.get('routing')

            response = es.search(
                query,
                index=self.get_index(),
                doc_type=self.get_type(),
                # query_params=query_params
            )
            hit_stats = response.pop('hits', {})
            hit_data = hit_stats.pop('hits', [])
            if kwargs.get('paginate', True):
                paginator = ESPaginator(
                    hit_data,
                    page_size,
                    count=hit_stats.get('total', 0)
                )

                try:
                    return paginator.page(page)
                except EmptyPage:
                    raise Http404
            else:
                return hit_data
        else:
            query_params = {}
            if 'routing' in kwargs:
                query_params['routing'] = kwargs.get('routing')

            return es.count(
                query.get('query', {}),
                index=self.get_index(),
                doc_type=self.get_type(),
                # query_params=query_params
            ).get('count', 0)

    def search(self, **kwargs):
        return self._get_results(count=False, **kwargs)

    def count(self, **kwargs):
        return self._get_results(count=True, **kwargs)
