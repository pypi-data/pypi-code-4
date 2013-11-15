#
# Copyright (c) 2013
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
from coils.core import \
    CoilsException, \
    NotImplementedException, \
    CoilsUnreachableCode, \
    Route, \
    Process, \
    Collection, \
    Contact, \
    Enterprise, \
    BLOBManager, \
    CTag, \
    Team, \
    Project, \
    PropertyManager, \
    AssumedContext
from coils.foundation import \
    OGO_ROLE_WORKFLOW_DEVELOPERS, \
    OGO_ROLE_DATA_MANAGER, \
    OGO_ROLE_SYSTEM_ADMIN, \
    OGO_ROLE_HELPDESK, \
    OGO_ROLE_WORKFLOW_ADMIN
from decorators import has_context


class CIAAPI(object):

    def __init__(self, context):
        self.context = context

    @has_context(
        required_role=(OGO_ROLE_SYSTEM_ADMIN,
                       OGO_ROLE_WORKFLOW_ADMIN, ))
    def get_rights(self, context_id, object_id):
        '''
        Return a dict representing the rights for the specified context
        on the specified target object; this also includes information on
        the context such as roles and context_ids.
        :param context_id: account id for context to test
        :param object_id: object id of the object to test
        '''

        # TODO: simple CoilsException seems the wrong result value
        tmpctx = AssumedContext(context_id)
        if not tmpctx:
            raise CoilsException(
                'OGo#{0} is not a valid context'.format(context_id, ))

        # TODO: simple CoilsException seems the wrong result value
        target = self.context.type_manager.get_entity(object_id)
        if not target:
            raise CoilsException(
                'Cannot marshall entity OGo#{0}'.format(object_id, ))

        rights = list(tmpctx.access_manager.access_rights(target))
        result = {
            'accountObjectId': tmpctx.account_id,
            'contextContextIds': tmpctx.context_ids,
            'contextLogin': tmpctx.login,
            'contextRoles': list(tmpctx.roles),
            'targetObjectId': target.object_id,
            'targetEntityNamee': target.__entityName__,
            'targetAccessRights': rights,
        }

        tmpctx.close()

        return result
