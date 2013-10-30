from __future__ import absolute_import


class DuxlibException(Exception):
  pass


def and_then(*args):
  if len(args) == 1 and isinstance(args[0], list):
    args = args[0]

  if not len(args) > 0:
    raise DuxlibException("and_then requires > 1 functions")

  def decorated(*args_, **kwargs_):
    result = args[0](*args_, **kwargs_)
    for f in args[1:]:
      result = f(result)
    return result

  return decorated
