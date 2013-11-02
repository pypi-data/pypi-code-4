#
from .go import GoEnvironment
from .py import PyEnvironment
from ..utils import _check_call


def select_runtime(name, options):
    # pyjuju does juju --version
    result = _check_call(["juju", "version"], None, ignoreerr=True)
    if result is None:
        return PyEnvironment(name, options)
    return GoEnvironment(name, options)

