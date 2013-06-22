"""This module contains extentions to the werkzeug Request object."""

from werkzeug.wrappers import Request as WerkzeugRequest

import uuid


class UniqueRequest(WerkzeugRequest):
    """This request type provides a globally unique request id.

    This is intended to assist in tracking/profiling a request through
    multiple middlewares and function calls.

    The id is a random UUID4 that is generated at initialization. It is
    accessible through the `uuid` property of the request. The uuid is already
    cast as a string.
    """

    def __init__(self, *args, **kwargs):

        super(UniqueRequest, self).__init__(*args, **kwargs)

        self.uuid = str(uuid.uuid4())

# Overwrite the original werkzeug request with UniqueRequest
Request = UniqueRequest
