# Copyright (c) 2009, 2010, 2013
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
import time
from render_appointment import render_appointment, render_resource
from render_project import render_project
from render_contact import render_contact
from render_enterprise import render_enterprise
from render_team import render_team
from render_task import render_task
from render_lock import render_lock
from render_blob import render_folder, render_file
from render_route import render_route
from render_process import render_process
from render_collection import render_collection
from render_routegroup import render_routegroup
from coils.core import BundleManager, CoilsException

RENDER_MAP = {'Document': render_file,
              'Folder': render_folder,
              'Contact': render_contact,
              'Project': render_project,
              'Enterprise': render_enterprise,
              'Team': render_team,
              'Lock': render_lock,
              'lock': render_lock,
              'Task': render_task,
              'Route': render_route,
              'Process': render_process,
              'Collection': render_collection,
              'RouteGroup': render_routegroup,
              'Appointment': render_appointment,
              'Resource': render_resource,
              'resource': render_resource, }


class Render:
    @staticmethod
    def Result(entity, detail, ctx):
        result = Render.Results([entity], detail, ctx)
        if (len(result) == 0):
            return None
        return result[0]

    @staticmethod
    def Results(entities, detail, ctx):

        if (len(entities) == 0):
            return []

        start = time.time()
        kinds = ctx.type_manager.group_by_type(objects=entities)
        fav_ids = {}
        results = []

        for kind in kinds.keys():

            # Get favorites for this kind
            fav_ids = ctx.get_favorited_ids_for_kind(kind, refresh=False)
            if not fav_ids:
                '''
                this default may not be defined for this user, but we did
                check for it so in this case we assume the context has no
                favorites
                '''
                fav_ids = []

            method = RENDER_MAP.get(kind, None)
            if not method:
                raise CoilsException(
                    'Omphalos cannot render entity {0}'.format(kind, ))

            if (detail & 8192):
                plugins = BundleManager.get_content_plugins(kind, ctx)
            else:
                plugins = False

            # Render the entities
            total_time = 0.0
            for entity in kinds[kind]:
                start = time.time()
                o_rep = method(entity, detail, ctx, favorite_ids=fav_ids)
                if plugins:
                    '''
                    Process *content* plugins if detail level 8192 is specified
                    '''
                    plugin_data = []
                    for plugin in plugins:
                        if hasattr(plugin, 'get_extra_content'):
                            data = plugin.get_extra_content(entity)
                            if isinstance(data, dict):
                                data.update(
                                    {'entityName': 'PluginData',
                                     'pluginName': plugin.__pluginName__, })
                                plugin_data.append(data)
                    o_rep['_PLUGINDATA'] = plugin_data
                total_time += time.time() - start
                results.append(o_rep)

        return results
