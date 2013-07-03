""" The module creates constants """

from logging.handlers import DEFAULT_TCP_LOGGING_PORT


INITIALIZATION = """
import logging
logging.basicConfig(
    format="%(levelname)s %(asctime)s %(filename)s %(message)s",
    level=logging.ERROR,
)
"""

SCRIPT_ARGUMENTS = """
        # additional arguments (eg: start)
        sys.argv,
        # script settings
        ip='%(ip)s',
        port=%(port)s,
        main_dir='%(main_dir)s',
        # storage settings
        maxlen=%(maxlen)s,    # buffer size
        mode=%(mode)s,
        format='%(format)s',
        # subfolder to main_dir. Logs will be saved there
        storage_dir='%(storage_dir)s',
"""

# define the default params
DEFAULT_OPTIONS = {
    # script settings
    'ip': 'localhost',
    'port': DEFAULT_TCP_LOGGING_PORT,
    # storage settings
    'maxlen': 100,    # buffer size (100 items)
    'mode': None,
    'format': 'json',
}
