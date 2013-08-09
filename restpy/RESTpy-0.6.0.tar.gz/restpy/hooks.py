import uuid


def unique_request(request):
    """Assignes a UUID to the request.

    This hook will first look in the environ for a UUID. If found, it will
    assign that UUID to the request object. If not found it will create a
    new UUID for the request.
    """

    request.uuid = request.environ.get('uuid', str(uuid.uuid4()))
