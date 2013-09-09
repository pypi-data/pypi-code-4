# copyright 2012-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-wireit controllers"""

from cubicweb import Binary
from cubicweb.predicates import match_form_params, match_user_groups
from cubicweb.web import jsonize
from cubicweb.web.controller import Controller


class FileFieldUploadController(Controller):
    __regid__ = 'wireit_upload'
    __select__ = (Controller.__select__ & match_user_groups('managers', 'users')
                  & match_form_params('files[]'))

    @jsonize
    def publish(self, *args, **kwargs):
        self.debug("UploadController call with args %s, kwargs %s and form %s",
                   args, kwargs, self._cw.form)
        try:
            data_name, flike_obj = self._cw.form['files[]']
            newfile = self._cw.create_entity('File', data_name=data_name,
                                             data=Binary(flike_obj.read()))
        except Exception, exc:
            self.exception(exc)
            return {'status': False, 'msg': self._cw._('unknown error')}
        return {'status': True, 'eid': newfile.eid, 'title': newfile.dc_title(),
                'url': newfile.absolute_url()}
