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
from sqlalchemy.orm import joinedload, noload, subqueryload, eagerload
from task import Task
from contact import Contact
from project import Project

ORMHINTS = \
    {Task:
        {'zogi': (
            noload('info'),
            joinedload('owner'),
            noload('owner.notes'),
            noload('owner.acls'),
            noload('owner.locks'),
            noload('owner.telephones'),
            noload('owner.addresses'),
            noload('owner.company_values'),
            noload('creator'),
            noload('creator.notes'),
            noload('creator.acls'),
            noload('creator.locks'),
            noload('creator.telephones'),
            noload('creator.addresses'),
            noload('creator.company_values'),
            joinedload('project'),  # Disabling will break access projection!
            noload('project.acls'),
            noload('project.locks'),
            noload('project.tasks'),
            noload('project.children'),
            noload('project.folder'),
            noload('project.assignments'),
            #noload('project.notes'),
            noload('creator.projects'),
            noload('owner.projects'),
            subqueryload('acls'),
            eagerload('acls'),
            noload('creator.enterprises'),
            noload('owner.enterprises'),
            noload('creator.teams'),
            noload('owner.teams'),
            noload('creator.info'),
            noload('owner.info'), ),
         'webdav': (
            joinedload('info'),
            noload('owner'),
            noload('creator'),
            noload('project'),
            noload('properties'), ),
         0: (
            noload('notes'),
            noload('attachments'),
            joinedload('parent'),
            noload('parent.creator'),
            noload('parent.owner'),
            noload('parent.project'),
            noload('parent.properties'),
            noload('parent.acls'),
            noload('parent.children'),
            noload('parent.attachments'),
            noload('logs'),
            noload('project_assignments'),
            noload('parent.project_assignments'), ),
         1: (
            joinedload('notes'),
            eagerload('notes'), ),
         16: (
            noload('properties'),
         ),
         32: (
            subqueryload('logs'),
            eagerload('logs'), ),
         128: (
            subqueryload('children'),
            eagerload('children'),
            subqueryload('children.children'),
            eagerload('children.children'),
            subqueryload('parent.children'), ),
         },
     Contact:
        {'zogi':(
            noload('company_values'),
            noload('notes'),
            noload('enterprises'),
            noload('teams'),
            noload('projects'),
            noload('logs'),
            noload('properties'),
            joinedload('info'),
            subqueryload('telephones'),
            subqueryload('addresses'),
            ),
         'webdav': (
            joinedload('info'),
            noload('owner'),
            noload('creator'),
            noload('project'),
            subqueryload('properties'), ),
         8: (
            eagerload('company_values'), ),
         16: (
            subqueryload('properties'),
            eagerload('properties'), ),
         32: (
            subqueryload('logs'),
            eagerload('logs'), ),
        },
     Project:
        {'zogi':(
            noload('tasks'),
            noload('properties'),
            noload('logs'),
            noload('children'),
            joinedload('_info'),
            ),
         'webdav':(
            noload('tasks'),
            noload('properties'),
            #noload('logs'),
            subqueryload('children'),
            ),
         16: (
            subqueryload('properties'),
            eagerload('properties'),
            ),
         32: (
            #subqueryload('logs'),
            #eagerload('logs'),
            ),
         128: (
            subqueryload('children'),
            ),
         4096: (
            subqueryload('tasks'),
            ),
         32768: (
            subqueryload('acls'),
            ),
        }
     }
