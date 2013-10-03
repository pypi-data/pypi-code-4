from .server import start_server, create_server
from .client import server_proxy, remote_module
from .cli import main


__all__ = (
    start_server,
    create_server,
    server_proxy,
    remote_module,
)


if __name__ == '__main__':
    main()
