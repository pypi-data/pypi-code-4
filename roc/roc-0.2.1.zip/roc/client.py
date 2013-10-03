from .remote import RemoteModule


def server_proxy(host='127.0.0.1', port=8000):
    try:
        from xmlrpclib import ServerProxy
    except ImportError:
        from xmlrpc.client import ServerProxy
    return ServerProxy(
        "http://%s:%d/" % (host, port),
        allow_none=True
    )


def remote_module(proxy):
    return RemoteModule(proxy)
