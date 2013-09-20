# jinja-tools
#
# various tools for Jinja2
# including new filters and tests based on python-moretools,
# a JinjaLoader class for Django
# and a simple JinjaBuilder class for SCons
#
# Copyright (C) 2011-2013 Stefan Zimmermann <zimmermann.code@gmail.com>
#
# jinja-tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jinja-tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with jinja-tools.  If not, see <http://www.gnu.org/licenses/>.

from moretools import *

__all__ = 'filters',

def dictremove(dict_, *keys):
  for key in keys:
    try: del dict_[key]
    except KeyError: pass

  return dict_

def dictupdate(dict_, items = (), **kwitems):
  dict_.update(items, **kwitems)
  return dict_

filters = dict(
  mapattr = mapattr,
  mapmapattr = mapmapattr,

  mapattrs = mapattrs,
  mapmapattrs = mapmapattrs,

  mapitem = mapitem,
  mapmapitem = mapmapitem,

  mapitems = mapitems,
  mapmapitems = mapmapitems,

  mapmethodcall = mapmethodcall,
  mapmapmethodcall = mapmapmethodcall,

  mapjoin = lambda seqs, sep: map(
    lambda seq: sep.join(map(str, seq)),
    seqs),

  zip = lambda seq, *seqs: zip(*chain(seq, seqs)),
  zipwith = zip,

  tee = tee,

  repeat = repeat,

  chain = lambda seq, *seqs: chain(*chain(seq, seqs)),
  chainwith = chain,

  combine = combinations,
  permutate = permutations,

  cross = lambda seq, *seqs: product(*chain(seq, seqs)),
  crosswith = product,

  dict = dict,

  dictremove = dictremove,
  dictupdate = dictupdate,

  partial = partial,

  split = str.split,
  )
