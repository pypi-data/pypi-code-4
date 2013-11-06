from server import Server, Scheduler

def make_server(path, host='127.0.0.1', port=22972, serverClass=Server):
    # code borrowed from xdserver.server
    scheduler = Scheduler()
    server = serverClass(
        scheduler=scheduler,
        path=path,
        host=host,
        port=int(port)
        )
    scheduler.add(server.dispatch)
    return scheduler

