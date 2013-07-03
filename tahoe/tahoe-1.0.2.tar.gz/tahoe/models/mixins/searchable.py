"""
The MIT License (MIT)

Copyright (c) 2013 Lunar Technology Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import pyes
from tahoe import search
from tahoe.misc import get_timestamp


def SearchableMixin(bucket, logger):
    elastic_search = bucket.get('elastic_search')
    environment = bucket.get('environment')

    class SearchableMixin(object):
        """
        Makes a Model Searchable.

        Consult the ``Account`` model to see examples.

        Essentially, all you have to do to make a model searchable
        is to include this mixin in its definition and then define two
        methods to define how you would like the model indexed by
        ElasticSearch.
        """
        @classmethod
        def _search_geo_configure(cls, search_terms, distance, filters, sort, geo_filter=pyes.GeoDistanceFilter):
            """
            Determines is the query was geo-centered and configure the query appropriately.

            Results will be geo-filtered if the query included both ``lat``
            and ``lng`` facet.  The results will be filtered in KILOMETERS
            by the ``distance`` argument.

            If there existed a ``sorted_by`` parameter set to 'distance' then
            the results will be organized by distance from the given
            lat/lng coordinates.

            If ``lat`` and ``lng`` were not specified, this is a no-op.
            """
            lat = search_terms.get('lat')
            lng = search_terms.get('lng')
            sorted_by = search_terms.get('sorted_by')
            geo_search = False
            if lat and lng:
                geo_search = True
                location = "{},{}".format(lat, lng)
                filters.append(
                    geo_filter(
                        "location",
                        location,
                        distance,
                        distance_type="arc",
                        distance_unit="km"
                        ))
                if sorted_by == 'distance':
                    sort = [dict(_geo_distance=dict(
                        location=location,
                        order="asc",
                        unit="km",
                        ))]
            return sort, geo_search

        @classmethod
        def _search_geo_annotate_distance(cls, geo_results):
            """
            Annotates the results with each result's distance from the
            latitude and longitude given in the query.
            """
            for result in geo_results:
                if result._meta.sort:
                    result[u'distance'] = result._meta.sort[0]
                    result[u'distance_unit'] = 'km'
            return geo_results

        @classmethod
        def search(cls, per_page=12, page=1, distance=100, sort=None, **search_terms):
            """
            Parameters:

            - `per_page`: How many results to return per page.
            - `page`: Which page of results to return.
            - `sort` (list): `[{'created_at':'asc'}, {'username':'desc'}]`
            - `**search_terms`: Keyword args: `{'username':'clint'}`
            """
            queries = []
            filters = []
            # Obtain the mapping as defined by the model
            mapping = cls._search_builder_mapping()
            # Build up the query using the given terms and the allowed
            # fields in the mapping.
            logger.info("Got search terms: {}".format(search_terms))
            for field, value in search_terms.iteritems():
                query_builder = mapping.get(field)
                if query_builder:
                    query = query_builder.for_value(value)
                    if query_builder.filter:
                        filters.append(query)
                    else:
                        queries.append(query)
            logger.info("Produced queries: {}".format(queries))
            # Setup geo filters if necessary
            sort, geo_search = cls._search_geo_configure(
                search_terms,
                distance,
                filters,
                sort
                )
            f = None
            if queries:
                # All queries must be satisfied
                q = pyes.BoolQuery(must=queries)
            else:
                # If no queries happened to be produced by this query,
                # we start with Matching everything.
                q = pyes.MatchAllQuery()
            if filters:
                # We AND together all the filters.
                f = pyes.ANDFilter(filters)

            try:
                page = int(page)
            except ValueError:
                page = 1

            try:
                per_page = int(per_page)
            except ValueError:
                per_page = 12

            start = (page - 1) * per_page
            # Produce a Search Object. Hint: You can print this to see
            # the JSON search object that will be transmitted to the ES
            # server.
            s = pyes.Search(
                query=q,
                filter=f,
                sort=sort,
                start=start,
                size=per_page
                )

            # Produce the resultset.
            results = elastic_search.search(
                s,
                doc_types=[cls._search_doc_type()],
                indices=[cls._search_index_alias()],
                start=start
                )

            logger.info("Got {} results: {}.".format(results.total, results))

            # Results is a lazy object, so lets chop it down.
            results = [p for p in results]
            # If the query was geo-search targeted, we will annotate each
            # result with the distance from the source coordinates (in KM).
            if geo_search:
                results = cls._search_geo_annotate_distance(results)
            return results

        @classmethod
        def _search_doc_type(cls):
            """
            Determines which "Document Type" mapping to use in ElasticSearch.

            We just use the string of the Class we're indexing.
            """
            return cls.__name__

        @classmethod
        def _search_index_alias(cls):
            """
            We use ElasticSearch aliases to point to timestamped versions
            of the Model's real index.  Makes things easier.

            Accounts would be indexed at:

                ``accounts-production``
            """
            return "{}-{}".format(
                cls._search_doc_type().lower(),
                environment.lower()
                )

        @classmethod
        def _search_index_name(cls, suffix):
            """
            The real indexes are generally something like:

                ``photos-staging-<< timestamp() >>``
            """
            return "{}-{}".format(
                cls._search_index_alias(),
                str(suffix)
                )

        @classmethod
        def _search_index(cls):
            """
            Defines how the ElasticSearch Index for a given model should be configured.
            """
            return dict(
                settings=search.STANDARD_SETTINGS,
                mappings={cls._search_doc_type(): cls._search_index_mapping()}
                )

        @classmethod
        def _search_builder_mapping(self):
            """
            How the fields of a model should be **queried**.

            Define this method on your model. It should return a mapping
            of terms you expect to be passed to your model's ``search()``
            method.

            Consult the ``Account`` model to get common examples.
            Additional builder types can be defined in ``tahoe.search``.
            """
            raise NotImplementedError("Define a search builder mapping on your Model.")

        @classmethod
        def _search_index_mapping(cls):
            """
            How to fields of a model should be **indexed**.

            Define this method on your model. It should return a mapping of
            fields present in your model's ``to_dict()`` method and how
            ElasticSearch should index those fields.

            Consult the ``Account`` model to get common examples. Additional
            index types can be defined in ``tahoe.search``.
            """
            raise NotImplementedError("Define a search index mapping on your Model.")

        @classmethod
        def _search_create_index(cls, suffix):
            """
            Creates a new timestamped index for a model.

            Produces a timestamped index for a Model and applies the
            developer-defined mapping for each field.
            """
            index_name = cls._search_index_name(suffix=suffix)
            logger.info("Creating index: {}".format(index_name))
            index_settings = cls._search_index().get('settings')
            elastic_search.indices.delete_index_if_exists(index_name)
            elastic_search.indices.create_index(
                index_name,
                settings=index_settings
                )
            mapping = cls._search_index_mapping()
            doc_type = cls._search_doc_type()
            logger.info(" - Applying mapping for: {}".format(doc_type))
            elastic_search.indices.put_mapping(doc_type, mapping, [index_name])
            return index_name

        @classmethod
        def _search_index_all_records(cls, suffix=None, index_name=None, remove_old=False, refresh_now=False):
            """
            Sets up a new index for a model and re-indexes all the data for that model.

            Goal: Online generation of a new index without index downtime.

            Procedure:

                - Create a new timestamped index for the Model
                - Index every un-deleted document into this new index.
                - Alias the commonly-known index name to the new timestamped
                  index.
                - Remove all the old indices.
            """
            suffix = suffix or get_timestamp()
            index_name = index_name or cls._search_create_index(suffix=suffix)
            index_alias = cls._search_index_alias()
            doc_type = cls._search_doc_type()
            if hasattr(cls, 'query_active'):
                query = cls.query_active()
            else:
                query = cls.query

            num_records_indexed = 0
            logger.info(' - Indexing {} records into {}.'.format(
                doc_type,
                index_name
                ))
            for record in query.all():
                if record.can_index():
                    num_records_indexed += 1
                    record.index(index_name=index_name, bulk=True)

            logger.info(' - Indexed {} {}(s) into {}'.format(
                num_records_indexed,
                doc_type,
                index_name
                ))

            if refresh_now:
                elastic_search.indices.refresh(index_name)
                logger.info(' - Refreshed index: {}'.format(index_name))

            elastic_search.indices.delete_index_if_exists(index_alias)
            elastic_search.indices.add_alias(index_alias, index_name)
            logger.info(' - Aliased {} to {}'.format(index_name, index_alias))

            if remove_old:
                logger.info(' - Removing old indices:')
                current_indices = elastic_search.indices.aliases()
                # Remove all old indexes which match this prefix (except the one we just made!)
                cleanup_indices = [a_index_name for a_index_name, _ in current_indices.iteritems() if a_index_name.startswith(index_alias) and a_index_name != index_name]
                for index_name in cleanup_indices:
                    elastic_search.indices.delete_index_if_exists(index_name)
                    logger.info("    - Deleted old index: {}".format(index_name))

            return dict(
                index_name=index_name,
                index_alias=index_alias,
                doc_type=doc_type,
                num_records_indexed=num_records_indexed,
                num_indices_deleted=len(cleanup_indices),
                indices_deleted=cleanup_indices
                )

        def index(self, index_name=None, bulk=False):
            """
            Indexes this model instance.

            Does not immediately make it available for search.  If you need
            the record to appear immediately, you must refresh the index.

            Otherwise, the results will only become available as ES
            periodically refreshes its indexes.
            """
            index_name = index_name or self.__class__._search_index_alias()
            return elastic_search.index(
                doc=self.to_dict(),
                index=index_name,
                doc_type=self.__class__._search_doc_type(),
                id=self.id,
                bulk=True
                )

        def can_index(self):
            """
            Determines if a model can be indexed.
            """
            return hasattr(self, 'index') and hasattr(self, 'to_dict')

        def remove_from_index(self, index_name=None):
            """
            Removes an instance from the search index.
            """
            index_name = index_name or self.__class__._search_index_alias()
            try:
                elastic_search.delete(
                    index=index_name,
                    doc_type=self.__class__._search_doc_type(),
                    id=self.id
                    )
            except pyes.exceptions.NotFoundException:
                return False
            return True

    return SearchableMixin
