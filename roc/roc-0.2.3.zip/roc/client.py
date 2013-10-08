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


def wait(proxy, attempts_amount=10, repeat_timout_sec=10):
    for attempt_count in range(attempts_amount):
        if is_online(proxy):
            return True
        else:
            import time
            time.sleep(repeat_timout_sec)
    return False


def is_online(proxy):
    import socket
    try:
        proxy.classes()
        return True
    except socket.error as e:
        if e.errno in (10060, 10061):
            return False
        else:
            raise
