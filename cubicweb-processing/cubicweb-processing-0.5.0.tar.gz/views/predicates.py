# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-processing forms"""

from logilab.common.registry import objectify_predicate


def _runchain_linkto_eid(req):
    runchain_eid = None
    for linkto in req.list_form_param('__linkto'):
        rtype, linkto_eid, role = linkto.split(':')
        if rtype == 'wiring':
            runchain_eid = linkto_eid
            break
    return runchain_eid

@objectify_predicate
def has_link_to_runchain(self, req, **kwargs):
    return _runchain_linkto_eid(req) is not None
