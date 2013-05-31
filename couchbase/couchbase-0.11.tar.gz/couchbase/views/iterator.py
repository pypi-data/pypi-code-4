#
# Copyright 2013, Couchbase, Inc.
# All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from collections import namedtuple
from warnings import warn

from couchbase.exceptions import ArgumentError, CouchbaseError
from couchbase.views.params import (
    Params, _bool_param_handler, make_options_string, make_dvpath)


ViewRow = namedtuple('ViewRow', ['key', 'value', 'docid', 'doc'])

DEFAULT_BATCHSIZE = 100
"""
The default batch size. This sets the default value for 'limit'
"""

class View(object):
    def __init__(self,
                 parent,
                 ddoc,
                 view,
                 params = {},
                 row_factory=ViewRow,
                 batchsize = DEFAULT_BATCHSIZE,
                 include_docs = False,
                 passthrough = False,
                 unrecognized_ok = False):

        self._parent = parent
        self.design = ddoc
        self.view = view
        self.row_factory = row_factory

        self._result = None
        self._batchsize = batchsize
        self._current_offset = 0

        if Params.REDUCE in params and include_docs and (
            _bool_param_handler(params['reduce'] == 'true')):

            raise ArgumentError.pyexc("include_docs is only applicable "
                                      "for map-only views, but 'reduce' "
                                      "was specified")

        self._include_docs = include_docs
        self._params = params.copy()

        # Validate the params at construction time. This might waste some
        # CPU cycles, but for now we're assuming this isn't a critical path:
        make_options_string(self._params,
                            allow_unrecognized = unrecognized_ok,
                            passthrough = passthrough)

        self._passthrough = passthrough
        self._unrecognized_ok = unrecognized_ok

        self.indexed_rows = 0



    def _get_page(self):
        if self._current_offset == -1:
            # Pagination done
            return ([],{})

        params = self._params.copy()
        if self._batchsize:
            params[Params.SKIP] = self._current_offset
            params[Params.LIMIT] = self._batchsize

        rv = self._parent._view(
            self.design,
            self.view,
            params,
            allow_unrecognized_params = self._unrecognized_ok,
            params_is_passthrough = self._passthrough)

        if not rv.success:
            excls = CouchbaseError.rc_to_exctype(rv.rc)
            raise excls.pyexc("Couldn't get view results")

        # TODO: on_error handling for inline errors

        docs = {}
        rows = rv.value['rows']
        self.indexed_rows = rv.value['total_rows']

        if self._include_docs:
            keys = map(lambda x: x['id'], rows)
            docs = self._parent.get_multi(keys, quiet=True)

        if len(rows) < self._batchsize:
            self._current_offset = -1
        else:
            self._current_offset += self._batchsize

        return (rows, docs)


    def __iter__(self):
        while True:
            rows, docs = self._get_page()
            if not rows:
                break

            for row in rows:
                key, value, docid = row['key'], row['value'], row['id']
                doc = None

                if self._include_docs:
                    try:
                        doc = docs[docid]
                    except KeyError:
                        warn("Possible inconsistency between "
                             "view and memcached detected. Could not fetch doc")

                yield self.row_factory(key, value, docid, row)
