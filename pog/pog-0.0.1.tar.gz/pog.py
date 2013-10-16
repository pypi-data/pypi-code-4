#!/usr/bin/env python
# encoding: utf-8

"""Azkaban CLI.

Usage:
  pog [PATH]

"""

from collections import defaultdict
from contextlib import contextmanager
from getpass import getuser
from os import close, remove
from os.path import basename, exists, splitext
from tempfile import mkstemp
from zipfile import ZipFile


def flatten(dct, sep='.'):
  """TODO: flatten docstring.

  :param dct: TODO
  :param sep: TODO

  """
  def _flatten(dct, prefix=''):
    """Inner recursive function."""
    items = []
    for key, value in dct.items():
      new_prefix = '%s%s%s' % (prefix, sep, key) if prefix else key
      if isinstance(value, dict):
        items.extend(_flatten(value, new_prefix).items())
      else:
        items.append((new_prefix, value))
    return dict(items)
  return _flatten(dct)

def id_generator():
  """TODO: id_generator docstring."""
  index = 0
  while True:
    index += 1
    yield index

@contextmanager
def temppath():
  """TODO: temppath docstring."""
  (desc, path) = mkstemp()
  close(desc)
  remove(path)
  try:
    yield path
  finally:
    if exists(path):
      remove(path)

class PogError(Exception):

  """TODO: PogError docstring

  :param message: TODO

  """

  def __init__(self, message):
    super(PogError, self).__init__(message)


class Job(object):

  """TODO: Job docstring

  :param options: TODO
  :param dependencies: List of `Job` instances that should be run first.
  :param name: If you want to run the job separately.

  """

  def __init__(self, *options):
    self._options = options

  @property
  def options(self):
    """TODO: options docstring."""
    options = {}
    for option in reversed(self._options):
      options.update(flatten(option))
    return options

  def generate(self, path):
    """Create job file.

    :param path: TODO

    """
    with open(path, 'w') as writer:
      for key, value in sorted(self.options.items()):
        writer.write('%s=%s\n' % (key, value))


class Project(object):

  """TODO: Project docstring

  :param name: TODO
  :param user: TODO

  """

  def __init__(self, name):
    self.name = name
    self._jobs = {}
    self._files = set()

  def add_file(self, path):
    """TODO: add_file docstring.

    :param path: TODO

    """
    self._files.add(path)

  def add_job(self, name, job):
    """TODO: add docstring.

    :param job: TODO
    :param dependencies: list of jobs or job names

    """
    if name in self._jobs:
      raise PogError('duplicate job name: %r' % (name, ))
    else:
      self._jobs[name] = job

  def upload(self, user=None):
    """TODO: upload docstring.

    :param user: TODO

    """
    user = user or getuser()

  def build(self, path):
    """TODO: zip docstring.

    :param path: TODO

    """
    with ZipFile(path, 'w') as writer:
      for name, job in self._jobs.items():
        with temppath() as fpath:
          job.generate(fpath)
          writer.write(fpath, '%s.job' % (name, ))
      for fpath in self._files:
        writer.write(fpath)


def chain(*args):
  """TODO: chain docstring.

  :param *args: TODO

  """
  pass


def group(*args):
  """TODO: group docstring.

  :param *args: TODO

  """
  pass


if __name__ == '__main__':
  pass
