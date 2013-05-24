import time
import threading
from .base import BackendBase

import logging
log = logging.getLogger(__name__)

class SyncInProgress(RuntimeError):
    pass


class LocMemBackend(BackendBase):
    # All documents are stored in this dict
    # data[collection_name][object_id] = document
    data = None

    # Used to keep collections that are currently being synced consistent,
    # even if an update happens during dump_collection.
    # WARNING: This still does not cover all possible race conditions,
    #          especially not if database transactions are enabled!
    _dirty = None
    _lock = None

    def __init__(self, name=None):
        super(LocMemBackend, self).__init__(name=name)
        self.data = {}
        self._dirty = {}
        self._lock = threading.Lock()

    def deleted(self, collection, doc_id):
        log.debug('deleted: %s %s', collection.name, doc_id)
        with self._lock:
            coldata = self.data.setdefault(collection.name, {})
            try:
                del coldata[doc_id]
            except KeyError:
                pass
            else:
                self._mark_dirty(collection.name, doc_id)

    def added(self, collection, doc_id, doc):
        log.debug('added: %s %s', collection.name, doc_id)
        with self._lock:
            coldata = self.data.setdefault(collection.name, {})
            coldata[doc_id] = doc
            self._mark_dirty(collection.name, doc_id)

    def changed(self, collection, doc_id, doc):
        log.debug('changed: %s %s', collection.name, doc_id)
        with self._lock:
            coldata = self.data.setdefault(collection.name, {})
            coldata[doc_id] = doc
            self._mark_dirty(collection.name, doc_id)

    def _mark_dirty(self, collection_name, doc_id):
        if collection_name in self._dirty:
            try:
                self._dirty[collection_name].add(doc_id)
            except KeyError:
                pass

    def get_doc(self, collection, doc_id):
        return self.data[collection.name][doc_id]

    _sync_collection_before_handling_dirty = None # method

    def sync_collection(self, collection):
        log.info("Starting full sync for collection %s", collection.name)
        t0 = time.time()

        # TODO: there is a slight race condition here
        if collection.name in self._dirty:
            log.error("There is already a full sync running for collection %s!",
                collection.name)
            raise SyncInProgress("There is already a sync in progress")

        docs = {}
        has_lock = False
        try:
            # Lock collection for sync
            # This will make all the signal handlers register all changes
            # crom now on. We want updates to continue, because this can
            # take a long time, and we do not want to block other code.
            self._dirty[collection.name] = set()
            for doc in collection.dump_collection():
                docs[doc['id']] = doc

            # Used for testing only
            if self._sync_collection_before_handling_dirty is not None:
                self._sync_collection_before_handling_dirty()

            # Now handle the changes that occurred during the full dump.
            # We will acquire a long for this update, as it only touches
            # local memory and will be very fast.
            dirty_ids = self._dirty[collection.name]
            log.info("%i dirty objects for collection %s",
                len(dirty_ids), collection.name)

            # Lock the data during this update
            has_lock = True
            self._lock.acquire()

            for doc_id in dirty_ids:
                # Patch up new data with updated local data
                doc = self.data[collection.name].get(doc_id, None)
                if doc:
                    docs[doc_id] = doc
                elif doc_id in docs:
                    del docs[doc_id]

            # Now overwrite the current collection data
            self.data[collection.name] = docs

        finally:
            # Unlock
            del self._dirty[collection.name]
            if has_lock:
                self._lock.release()
            t1 = time.time()
            log.info("Full sync for collection %s completed in %.3fs",
                collection.name, t1-t0)

