# ==================================================================================================
# Copyright 2013 Twitter, Inc.
# --------------------------------------------------------------------------------------------------
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this work except in compliance with the License.
# You may obtain a copy of the License in the LICENSE file, or at:
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==================================================================================================

__author__ = "tdesai"

import os
import re


class ArgError(Exception):
  """Raised to indicate a given Argument value is not valid."""


class BaseArg(object):
  def get(self, config=None):
    """
    Return an iterable of strings representing this argument
    """
    raise NotImplementedError("get must be implemented for all 'BaseArg's")


class Arg(BaseArg):
  """
  Key value arguments
  """
  """
  This Regular expression supports config value as /tmp/%(config.pants_workdir)s/thrift
  group1 is prefix or '/tmp'
  group2 is '%('
  group3 is value 'config.' or empty string if section is not present
  group4 is section value 'config' or empty string
  group5 is '.' if present or empty string
  group6 is option value 'pants_workdir'
  group7 is ')s'
  group 8 is suffix 's/thrift'
  """
  CONFIG_PATTERN = re.compile(r'(.*)(\%\()((.*)(\.))?(.+)(\)s)(.*)')

  def __init__(self, name, value, separator=None):
    self._name = name
    self._value = value
    self._separator = separator
    self._calculated_value = None

  def get(self, config):
    """
    >>> Arg('hello', 'world').get(None)
    ('hello', 'world')

    >>> Arg('-f', 'plain').get(None)
    ('-f', 'plain')

    >>> Arg('-k', '2', separator='=').get(None)
    ('-k=2',)
    """
    self._set_calculated_value(config)
    return ((self._name, self._calculated_value) if self._separator is None else
            (self._separator.join((self._name, self._calculated_value)),))

  def _set_calculated_value(self, config):
    if not self._calculated_value:
      self._calculated_value = self._interpolate_config(config, self._value)

  def _interpolate_config(self, config, value):
    config_key = Arg.CONFIG_PATTERN.match(value)
    if config_key:
      config_value = self._get_config_value(config, config_key.group(4), config_key.group(6))
      value = ''.join([config_key.group(1), config_value, config_key.group(8)])
      return self._interpolate_config(config, value)
    else:
      return value

  def _get_config_value(self, config, section, option):
    if not config:
      raise ArgError('Can not apply None config to value %s' % self._value)
    config_value = config.get(section, option) if section else config.getdefault(option)
    if not config_value:
      raise ArgError('Config value %s not set in the ini. Please check and re-run' % self._value)
    return config_value

  def get_value(self):
    return self._value


class FileArg(Arg):
  """
  Arguments whose value is a file
  """
  def __init__(self, name, file_name, separator=None, must_exist=False):
    super(FileArg, self).__init__(name, file_name, separator)
    self._must_exist = must_exist

  def file_exists(self):
    return os.path.exists(self._calculated_value)

  def get(self, config):
    """
    >>> FileArg('foo', 'bar', must_exist=False).get(None)
    ('foo', 'bar')

    >>> import tempfile
    >>> with tempfile.NamedTemporaryFile() as temp_file:
    ...   print FileArg('-c', temp_file.name, must_exist=True).get(None) == ('-c', temp_file.name)
    True

    >>> FileArg('-foo', 'test', must_exist=True).get(None)
    Traceback (most recent call last):
    ...
    ArgError: File test does not exists for argument -foo
    """
    args = super(FileArg, self).get(config)
    if self._must_exist and not self.file_exists():
      raise ArgError("File %s does not exists for argument %s" % (self._calculated_value,
                                                                  self._name))
    return args


class JvmProperty(Arg):
  """
  Java property style arguments
  Generates a -D<key>=<value> flag
  """

  def __init__(self, key, value):
    self._key = key
    self._value = value
    self._calculated_value = None

  def get(self, config):
    """
    >>> JvmProperty('foo', 'bar').get(None)
    ('-Dfoo=bar',)

    >>> JvmProperty('foo', '').get(None)
    ('-Dfoo=',)
    """
    self._set_calculated_value(config)
    return ('-D%s=%s' % (self._key, self._calculated_value),)


class Flag(BaseArg):

  def __init__(self, flag):
    self._flag = flag

  def get(self, config):
    """
    >>> Flag('-foo').get(None)
    ('-foo',)

    >>> Flag('-usejavacp').get(None)
    ('-usejavacp',)
    """
    return ("%s" % (self._flag),)
