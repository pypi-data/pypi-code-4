# -*- coding: utf-8 -*-
#
# src/configviper/tests.py
# https://bitbucket.org/danielgoncalves/configviper
#
# ConfigViper  Copyright (C) 2012  Daniel Gonçalves <daniel@base4.com.br>
#
# This file is part of ConfigViper.
#
# ConfigViper is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as 
# published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.
#
# ConfigViper is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ConfigViper. If not, see <http://www.gnu.org/licenses/>.
#

"""ConfigViper's tests module."""

import datetime
import decimal
import json
import os
import unittest

import converters

from configviper import ConfigViper
from configviper import PathOverrun


class TestConverters(unittest.TestCase):
    """Test conversions for all built-in converters."""
    
    def test_converter(self):
        """Default converter should return the value without changes in both
        directions, to python and to json, as-is."""
        converter = converters.Converter()

        # assert standard types
        value_str = 'The quick brown fox jumps over the lazy dog.'
        value_int = 1973
        value_float = 3.1415
        value_bool = True

        self.assertEqual(
                converter.to_json(value_str), 
                converter.to_python(value_str))

        self.assertEqual(
                converter.to_json(value_int), 
                converter.to_python(value_int))

        self.assertEqual(
                converter.to_json(value_float), 
                converter.to_python(value_float))

        self.assertEqual(
                converter.to_json(value_bool), 
                converter.to_python(value_bool))

        # assert boolean values
        self.assertTrue(converter.to_python(converter.to_json(True)))
        self.assertFalse(converter.to_python(converter.to_json(False)))


    def test_date_converter(self):
        """Date converter should convert a python ``datetime.date`` object to a
        string formatted as ``yyyy-mm-dd`` which is clearly understandable and
        can be easily editable.
        """
        converter = converters.DATE_CONVERTER

        # assert a simple date value
        value = datetime.date(year=1973, month=9, day=27)
        self.assertEqual('1973-09-27', converter.to_json(value))
        self.assertEqual(value, converter.to_python('1973-09-27'))
        
        # assert a leap year date
        value = datetime.date(year=2012, month=2, day=29)
        self.assertEqual('2012-02-29', converter.to_json(value))
        self.assertEqual(value, converter.to_python('2012-02-29'))

        # assert date with month and day with one digit;
        # month and day should have a trailing zero
        value = datetime.date(year=2012, month=1, day=1)
        self.assertEqual('2012-01-01', converter.to_json(value))
        self.assertEqual(value, converter.to_python('2012-01-01'))


    def test_time_converter(self):
        """Time converter should convert a python ``datetime.time`` object to a
        string formatted as ``hh:MM:ss`` which is clearly understandable and can
        be easily editable.
        """
        converter = converters.TIME_CONVERTER

        # assert a simple time value
        value = datetime.time(14, 5, 17)
        self.assertEqual('14:05:17', converter.to_json(value))
        self.assertEqual(value, converter.to_python('14:05:17'))


    def test_datetime_converter(self):
        """Date/Time converter should convert a Python ``datetime.datetime``
        object to a string formatted as ``yyyy-mm-dd hh:MM:ss`` which is
        clearly understandable and can be easily editable.
        """
        converter = converters.DATETIME_CONVERTER

        # assert a simple date/time value (leap year)
        value = datetime.datetime(2012, 2, 29, 13, 37, 54)
        self.assertEqual('2012-02-29 13:37:54', converter.to_json(value))
        self.assertEqual(value, converter.to_python('2012-02-29 13:37:54'))


    def test_decimal_converter(self):
        """Decimal converter should convert a Python ``decimal.Decimal`` object
        to a string by simple calling ``str`` function on it.
        """
        converter = converters.DECIMAL_CONVERTER

        # assert a simple value
        value = decimal.Decimal('123.79')
        self.assertEqual(str(value), converter.to_json(value))
        self.assertEqual(value, converter.to_python(str(value)))


class TestConfigStabilization(unittest.TestCase):
    """Configuration stabilization is a way to ensure that a config file
    have, at least, the config-paths expected by the host application.
    After stabilization, existing config-paths should return their current 
    values.
    """

    def setUp(self):
        """Mockup a JSON file for these fixtures."""
        # config-paths:
        #       "foo.bar.baz"
        #       "foo.bar.fog"
        mockup = {
            'foo': {
                'bar': {
                    'baz': 4,
                    'fog': 3.15
                }
            }
        }

        self._cfg_filename = 'test-stab.json'
        with open(self._cfg_filename, 'wb') as f:
            f.write(json.dumps(mockup, sort_keys=True, indent=4))

        ConfigViper.configure(
                pathname='.', 
                filename=self._cfg_filename)


    def test_stabilization(self):
        """
        """
        conf = ConfigViper()
        conf.stabilize((
                ('foo.bar.bog', 123, None),
                ('foo.bar.cog', 7.77, None),
                ('foo.bar.biz', 'viper', None),

                # below are config-paths with their default values;
                # note that these config-paths already exists in the
                # configuration file and should not be overwritten
                ('foo.bar.baz', 18, None),
                ('foo.bar.fog', 15.7, None),))

        # assert each path set on stabilization
        self.assertEqual(123, conf.get('foo.bar.bog'))
        self.assertEqual(7.77, conf.get('foo.bar.cog'))
        self.assertEqual('viper', conf.get('foo.bar.biz'))

        # already existing config-paths should not be overwritten during
        # stabilization; existing config-paths should be left with their
        # current values
        self.assertEqual(4, conf.get('foo.bar.baz'))
        self.assertEqual(3.15, conf.get('foo.bar.fog'))


    def tearDown(self):
        if os.path.exists(self._cfg_filename):
            os.unlink(self._cfg_filename)


class TestConfigGetSet(unittest.TestCase):
    """Test get/set config-paths on various Python types, and using all
    built-in converters.
    """

    def setUp(self):
        self._cfg_filename = 'test-getset.json'

        ConfigViper.configure(
                pathname='.', 
                filename=self._cfg_filename)

        # ensure file do not exists
        if os.path.exists(self._cfg_filename):
            os.unlink(self._cfg_filename)


    def test_set_get_default_json_types(self):
        """Set value types JSON can handle by default."""

        conf = ConfigViper()
        conf.set('type.int', 1357)
        conf.set('type.float', -1.19)
        conf.set('type.str', 'hello config')
        conf.set('type.bool.on', True)
        conf.set('type.bool.off', False)
        conf.set('type.none', None)

        # a list
        conf.set('type.list', ['a', 'b', 'c', 1, 2, 3, 1.1, 1.2, 1.3,])

        # an object
        conf.set('type.object', { 'a': 1, 'b': 1.1, 'c': 'd' })

        # assert config-paths are there
        self.assertTrue(conf.exists('type.int'))
        self.assertTrue(conf.exists('type.float'))
        self.assertTrue(conf.exists('type.str'))
        self.assertTrue(conf.exists('type.bool.on'))
        self.assertTrue(conf.exists('type.bool.off'))
        self.assertTrue(conf.exists('type.list'))
        self.assertTrue(conf.exists('type.object'))
        self.assertTrue(conf.exists('type.none'))

        # check values
        self.assertEqual(1357, conf.get('type.int'))
        self.assertEqual(-1.19, conf.get('type.float'))
        self.assertEqual('hello config', conf.get('type.str'))
        self.assertEqual(None, conf.get('type.none'))
        self.assertTrue(conf.get('type.bool.on'))
        self.assertFalse(conf.get('type.bool.off'))

        # check list length
        self.assertEqual(9, len(conf.get('type.list')))

        # check object values
        self.assertEqual(1, conf.get('type.object')['a'])
        self.assertEqual(1.1, conf.get('type.object')['b'])
        self.assertEqual('d', conf.get('type.object')['c'])


    def test_get_on_unknown_paths(self):
        """An unknown path should raise ``KeyError``."""
        conf = ConfigViper()
        self.assertRaises(KeyError, conf.get, 'do')
        self.assertRaises(KeyError, conf.get, 'do.not')
        self.assertRaises(KeyError, conf.get, 'do.not.exists')
        self.assertRaises(KeyError, conf.get, 'do.not.exists.')
        self.assertRaises(KeyError, conf.get, '')
        self.assertRaises(KeyError, conf.get, '.')
        self.assertRaises(KeyError, conf.get, '...')


    def test_set_strange_paths(self):
        """Test strange config-paths and config-path overruns."""
        conf = ConfigViper()
        conf.set('', 1)
        self.assertRaises(PathOverrun, conf.set, '...', 2)

        conf.set('a.b', 1)
        self.assertRaises(PathOverrun, conf.set, 'a.b.c', 2)


    def tearDown(self):
        if os.path.exists(self._cfg_filename):
            os.unlink(self._cfg_filename)


class TestProxyProperty(unittest.TestCase):
    """Test config-path access via object attribute access."""

    def setUp(self):
        self._cfg_filename = 'test-proxy.json'
        ConfigViper.configure(pathname='.', filename=self._cfg_filename)
        if os.path.exists(self._cfg_filename):
            # ensure file do not exists
            os.unlink(self._cfg_filename)

        values = (
                ('foo.bar.baz', 'circus', None),
                ('foo.bar.spam.ham', 3.1415, None),
                ('foo.bar.spam.eggs', SpamEggs(), SpamEggsConverter()),)

        conf = ConfigViper()
        conf.stabilize(values)


    def test_basic_access(self):
        """Test basic access via object attribute."""
        conf = ConfigViper()
        self.assertEqual('circus', conf.foo.bar.baz)
        self.assertEqual(3.1415, conf.foo.bar.spam.ham)
        self.assertEqual(SpamEggs(), conf.foo.bar.spam.eggs)


    def test_proxy(self):
        """Test config-path composition and access."""
        conf = ConfigViper()
        p = conf.foo.bar.spam  # "ham" and "eggs" below "foo.bar.spam"
        self.assertEqual('foo.bar.spam', p.path)
        self.assertEqual(3.1415, p.ham)
        self.assertEqual(SpamEggs(), p.eggs)


    def test_proxy_instance(self):
        """The proxy instance should be the same through the config-paths."""
        conf = ConfigViper()
        foo = conf.foo
        bar = foo.bar
        spam = bar.spam
        self.assertEqual(foo, bar)
        self.assertEqual(bar, spam)


    def tearDown(self):
        if os.path.exists(self._cfg_filename):
            os.unlink(self._cfg_filename)


class TestStopSaving(unittest.TestCase):
    """Test set with/without stop saving feature."""

    def setUp(self):
        self._cfg_filename = 'test-stopsaving.json'

        ConfigViper.configure(
                pathname='.', 
                filename=self._cfg_filename)

        # ensure file do not exists
        if os.path.exists(self._cfg_filename):
            os.unlink(self._cfg_filename)


    def test_scenario(self):
        conf = ConfigViper()

        # auto save is the default behavior
        self.assertTrue(conf.is_auto_save)

        # set some values
        conf.set('spam.ham', 1)
        conf.set('spam.eggs', 'sausage')

        # assert these values are saved
        with open(os.path.join(conf.pathname, conf.filename), 'r') as f:
            data = json.load(f)

        self.assertEqual(1, data['spam']['ham'])
        self.assertEqual('sausage', data['spam']['eggs'])

        # stop saving and set new values
        conf.stop_saving()
        conf.set('spam.ham', 7)
        conf.set('spam.eggs', 'cheese')

        # assert the old values still there
        with open(os.path.join(conf.pathname, conf.filename), 'r') as f:
            data = json.load(f)

        self.assertEqual(1, data['spam']['ham'])
        self.assertEqual('sausage', data['spam']['eggs'])

        # when save() is called, the old behavior should be restored
        conf.save()
        self.assertTrue(conf.is_auto_save)

        # and the new values should be seen
        self.assertEqual(7, conf.spam.ham)
        self.assertEqual('cheese', conf.spam.eggs)


    def tearDown(self):
        if os.path.exists(self._cfg_filename):
            os.unlink(self._cfg_filename)


class SpamEggs(object):

    def __init__(self):
        super(SpamEggs, self).__init__()
        self.what = 'egg'
        self.how_many = 1


    def __eq__(self, other):
        what_eq = self.what == other.what
        how_many_eq = self.how_many == other.how_many
        return what_eq and how_many_eq


class SpamEggsConverter(converters.Converter):

    def to_json(self, value):
        return { 'what': value.what, 'how_many': value.how_many }


    def to_python(self, value):
        instance = SpamEggs()
        instance.what = value['what']
        instance.how_many = value['how_many']
        return instance


if __name__ == '__main__':
    unittest.main()
