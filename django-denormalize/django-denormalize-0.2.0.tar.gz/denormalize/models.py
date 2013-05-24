from django.db import models

import logging

log = logging.getLogger(__name__)


class Skip(Exception):
    """Skip serializing a value"""
    pass

class MultipleValues(dict):
    """Used to rename keys, or split data into multiple keys"""
    pass

class DocumentCollection(object):
    # The root model
    model = None

    # Name of the target Collection. If not specified, db_table is used.
    name = None

    # Fields you want to exclude ('__'-traversal is supported)
    exclude = []
    # This applies to any level of traversal
    exclude_all = []

    # These are used for three things:
    # - to determine which models are related
    # - to determine which sub-objects to include
    # - efficient fetching of sub-documents (the normal use in Django)

    # Subdocuments (ForeignKey field pointing to other model)
    select_related = []

    # To support OneToMany and ManyToMany (ForeignKey pointing to us)
    # These will result in lists of documents
    prefetch_related = []

    # Whether or not to include a '_model' attribute
    add_model_name = False

    # Dictionaries that will be passed to the corresponding QuerySet methods
    # in the default DocumentCollection.queryset()
    # WARNING: Be very careful when relying on these!
    #          Suppose you filter on foo=42. If you change the foo field
    #          to another value, the object will no longer be included in
    #          the queryset and no deleted signal (and not even changed)
    #          will alert you to the fact that this object dropped out of
    #          the collection!
    #          It's best to avoid any filtering here, unless you understand
    #          the limitations and edge cases.
    # TODO:    See if we can fix this
    # FIXME:   Even worse, AggregateCollections will not get updated when this happens!
    # TODO:    Write tests for edge cases.
    queryset_filter = None
    queryset_exclude = None

    def __init__(self):
        if self.model is None:
            raise NotImplementedError("Document.model not set")
        if not self.name:
            self.name = self.model._meta.db_table

    def _split_selectors(self, selectors, path):
        """Splits a Django-style '__'-delimited object path into tuples,
        and strips the given path off.
        """
        for sel in selectors:
            p = sel.split('__')
            level = len(path)
            subp = p[level:]
            if subp:
                if p[:level] == path:
                    yield subp

    def _fk_fields_to_follow(self, path):
        names = set(x[0] for x in self._split_selectors(self.select_related, path))
        log.debug("    _fk_fields_to_follow for %s: %s", '__'.join(path), ' '.join(names))
        return names

    def _excluded_for_path(self, path):
        excluded = set(
            x[0] for x in self._split_selectors(self.exclude, path)
            # Specific matches (otherwise it affects a field on a subdocument)
            if len(x) == 1
        )
        return excluded | set(self.exclude_all)

    def get_related_models(self):
        """
        Determine on which models the return data might depend, and the query
        to determine the affected objects

        @@@ TODO: move this example to the class doc string

        Consider the following situation::

         * Our root collection is based on the model `Book`
         * The model `Chapter` has a `book` field pointing to a `Book`
         * The `Book` has a `publisher` field pointing to a `Publisher`
         * There is an `Author` model with a many-to-many relationship with
           `Book` through `Book.authors`

        The document declaration will contain the following::

            select_related = ['publisher']
            prefetch_related = ['chapter_set', 'authors']

        When a Chapter is added or updated, the affected book collections
        can be found using the following query::

            affected_books_1 = Book.objects.filter(publisher=publisher)
            affected_books_2 = Book.objects.filter(chapter_set=chapter)
            affected_books_3 = Book.objects.filter(authors=author)

        This also works over a '__' separated path. The nice thing here is
        that we do not need to perform extra work to determine the query
        filters.

        The return value for the book collection would be::

            {
                'chapter':   {'direct': False,
                              'm2m': False,
                              'model': <class 'Chapter'>,
                              'path': 'chapter_set'
                },
                'publisher': {'direct': True,
                              'm2m': False,
                              'model': <class 'Publisher'>,
                              'path': 'publisher__links'
                },
                'authors': {  'direct': True,
                              'model': <class 'Author'>,
                              'path': 'authors',
                              'through': <class 'Book_authors'>
                }
            }

        """
        model_info = {}
        for pathstring in self.select_related + self.prefetch_related:
            model = self.model
            # If the related_name is not set, the filter_path will contain
            # 'chapter' and the accessor attribute and what we pass to
            # prefetch_related will be 'chapter_set', se this is not always
            # the same as the passed pathstring...
            filter_path = []
            for accessor in pathstring.split('__'):
                log.debug("get_related_models: %s (%s)", pathstring , accessor)
                # Most of the time these are equal
                fieldname = accessor
                info = {}

                # Get field info
                # TODO: show list of valid names if the field is invalid
                try:
                    field, field_model, direct, m2m = \
                        model._meta.get_field_by_name(fieldname)
                except models.FieldDoesNotExist:
                    if accessor.endswith('_set'):
                        # If no related_name is specified, the field name will
                        # be 'foo', while the queryset is accessible through
                        # 'foo_set'. If the related_name has been set, these
                        # will be the same.
                        fieldname = accessor[:-4] # strip '_set'
                        field, field_model, direct, m2m = \
                            model._meta.get_field_by_name(fieldname)
                    else:
                        raise

                # We want to get the next model in our iteration
                if direct and not m2m:
                    # (<related.ForeignKey: publisher>, None, True, False)
                    model = field.related.parent_model
                elif direct and m2m:
                    # (<related.ManyToManyField: authors>, None, True, True)
                    # (<related.ManyToManyField: tags>, None, True, True)
                    model = field.rel.to
                    info['through'] = field.rel.through
                elif not direct and not m2m:
                    # (<RelatedObject: tests:extrabookinfo related to book>, None, False, False)
                    # (<RelatedObject: tests:chapter related to book>, None, False, False)
                    # (<RelatedObject: tests:publisherlink related to publisher>, None, False, False)
                    model = field.model
                elif not direct and m2m:
                    # (<RelatedObject: tests:category related to books>, None, False, True)
                    model = field.model
                    info['through'] = field.field.rel.through
                else:
                    # Cannot happen, we covered all four cases
                    raise AssertionError("Impossible")

                log.debug("get_related_models: %s (%s) => %s",
                    pathstring , accessor, model.__name__)

                # We also store all intermediate paths # FIXME: include in tests
                filter_path.append(fieldname)
                filter_pathstring = '__'.join(filter_path)
                info['model'] = model
                info['path'] = pathstring
                info['m2m'] = m2m
                info['direct'] = direct
                model_info[filter_pathstring] = info

        return model_info

    def queryset(self, prefetch=True):
        qs = self.model.objects
        if prefetch and self.select_related:
            qs = qs.select_related(*self.select_related)
        if prefetch and self.prefetch_related:
            qs = qs.prefetch_related(*self.prefetch_related)
        if self.queryset_filter:
            qs = qs.filter(**self.queryset_filter)
        if self.queryset_exclude:
            qs = qs.exclude(**self.queryset_exclude)
        return qs.all()

    def dump_collection(self):
        for obj in self.queryset():
            yield self.dump(obj)

    def dump_id(self, root_pk):
        return self.dump(self.model.objects.get(pk=root_pk))

    def dump(self, root_obj):
        if not isinstance(root_obj, self.model):
            raise ValueError("root_obj is not an instance of self.model")
        return self.dump_obj(self.model, root_obj, path=[])

    def dump_obj(self, model, obj, path):
        # TODO: Add follow_extra=[] param
        # TODO: Refactor this code. I'm not happy with how relations are
        #       handled here.

        if obj is None:
            return None
        if not isinstance(obj, model):
            raise ValueError("obj is not an instance of model")

        log.debug("dump_obj for %s %s, path '%s'",
            model.__name__, obj.pk, '__'.join(path))

        # Create a meta field mapping
        meta = obj._meta
        fields = meta.fields
        fieldmap = {}
        for field in fields:
            fieldmap[field.name] = field

        # Filter the fields based on user preferences
        excluded = self._excluded_for_path(path)
        selected_fields = set(fieldmap.keys()) - excluded
        selected_fields = self.filter_fields(model, selected_fields)

        # Build the output dictionary
        data = {}
        for fieldname in selected_fields:
            field = fieldmap[fieldname]
            try:
                value = self.value_for_field(model, obj, field, path)
            except Skip:
                pass
            else:
                if isinstance(value, MultipleValues):
                    # This allows the method to rename the field or
                    # set multiple fields in the output dict.
                    for key, val in value.items():
                        data[key] = val
                else:
                    # Simply set the value
                    data[fieldname] = value

        # Class name
        if self.add_model_name:
            data['_model'] = model._meta.app_label + ':' + model.__name__

        # Find reverse OneToOneField relations (they do not appear in fields)
        # TODO: merge this with the next block
        for fieldname in self._fk_fields_to_follow(path):
            if fieldname in data:
                # Probably a ForeignKey that was already dumped
                continue
            try:
                field = getattr(obj, fieldname)
                if isinstance(field, models.Model):
                    reldoc = self.dump_obj(field.__class__, field,
                        path + [fieldname])
                    data[fieldname] = reldoc
            except models.ObjectDoesNotExist:
                # It's probably a OneToOneField, but the relation does not
                # exist. Ignoring this seems nicer than crashing.
                # TODO: decide whether crashing is the desired behavior here
                pass

        # Follow allowed relations
        included_relations = set(x[0] for x in
            self._split_selectors(self.prefetch_related, path))
        log.debug("  included_relations = %r", included_relations)
        m2one = dict((x[0].var_name, x[0]) for x in meta.get_all_related_objects_with_model())
        m2m = dict((x[0].var_name, x[0]) for x in meta.get_all_related_m2m_objects_with_model())
        for relname in included_relations:
            # If the related_name is not set, the path will contain 'chapter' and
            # the accessor attribute will be 'chapter_set', so we cannot assume
            # these are the same.
            accessor = relname
            if relname in m2one:
                accessor = m2one[relname].get_accessor_name()
            if relname in m2m:
                accessor = m2m[relname].get_accessor_name()

            if accessor in data:
                # Probably a ForeignKey that was already dumped
                continue
            doclist = []
            rel = getattr(obj, accessor)
            for relobj in rel.all():
                try:
                    reldoc = self.dump_obj(relobj.__class__, relobj, path + [relname])
                except Skip:
                    pass
                else:
                    doclist.append(reldoc)
            data[relname] = doclist

        # Allow custom processing on the output dict
        data = self.transform_data(model, obj, data, path)

        return data

    def filter_fields(self, model, fieldnames):
        return fieldnames

    def value_for_field(self, model, obj, field, path):
        log.debug("  value_for_field %s %s %s, path '%s'",
            model.__name__, obj.pk, field.name, '__'.join(path))

        # TODO: Maybe move this check to dump_obj()?
        if isinstance(field, models.ForeignKey):
            # (Note that this also matches OneToOneField, which is a subclass)
            if not field.name in self._fk_fields_to_follow(path):
                # Not following the ForeignKey, only the corresponding
                # fieldname_id field will be set
                id_field = '{0}_id'.format(field.name)
                fields_to_set = {id_field: getattr(obj, id_field)}
                return MultipleValues(fields_to_set)
            else:
                fk_obj = getattr(obj, field.name)
                return self.dump_obj(fk_obj.__class__, fk_obj, path + [field.name])

        value = getattr(obj, field.name)
        return value

    def transform_data(self, model, obj, data, path):
        # Hook for models to influence how they are serialized
        if hasattr(obj, 'denormalize_transform_data'):
            kwargs = dict(path=path, collection=self)
            data = obj.denormalize_transform_data(data, **kwargs)
        return data

    def map_affected(self, ids):
        """Maps a list of ids found to have changed to actual ids that
        need to be updated.

        This is added primarily to implement AggregateCollection, but it
        might allow you to use a different field as an output primary
        key (untested).
        """
        return ids

    def __str__(self):
        return self.name


class AggregateCollection(DocumentCollection):
    """Like DocumentCollection, but for generating aggregates.

    Aggregates are documents that do not have a 1:1 relation to the
    model they are based on, but perform a data transformation.

    The most important difference with a DocumentCollection is that an
    AggregateCollection will regenerate _all_ data whenever _any_ object
    included in the queryset changes.

    Examples for which this class can be used:

     * Creating one document with a tree structure of pages or categories
       to generate a menu.
     * Calculating statistics about data stored in an entire table.
     * Generating an index document, mapping one field to
       the ids of the documents where the field has a certain value.
    """
    # TODO: test this class

    aggregate_keys = ['default']

    def aggregate(self, key):
        """Implement your aggregation here

        :param key: key that will be used for the aggregation. By default
            this is the string 'default'. (See `self.aggregate_keys`)
        :return: dict
        """
        if not key in self.aggregate_keys:
            raise KeyError("Invalid aggregate key: {0}".format(key))

        # This is just an example of how to use this class
        return dict(n_objects=self.queryset(prefetch=False).count())


    # You probably do not need to override anything below here

    def dump_collection(self):
        for key in self.aggregate_keys:
            yield self.aggregate(key)

    def dump_id(self, root_pk):
        return self.aggregate(key=root_pk)

    def map_affected(self, ids):
        # This always maps any affected objects onto the aggregate keys
        # that need to be updated (all of them), unless no objects were
        # affected. The backend will call dump_id() for all the aggregates.
        # FIXME: any type of change should because a 'change', not 'deleted'
        #        or 'added'.
        if not ids:
            return set()
        return set(self.aggregate_keys)

