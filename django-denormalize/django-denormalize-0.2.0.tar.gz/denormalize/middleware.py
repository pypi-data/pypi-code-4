from .context import _enter, _exit

import logging
log = logging.getLogger(__name__)


class DelaySyncContextMiddleware(object):
    """Middleware to group sync together to prevent multiple syncs of the
    same data. For example, this allows you to make sure that the cache is
    only updated after the database transaction has succeeded, and the same
    object is not rewritten multiple times due to multiple related updates.
    """

    def process_request(self, request):
        _enter()
        request._mw_entered_context = True
        log.debug('Entered context')

    def process_response(self, request, response):
        # In some cases process_request was not executed yet (redirects)
        if getattr(request, '_mw_entered_context', False):
            if response.status_code < 400:
                # Everything OK (commit)
                _exit(flush=True, force_flush=False)
            else:
                # Error, ignore everything (rollback)
                log.info("Response code %s considered an error, not flushing",
                         response.status_code)
                _exit(flush=False)
        else:
            log.debug("Not unwinding context, because never entered one. "
                "(response HTTP code is %s)", response.status_code)
        return response

