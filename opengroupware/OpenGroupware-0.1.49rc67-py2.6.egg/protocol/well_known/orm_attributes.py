
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

TASK_ATTRIBUTES = [
    {'attribute': 'startDate',
     'type': 'datetime',
     'description':
     'Start Date',
     'hints': ['utc', ], },
    {'attribute': 'endDate',
     'type': 'datetime',
     'description': 'End Date',
     'hints': ['utc', ], },
    {'attribute': 'name',
     'type': 'string',
     'description': 'Title',
     'hints': [], },
    {'attribute': 'project_id',
     'type': 'integer',
     'description': 'Project',
     'hints': ['objectId', 'project', ], },
    {'attribute': 'owner_id',
     'type': 'integer',
     'description': 'Owner',
     'hints': ['objectId', 'account', ], },
    {'attribute': 'executor_id',
     'type': 'integer',
     'description': 'Executor',
     'hints': ['objectId', 'executor', ], },
    {'attribute': 'completed',
     'type': 'datetime',
     'description': 'Completed',
     'hints': ['readonly', 'nullable', ], },
    {'attribute': 'notify',
     'type': 'integer',
     'description': 'Notify',
     'hints': ['taskNotification', ], },
    {'attribute': 'state',
     'type': 'string',
     'description': 'Status',
     'hints': ['taskStatus', 'readonly', ], },
    {'attribute': 'category',
     'type': 'string',
     'description': 'Categories',
     'hints': ['csv', 'categoryList', ], },
    {'attribute': 'kind',
     'type': 'string',
     'description': 'Kind',
     'hints': ['kind', 'tko', 'nullable', ], },
    {'attribite': 'keywords',
     'type': 'string',
     'description': 'Keywords',
     'hints': ['keywords', 'wsv', ], },
    {'attribute': 'sensitivity',
     'type': 'integer',
     'description': 'Sensitivity',
     'hints': ['sensitivity', ], },
    {'attribute': 'priority',
     'type': 'integer',
     'description': 'Priority',
     'hints': ['priority', ], },
    {'attribute': 'comment',
     'type': 'string',
     'description': 'Comment',
     'hints': ['comment', ], },
    {'attribute': 'complete',
     'type': 'integer',
     'description': 'Percent Complete',
     'hints': ['percentBy10s', ], },
    {'attribute': 'actual',
     'type': 'integer',
     'description': 'Actual Minutes',
     'hints': ['minutes', ], },
    {'attribute': 'total',
     'type': 'integer',
     'description': 'Total Minutes',
     'hints': ['minutes', ], },
    {'attribute': 'accounting',
     'type': 'string',
     'description': 'Accounting',
     'hints': ['outlook', ], },
    {'attribute': 'travel',
     'type': 'integer',
     'description': 'Kilometers',
     'hints': ['kilometers', ], },
    {'attribute': 'associated_companies',
     'type': 'string',
     'description': 'Companies',
     'hints': ['outlook', 'quotedCSV', ], },
    {'attribute': 'associated_contacts',
     'type': 'string',
     'description': 'Contacts',
     'hints': ['outlook', 'quotedCSV', ], },
    {'attribute': 'uid',
     'type': 'string',
     'description': 'GUID',
     'hints': ['guid', 'readonly', ], },
]

ORM_ATTRIBUTES = {
    'Task': TASK_ATTRIBUTES,
}

