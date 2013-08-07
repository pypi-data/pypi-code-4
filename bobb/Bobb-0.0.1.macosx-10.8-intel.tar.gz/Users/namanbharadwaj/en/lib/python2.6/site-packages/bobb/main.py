import os
import os.path
import imp
import fnmatch

import bobb.internal
import bobb.exceptions

def import_bobbfile(name="bobbfile"):
  """ Finds and imports a bobbfile given the module or package name. """
  name = os.path.split(name)[1]
  if name.endswith('.py'):
    name = name[:-3]

  path = os.getcwd()
  while path != '/':
    try:
      mod_tup = imp.find_module(name, [path])
    except ImportError:
      path = os.path.abspath(os.path.join(path, '..'))
      continue
    return imp.load_module(name, *mod_tup)

  raise bobb.exceptions.BobbfileNotFoundError()

def build(target):
  """ Builds a target """
  abs_target = os.path.join(os.getcwd(), target)

  if not bobb.internal.has_builder(abs_target):
    raise bobb.exceptions.BuilderNotFoundError(target)

  if bobb.internal.get_builder(abs_target)():
    print('target %s built' % target)
  else:
    print('nothing new to build for target %s' % target)
