import subprocess
import os
import os.path
import time
from contextlib import contextmanager
from functools import wraps

import bobb.internal
import bobb.exceptions

def run(command):
  """ Run the given command in the shell. """
  subprocess.call(command, shell=True)

@contextmanager
def cd(directory):
  """ Change directory within a context manager. """
  if directory is None:
    prev = os.getcwd()
    yield
    os.chdir(prev)
  else:
    prev = os.getcwd()
    os.chdir(directory)
    yield
    os.chdir(prev)

def builder(tgts=[], deps=[], always_build=False, dir=None):
  """ Register the given function as a builder.

  Bobb expects builders to create certain target paths. Bobb will also ensure
  that any paths required to build the targets (dependencies) exist, and if
  they don't, Bobb will attempt to build them.

  The builder can expect that none of the target paths exist prior to execution
  and that all of the dependencies do exist and have been appropriately built
  (by some other registered builder if it exists).

  Keyword arguments:
  tgts -- a list of paths which Bobb expects the builder to generate.
  deps -- a list of paths on which the builder depends.
  always_build -- if True, always rebuild the targets; otherwise, be smart.
  dir  -- the working directory within which Bobb will execute the builder.

  Note: If relative paths are used, they are assumed to be relative to the dir
  argument.

  Note 2: The builder should be able to build its targets without any passed
  arguments (default arguments are ok). When resolving dependencies, Bobb
  passes no arguments to the builder function.

  """
  def decorate(fn):
    if len(tgts) == 0:
      # Builders must generate one or more target paths.
      raise bobb.exceptions.TargetConfigError(fn.__name__)

    @wraps(fn)
    def wrapper():
      with cd(dir):
        def has_builder(tgt):
          return bobb.internal.has_builder(os.path.abspath(tgt))
        def is_file(path):
          return os.path.exists(path)

        # Check that every dependency is a file or can be built.
        def check_valid(dep):
          if not has_builder(dep) or is_file(dep):
            raise bobb.exceptions.BuilderNotFoundError(dep)
        map(check_valid, deps)

        # Build all dependencies that have a builder
        def call_builder(dep):
          if has_builder(dep):
            bobb.internal.get_builder(os.path.abspath(dep))()
        map(call_builder, deps)

        # Check that all dependencies are now files - if not, some builder is
        # deleting an unrelated dependency.
        def check_not_deleted(dep):
          if not is_file(dep):
            raise bobb.exceptions.TargetDeletionError(dep)
        map(check_not_deleted, deps)

        # If we're missing a tgt, build. If there's a newly modified
        # dependency, build. Otherwise, nothing to do (return False).
        def build():
          run('rm -Rf %s' % ' '.join(tgts))
          fn()
        if always_build:
          build()
        elif not all(map(is_file, tgts)):
          build()
        elif len(deps) > 0:
          newest_dep_time = max(map(os.getmtime, deps))
          oldest_tgt_time = min(map(os.getmtime, tgts))
          if oldest_tgt_time < newest_dep_time:
            build()
          else:
            return False
        else:
          return False

        # Quick check to make errors more transparent - make sure that all tgts
        # actually exist after "building" them.
        def check_built(tgt):
          if not is_file(tgt):
            raise BuilderError(tgt, fn.__name__)
        map(check_built, deps)

        return True

    # Register builder as building the given targets
    with cd(dir):
      for tgt in tgts:
        bobb.internal.register_builder(os.path.abspath(tgt), wrapper)

    return wrapper
  return decorate

def action(deps=[], dir=None):
  """ Register the given function as an action.

  Bobb will ensure that any paths required to execute the action (dependencies)
  exist, and if they don't, Bobb will attempt to build them.

  The action can expect that all of the dependencies do exist and have been
  appropriately built (by some other registered builder if it exists) prior to
  execution.

  Keyword arguments:
  deps -- a list of paths on which the builder depends.
  dir  -- the working directory within which Bobb will execute the builder.

  Note: If relative paths are used, they are assumed to be relative to the dir
  argument.

  """
  def decorate(fn):
    @wraps(fn)
    def wrapper():
      with cd(dir):
        def has_builder(tgt):
          return bobb.internal.has_builder(os.path.abspath(tgt))
        def is_file(path):
          return os.path.exists(path)

        # Check that every dependency is a file or can be built.
        def check_valid(dep):
          if not has_builder(dep) or is_file(dep):
            raise bobb.exceptions.BuilderNotFoundError(dep)
        map(check_valid, deps)

        # Build all dependencies that have a builder
        def call_builder(dep):
          if has_builder(dep):
            bobb.internal.get_builder(os.path.abspath(dep))()
        map(call_builder, deps)

        # Check that all dependencies are now files - if not, some builder is
        # deleting an unrelated dependency.
        def check_not_deleted(dep):
          if not is_file(dep):
            raise bobb.exceptions.TargetDeletionError(dep)
        map(check_not_deleted, deps)

        # Execute the action
        fn()

    # Register action
    with cd(dir):
      bobb.internal.register_action(wrapper)

    return wrapper
  return decorate
