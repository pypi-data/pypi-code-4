"""
Test instance creation.
"""

import shutil
import os

from tiddlywebplugins.imaker import spawn

from testpackage import instance as instance_module
from testpackage.config import config as init_config


class DummyInstanceModule:

    instance_config = {}


def setup_function(fn):
    try:
        shutil.rmtree('testinstance')
    except:
        pass


# NB: must come before `test_spawn` because `spawn` modifies the global
# `tiddlyweb.config`, adding `instance_pkgstores`
def test_spawn_without_pgkstore():
    empty_config = {}
    spawn('testinstance', empty_config, instance_module)

    assert os.path.exists('testinstance/tiddlywebconfig.py')
    assert not os.path.exists('testinstance/store/bags/testbag/tiddlers/testtiddler')


def test_spawn_without_store_structure():
    # NB: `instance_pkgstores` only sensible if `store_structure` exists
    empty_config = {}
    spawn('testinstance', empty_config, DummyInstanceModule())

    assert os.path.exists('testinstance/tiddlywebconfig.py')
    assert os.path.exists('testinstance/store/bags')
    assert len(os.listdir('testinstance/store/bags')) == 0


def test_spawn():
    spawn('testinstance', init_config, instance_module)

    assert os.path.exists('testinstance/tiddlywebconfig.py')
    assert os.path.exists('testinstance/store/bags/testbag/tiddlers/testtiddler')
