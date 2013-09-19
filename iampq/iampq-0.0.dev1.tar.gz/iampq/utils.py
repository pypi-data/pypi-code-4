from uuid import uuid4

def uuid():
    """Generate a unique id, having - hopefully - a very small chance of
    collision.

    For now this is provided by :func:`uuid.uuid4`.
    """
    return str(uuid4())

def gen_queue_name():
    return 'IOGAME-%s' % (uuid(), )
