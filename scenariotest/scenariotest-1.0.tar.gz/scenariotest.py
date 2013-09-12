# -*- coding: utf-8 -*-
# Copyright © 2013 by its contributors. See AUTHORS for details.
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
"""
This testing helper-class was taken from a gist written by github user
‘bigjason’. It combines a prototypical test case with a list of dictionaries
(each a dict of keyword arguments) and transforms the two into a series of
unittest-compatible test cases. The advantage of this approach is that an
identical test can be applied to multiple scenarios with minimal repetition
of code, while still having each scenario tested independently and reported
to the user by the test runner.

Example of usage can be found in the file xunit.py, or on
bigjason's blog post which introduced the concept:

    <http://www.bigjason.com/blog/scenario-testing-python-unittest/>

The original code this was based off of can be found on GitHub:

    <https://gist.github.com/856821/8966346d8e50866eae928ababa86acea6504bcee>
"""

# Python 2 and 3 compatibility utilities
import six

VERSION = (1,0,0, 'final', 0)

def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3:] == ('alpha', 0):
        version = '%spre-alpha' % version
    else:
        if VERSION[3] != 'final':
            version = "%s%s" % (version, VERSION[3])
            if VERSION[4] != 0:
                version = '%s%s' % (version, VERSION[4])
    return version

class ScenarioMeta(type):
    def __new__(cls, name, bases, attrs):
        new_attrs = {}

        for name, val in filter(lambda n: isinstance(n[1], ScenarioTestMeta), six.iteritems(attrs)):
            for id, params in enumerate(val.scenarios if not callable(val.scenarios) else val.scenarios()):
                if type(params) in (tuple, list):
                    params, id = params
                # create a unittest discoverable name
                test_name = "test_%s_%s" % (val.__name__, id)
                # Wrap the scenario in a closure and assign the discoverable name.
                new_attrs[test_name] = cls._wrap_test(params, val.__test__)
        attrs.update(new_attrs)
        return super(ScenarioMeta, cls).__new__(cls, name, bases, attrs)

    @staticmethod
    def _wrap_test(kwargs, meth):
        def wrapper(self):
            meth(self, **kwargs)
        return wrapper

class ScenarioTestMeta(type):
    def __new__(cls, name, bases, attrs):
        test_meth = attrs.pop("__test__", None)
        if test_meth:
            # Now that the __test__ method is pulled off the base it can be wrapped
            # as static and rebound. This allows it to be re-composed to the parent
            # test case.
            attrs["__test__"] = staticmethod(test_meth)

        return super(ScenarioTestMeta, cls).__new__(cls, name, bases, attrs)

class ScenarioTest(object):
    __metaclass__ = ScenarioTestMeta
    scenarios = ()
