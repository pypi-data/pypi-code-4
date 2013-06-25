""" The module sends logs """
import traceback

from ZPublisher.interfaces import IPubAfterTraversal, IPubFailure
from zope.component import adapter

from .config import CRITICAL_RESPONSE_STATUS, TRACEBACK_LIMIT_RECORDS
from .requestutils import is_request_suitable, plain_dict, create_request_info
from .interfaces import ICollectiveErrorDetector
from .memoize import Sender


# set up socket connection and retain it
client = Sender.sendData()


# IPubAfterTraversal is used here because it brings us non-modified
# request (POST). As a result content_length (response.getHeader('content-length'))
# and response_status are excluded from logs. Otherwise, the IPubSuccess should be used.
@adapter(IPubAfterTraversal)
def beforeMapply(event):
    """ Detect and send important requests before they
        will be published by the mapply method.
    """
    request = event.request
    # check if package is installed
    if not ICollectiveErrorDetector.providedBy(request):
        return

    # filter CSS, KSS and other unimportant things
    if not is_request_suitable(request):
        return

    params = request.form
    if request.method == 'POST':
        # remove unsuitable data
        params = plain_dict(params)
    request_info = create_request_info(request, extra_info=params)
    client.send(request_info)


@adapter(IPubFailure)
def requestFailure(event):
    """ Detect and send an error log """
    # check if package is installed
    if not ICollectiveErrorDetector.providedBy(event.request):
        return

    # check an error status
    status = str(event.request.response.getStatus())
    if not status.startswith(CRITICAL_RESPONSE_STATUS):
        return

    error = ''.join(
        traceback.format_exception(
            *event.exc_info,
            limit=TRACEBACK_LIMIT_RECORDS
        )
    )
    request_info = create_request_info(event.request, extra_info=error)
    request_info['status'] = status
    client.send(request_info)
    # close storage and open a new one
    client.send(None)
