#
from .go import GoEnvironment
from .py import PyEnvironment
from ..utils import _check_call


def select_runtime(env_name):
    # pyjuju does juju --version
    result = _check_call(["juju", "version"], None, ignoreerr=True)
    if result is None:
        return PyEnvironment(env_name)
    return GoEnvironment(env_name)
