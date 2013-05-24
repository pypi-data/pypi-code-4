import weakref

from django.db.models import signals

from ..context import get_current_context

import logging
from denormalize.models import DocumentCollection

log = logging.getLogger(__name__)


class BackendBase(object):

    collections = None

    # Keep references to listeners to prevent garbage collection
    _listeners = None

    # This will be shared by all subclasses. It keeps track of all active
    # backends.
    _registry = weakref.WeakValueDictionary()

    def __init__(self, name=None):
        """

        :param name: Name for backend instance. This is used to refer to
            the backend instance from management commands. If not given,
            a name will be generated based on the id().
        :type name:
        :return:
        :rtype:
        """
        if name is None:
            name = '_{0}'.format(id(self))
        if name in self._registry:
            raise ValueError("A backend with name '{0}' has already been "
                "registered. Please pass another 'name' during "
                "initialization.".format(name))
        self._registry[name] = self
        self.collections = {}
        self._listeners = []

    def register(self, collection):
        """
        :type collection: denormalize.models.DocumentCollection
        :return:
        :rtype:
        """
        if collection.name in self.collections:
            raise ValueError("A collection with name '{0}' has already "
                "been registered to this backend.".format(collection.name))
        self.collections[collection.name] = collection
        self._setup_listeners(collection)

    def _get_collection(self, collection_name_or_obj):
        if isinstance(collection_name_or_obj, DocumentCollection):
            name = collection_name_or_obj.name
        elif isinstance(collection_name_or_obj, basestring):
            name = collection_name_or_obj
        else:
            raise KeyError("Invalid collection specified")
        # Can raise KeyError
        return self.collections[name]

    def _setup_listeners(self, collection):
        """
        :type collection: denormalize.models.DocumentCollection
        """
        dependencies = collection.get_related_models()
        self._add_listeners(collection, None, collection.model, None)
        for filter_path, info in dependencies.items():
            self._add_listeners(collection, filter_path, info['model'], info)

    def _add_listeners(self, collection, filter_path, submodel, info):
        """Connect the Django ORM signals to given dependency

        :type collection: denormalize.models.DocumentCollection
        :param filter_path: ORM filter path (not always the same as the
            path used in *_related! For example, 'chapter' instead of
            'chapter_set'!)
        :type filter_path: basestring, None
        :param submodel: dependency model to watch for changes
        :type submodel: django.db.models.Model
        :param info: dict as returned by `DocumentCollection.get_model_info`
        :type info: dict, None
        """
        # TODO: this does not handle changing foreignkeys well. The object
        #       will be added to the new root, but not deleted from the old
        #       root object. Maybe solve by also adding a pre_save? The
        #       database will still contain the old connection.
        # TODO: Consider moving all of this to a Collection or something
        #       separate and just listen to signals from there.

        def pre_save(sender, instance, raw, **kwargs):
            # Used to detect FK changes
            created_guess = not instance.pk
            log.debug('pre_save: collection %s, %s (%s) with id %s %s',
                collection.name, submodel.__name__, filter_path or '^',
                instance.id, 'added' if created_guess else 'changed')

            # From the Django docs: "True if the model is saved exactly as
            # presented (i.e. when loading a fixture). One should not
            # query/modify other records in the database as the database
            # might not be in a consistent state yet."
            if raw:
                log.warn("pre_save: raw=True, so no document sync performed!")
                return

            # We only need this to monitor FK *changes*, so no need to do
            # anything for new objects.
            if created_guess:
                log.debug("pre_save:   looks new, no action needed")
                return

            # Find all affected root model instance ids
            # These are the objects that reference the changed instance
            if filter_path:
                # Submodel only
                filt = {filter_path: instance}
                affected = set(collection.queryset(prefetch=False).filter(
                    **filt).values_list('id', flat=True))
                log.debug("pre_save:   affected documents: %r", affected)

                # Instead of calling the update functions directly, we make
                # sure it is queued for after the operation. Otherwise
                # the changes are not reflected in the database yet.
                instance._denormalize_extra_affected = affected


        def post_save(sender, instance, created, raw, **kwargs):
            log.debug('post_save: collection %s, %s (%s) with id %s %s',
                collection.name, submodel.__name__, filter_path or '^',
                instance.id, 'created' if created else 'changed')

            # From the Django docs: "True if the model is saved exactly as
            # presented (i.e. when loading a fixture). One should not
            # query/modify other records in the database as the database
            # might not be in a consistent state yet."
            if raw:
                log.warn("post_save: raw=True, so no document sync performed!")
                return

            # Find all affected root model instance ids
            # These are the objects that reference the changed instance
            if filter_path:
                # Submodel
                filt = {filter_path: instance}
                affected = set(collection.queryset(prefetch=False).filter(
                    **filt).values_list('id', flat=True))
            else:
                # This is the root model
                affected = set([instance.id])
            log.debug("post_save:   affected documents: %r", affected)

            # This can be passed by the pre_save handler
            extra_affected = getattr(instance, '_denormalize_extra_affected', None)
            if extra_affected:
                affected |= extra_affected

            if filter_path or not created:
                for doc_id in collection.map_affected(affected):
                    self._queue_changed(collection, doc_id)
            else:
                for doc_id in collection.map_affected(set([instance.id])):
                    self._queue_added(collection, doc_id)


        def pre_delete(sender, instance, **kwargs):
            log.debug('pre_delete: collection %s, %s (%s) with id %s being deleted',
                collection.name, submodel.__name__, filter_path or '^',
                instance.id)

            # Find all affected root model instance ids
            # These are the objects that reference the changed instance
            if filter_path:
                # Submodel
                filt = {filter_path: instance}
                affected = set(collection.queryset(prefetch=False).filter(
                    **filt).values_list('id', flat=True))
            else:
                # This is the root model
                affected = set([instance.id])
            log.debug("pre_delete:   affected documents: %r", affected)

            # Instead of calling the update functions directly, we make
            # sure it is queued for after the operation. Otherwise
            # the changes are not reflected in the database yet.
            instance._denormalize_deleted = affected


        def post_delete(sender, instance, **kwargs):
            log.debug('post_delete: collection %s, %s (%s) with id %s was deleted',
                collection.name, submodel.__name__, filter_path or '^',
                instance.id)
            affected = getattr(instance, '_denormalize_deleted', set())
            if filter_path:
                for doc_id in collection.map_affected(affected):
                    self._queue_changed(collection, doc_id)
            else:
                for doc_id in collection.map_affected(set([instance.id])):
                    self._queue_deleted(collection, doc_id)


        def m2m_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
            # An m2m change affects both sides: if an Author is added to a Book,
            # the Author will also have a new book on its side. It does not
            # matter however in which direction we are looking at this relation,
            # since any check on the instance passed will lead us to the root
            # object that must be marked as changed.

            # Opposite side of `model`
            instance_model = instance.__class__

            # FIXME: debug level
            log.info('m2m_changed: collection %s, %s (%s) with %s.id=%s m2m '
                '%s on %s side (reverse=%s), pk_set=%s',
                collection.name, submodel.__name__, filter_path or '^',
                instance_model.__name__,
                instance.id, action, model.__name__, reverse, pk_set)

            # Optimization: if either side is our root object, send out changes
            # without querying.
            if instance_model is collection.model:
                self._queue_changed(collection, instance.id)
                return

            elif model is collection.model and pk_set:
                for pk in pk_set:
                    self._queue_changed(collection, pk)
                return

            # Otherwise figure out which side is equal to the model we are
            # registering handlers for, and use that for querying.
            if instance_model is submodel:
                filt = {filter_path: instance}
                affected = set(collection.queryset(prefetch=False).filter(
                    **filt).values_list('id', flat=True))
                for doc_id in collection.map_affected(affected):
                    self._queue_changed(collection, doc_id)
                return

            elif model is submodel and pk_set:
                # FIXME: this is wrong! setting tags does not affect all other
                #        book that have the same tag!
                filt = {'{0}__pk__in'.format(filter_path): pk_set}
                affected = set(collection.queryset(prefetch=False).filter(
                    **filt).values_list('id', flat=True))
                for doc_id in collection.map_affected(affected):
                    self._queue_changed(collection, doc_id)
                return

            # FIXME: how to handle the clear signals (pre and post) in this form?
            # Tag (publisher__tags) with Publisher.id=1 m2m pre_clear on Tag side (reverse=False), pk_set=None
            # We don't have any ID for Tag, only for the other side
            # --> strip last item from filter path

            # The type of action does not matter, we simply do a lookup for
            # given model and
            #affected = getattr(instance, '_denormalize_m2m_affected', set())
            #if filter_path:
            #    for doc_id in collection.map_affected(affected):
            #        self._queue_changed(collection, doc_id)
            #else:
            #    for doc_id in collection.map_affected(set([instance.id])):
            #        self._queue_deleted(collection, doc_id)


        # We need to keep a reference, because signal connections are weak
        self._listeners.append(pre_save)
        self._listeners.append(post_save)
        self._listeners.append(pre_delete)
        self._listeners.append(post_delete)
        # Connect to the save signal
        signals.pre_save.connect(pre_save, sender=submodel)
        signals.post_save.connect(post_save, sender=submodel)
        signals.pre_delete.connect(pre_delete, sender=submodel)
        signals.post_delete.connect(post_delete, sender=submodel)
        # M2M handling
        if info and info['m2m']:
            self._listeners.append(m2m_changed)
            signals.m2m_changed.connect(m2m_changed, sender=info['through'])

    def _queue_deleted(self, collection, doc_id):
        """Queue a deleted notification"""
        context = get_current_context()
        if context is not None:
            log.debug("Queued delete for %s %s", collection, doc_id)
            key = u'{0}-{1}-{2}'.format(id(self), id(collection), doc_id)
            context.deleted[key] = (self, collection, doc_id)
        else:
            self._call_deleted(collection, doc_id)

    def _queue_added(self, collection, doc_id):
        """Queue an added notification"""
        context = get_current_context()
        if context is not None:
            log.debug("Queued add for %s %s", collection, doc_id)
            key = u'{0}-{1}-{2}'.format(id(self), id(collection), doc_id)
            context.added[key] = (self, collection, doc_id)
        else:
            self._call_added(collection, doc_id)

    def _queue_changed(self, collection, doc_id):
        """Queue a changed notification"""
        context = get_current_context()
        if context is not None:
            log.debug("Queued change for %s %s", collection, doc_id)
            key = u'{0}-{1}-{2}'.format(id(self), id(collection), doc_id)
            context.changed[key] = (self, collection, doc_id)
        else:
            self._call_changed(collection, doc_id)

    def _call_deleted(self, collection, doc_id):
        self.deleted(collection, doc_id)
        # TODO: signals

    def _call_added(self, collection, doc_id):
        doc = collection.dump_id(doc_id)
        self.added(collection, doc_id, doc)
        # TODO: signals

    def _call_changed(self, collection, doc_id):
        doc = collection.dump_id(doc_id)
        self.changed(collection, doc_id, doc)
        # TODO: signals


    # Implement these for your backend. The code above will call these with
    # ORM updates you need to commit to the backend.

    def deleted(self, collection, doc_id):
        """Called when the root object for a document was deleted in the Django ORM"""
        raise NotImplementedError()

    def added(self, collection, doc_id, doc):
        """Called when the root object for a document was added in the Django ORM"""
        raise NotImplementedError()

    def changed(self, collection, doc_id, doc):
        """Called when any data in a document was changed in the Django ORM"""
        raise NotImplementedError()

    def get_doc(self, collection, doc_id):
        """Fetch data from a collection (if supported by the backend))"""
        raise NotImplementedError()

    def sync_collection(self, collection):
        """Sync all data in the collections from the ORM to the backend

        This does not make sense for all backends.
        """
        raise NotImplementedError()

