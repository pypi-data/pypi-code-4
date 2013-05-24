from contextlib import contextmanager
from threading import local
import time

import logging
log = logging.getLogger(__name__)


queue_context = local()

class _Context(object):
    previous_context = None
    # These are sets of (backend, collection, doc_id)
    added = None
    changed = None
    deleted = None
    t0 = 0

    def __init__(self):
        self.added = dict()
        self.changed = dict()
        self.deleted = dict()

    def flush(self):
        log.debug("flushing...")
        # NOTE: here we make assumptions about the order in events happen.
        # We do not keep track of the order in which they happen, so we assume
        # the following events happened in the following order:
        # - added, changed -> added
        # - deleted, added -> same (we do not support the other way around!)
        # - changed, deleted -> deleted
        # - deleted, added, changed -> deleted, added
        # TODO: write test cases for this
        for backend, collection, doc_id in self.deleted.values():
            log.debug("flushing deleted: %s %s %s", backend, collection.name, doc_id)
            backend._call_deleted(collection, doc_id)
        for backend, collection, doc_id in self.added.values():
            log.debug("flushing added: %s %s %s", backend, collection.name, doc_id)
            backend._call_added(collection, doc_id)
        for key, value in self.changed.items():
            backend, collection, doc_id = value
            if key in self.added:
                log.debug("ignoring changed, because added: %s %s %s",
                    backend, collection.name, doc_id)
            elif key in self.deleted:
                log.debug("ignoring changed, because deleted (and not added): %s %s %s",
                    backend, collection.name, doc_id)
            else:
                log.debug("flushing changed: %s %s %s", backend, collection.name, doc_id)
                backend._call_changed(collection, doc_id)
        log.debug("flushed")

class ContextMissingException(RuntimeError):
    pass


def get_current_context():
    return getattr(queue_context, 'context', None)


def _enter():
    current_context = getattr(queue_context, 'context', None)
    new_context = _Context()
    new_context.previous_context = current_context
    new_context.t0 = time.time()
    queue_context.context = new_context
    log.debug('Entering context %s', id(new_context))


def _exit(flush=True, force_flush=False):
    current_context = getattr(queue_context, 'context', None)
    if current_context is None:
        raise ContextMissingException("Cannot unwind context")
    t1 = time.time()
    dt = (t1 - current_context.t0) * 1000
    log.debug('Exiting context %s (entire context took %.1f ms)',
              id(current_context), dt)
    if flush and (force_flush or current_context.previous_context is None):
        current_context.flush()
        t2 = time.time()
        dt = (t2 - t1) * 1000
        log.debug('Exiting context %s - flushed (flush took %.1f ms)',
            id(current_context), dt)
    queue_context.context = current_context.previous_context


@contextmanager
def delay_sync():
    """Use case one: delay syncs to an outer scope to prevent multiple
    identical syncs"""
    _enter()
    try:
        yield
    except:
        _exit(flush=False)
        raise
    else:
        _exit(flush=True, force_flush=False)

@contextmanager
def sync_together():
    """Use case two: force sync within a content in the presence of an outer
    delay_sync, to make sure the next statements will retrieve up to date data
    """
    _enter()
    try:
        yield
    except:
        _exit(flush=False)
        raise
    else:
        _exit(flush=True, force_flush=True)
