from django.db.models import Q


class AutoComplete(object):
    query_set = None
    search_fields = []
    url_search_parameters = None
    requires_auth = False
    id_name = 'id'
    label_name = 'label'

    # noinspection PyUnusedLocal
    def get_queryset(self, request):
        """
        This function can be overridden to return custom query set.
        @return: The query set for performing extra searches.
        """
        return self.query_set

    def search_term(self, queryset, term):
        """
        Performs a simple database search for the term given.
        This function will performs a __contains in the given
        fields of the query set.

        @param term: str A search term
        @return: django.db.models.query.QuerySet a result query set.
        """
        query = None
        fields = self.search_fields
        for field in fields:
            kwargs = {field + "__contains": term}
            if query is None:
                query = Q(**kwargs)
            else:
                query = query | Q(**kwargs)
        return queryset.filter(query)

    def search_url_paramters(self, query, url_params):
        """
        This function performs a query lookup with the parameters from the url.
        @param query:
        @param url_params:
        @return:
        """
        url_search_parameters = self.url_search_parameters
        if url_search_parameters is not None:
            for parameter in url_search_parameters:
                args_dict = {parameter: url_params.get(parameter, '')}
                query = query.filter(**args_dict)
        return query

    def search(self, queryset, term, url_params):
        query = self.search_term(queryset, term)
        return self.search_url_paramters(query, url_params)

    def get_instances(self, ids):
        """
        Returns a queryset with the instances with given list of ids.
        This function is mainly used in many to many fields.

        @param ids: A list/enumerable of primary keys for which the datas has to be returned.
        @return: django.db.models.query.QuerySet
        """
        return self.query_set.filter(pk__in=ids)

    def get_instance(self, pk):
        """

        @param pk: The primary key for which the instance has to be returned.
        @return: A single instance of the current Model.
        """
        return self.query_set.get(pk=pk)

    def simple_format(self, instance, string, *fields):
        lst = []
        for term in fields:
            lst.append(getattr(instance, term))
        return string % tuple(lst)

    def format_value(self, instance):
        """
        Returns the formatted values that represents the current instance.
        @param instance:
        @return:
        """
        return unicode(instance)

    def get_search_term(self, request):
        """
        @author Muhammed K K
        @param request: django.http.HttpRequest current django request
        @return: str The term to be searched.
        """
        term = request.GET.get("term")
        if term is None:
            term = request.GET.get("q")
        return term

    def get_results(self, request, params):
        term = self.get_search_term(request)
        query = self.get_queryset(request)
        query = self.search(query, term, params)
        results = []
        for result in query:
            val = self.format_value(result)
            results.append({
                self.id_name: result.id,
                self.label_name: val,
            })
        return results