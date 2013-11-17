import pytest
from bld import (validate_rules, TargetDoesNotExist, CircularReference,
                 AttrMissing, load_bldfile)
from bld.utils import AttrDict, is_execattr


def test_rules_empty():

    with pytest.raises(TargetDoesNotExist):
        rules = {}
        validate_rules(rules, tuple(), AttrDict(verbose=False))


def test_rules_circular_dep():
    'Circular Dependency.'
    rules = {'readme.html': AttrDict(
        me=u'readme.html', deps=u'DUDE.rst readme.html',
    )}
    with pytest.raises(CircularReference):
        validate_rules(rules, tuple(), AttrDict(verbose=False))


def test_at_least_one_exec_attr():
    data = '''
[readme.html]
deps = readme.rst
exec.sh = echo %deps
'''
    rules, _ = load_bldfile(None, from_string=data)
    assert [ k for k in rules['readme.html'].keys() if is_execattr(k) ]


def test_at_least_one_attr_neg():
    rules = {'readme.html': AttrDict(myfile=u'DUDE.rst')}
    with pytest.raises(AttrMissing):
        validate_rules(rules, tuple(), AttrDict(verbose=False))

