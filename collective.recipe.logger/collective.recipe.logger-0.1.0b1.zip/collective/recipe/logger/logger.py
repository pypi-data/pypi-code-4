""" The module defines loggers """
from .utils import id_generator
from .storage import PersistentDeque

from multiprocessing.connection import Listener


def objectLogger(params):
    """ Send data (dict, str, ...) into a storage """
    mode = params['mode']
    maxlen = params['maxlen']
    file_format = params['format']
    home_dir = params['storage_dir']
    server = Listener((params['ip'], int(params['port'])))
    storage = PersistentDeque(
        home_dir=home_dir,
        maxlen=maxlen,
        file_format=file_format,
        mode=mode,
    )
    while True:
        conn = server.accept()
        while True:
            try:
                data = conn.recv()
            except EOFError:
                break
            if data:
                storage.append(data)
            else:
                storage.sync(id_generator())
                storage = PersistentDeque(
                    home_dir=home_dir,
                    maxlen=maxlen,
                    file_format=file_format,
                    mode=mode,
                )
        conn.close()
