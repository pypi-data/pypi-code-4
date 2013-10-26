from passta.cli.get import do_get
from passta.cli.list import do_list
from passta.cli.remove import do_remove
from passta.cli.store import do_store


commands = {
    'get': do_get,
    'list': do_list,
    'remove': do_remove,
    'store': do_store,
}
