from .server import start_server, create_server
from .client import server_proxy, remote_module, is_online
from .cli import main


__all__ = (
    start_server,
    create_server,
    server_proxy,
    remote_module,
    is_online,
)


if __name__ == '__main__':
    main()
