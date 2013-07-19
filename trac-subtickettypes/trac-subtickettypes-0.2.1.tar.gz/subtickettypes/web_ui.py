 #
 # Copyright 2009, Niels Sascha Reedijk <niels.reedijk@gmail.com>
 # All rights reserved. Distributed under the terms of the MIT License.
 #

# debug
from pprint import pprint


from pkg_resources import resource_filename
from genshi import HTML
from genshi.builder import tag
from genshi.filters.transform import Transformer

from trac.core import *
from trac.ticket import model
from trac.util.text import unicode_quote_plus
from trac.web.api import IRequestFilter
from trac.web.chrome import ITemplateProvider
from trac.web.chrome import ITemplateStreamFilter
from trac.web.chrome import add_notice
from trac.web.chrome import add_script
from trac.ticket.roadmap import TicketGroupStats
from trac.util.translation import _

# --------------------------------------------------------------------------- #
class SubTicketTypesModule(Component):
    """Implements subtickettypes in Trac's interface."""

    implements(IRequestFilter, ITemplateProvider, ITemplateStreamFilter)

    # ....................................................................... #
    # IRequestFilter method
    def pre_process_request(self, req, handler):

        # handle the admin panel
        if req.path_info.startswith("/admin/ticket/type/"):

            # handle cancel submit by redirecting back to the list page
            # TODO: patch subcomponents with "cancel" check
            if req.method == "POST" and req.args.get('cancel'):
                    req.redirect(req.href.admin('ticket', 'type'))

            if req.method == "POST" and 'rename_children' in req.args:
                # if we are not renaming the children for a ticket type that
                # has childer, its a regular update, so let trac handle it.
                if req.args.get('rename_children') != 'on':
                    return handler

                # other wise first lets rename the parent type first
                # get the original name (before renaming)
                # 19 is the length of "/admin/ticket/type/" string
                parent_ticket_type_name = req.path_info[19:]

                parent_ticket_type = model.Type(self.env, parent_ticket_type_name)
                parent_ticket_type.name = req.args.get('name')
                try:
                    parent_ticket_type.update()
                except self.env.db_exc.IntegrityError:
                    raise TracError(_('The ticket type "%(name)s" already '
                                      'exists.', name=parent_ticket_type_name))

                # Now update names in the the child ticket types
                child_ticket_types = self._get_tickettype_children(parent_ticket_type_name)
                for ticket_type in child_ticket_types:
                    ticket_type.name = ticket_type.name.replace(parent_ticket_type_name, req.args.get('name'), 1)
                    ticket_type.update()
                add_notice(req, _('Your changes have been saved.'))
                req.redirect(req.href.admin('ticket', 'type'))

        return handler


    # ....................................................................... #
    # IRequestFilter method
    def post_process_request(self, req, template, data, content_type):
        # The /query paths are handled in filter_stream()
        if req.path_info.startswith('/ticket/') or \
           req.path_info.startswith('/newticket'):
            add_script(req, 'subtickettypes/tickettypeselect.js')

        if template == "query.html":
            # Allow users to query for parent ticket types and include all

            # sub ticket types as well
            # check if the entry already exists (might be added by another
            # plugin)
            begins_with_select_item = {'name': _("begins with"), 'value': ""}
            if begins_with_select_item not in data['modes']['select']:
                data['modes']['select'].insert(0, begins_with_select_item)

        if template == "milestone_view.html":
            # Group tickets in the milestone view by base component.
            if data['grouped_by'] == "type":
                ticket_type_name = ''
                new_groups = []
                new_ticket_types = []
                for ticket_type in data['groups']:
                    ticket_type_name = ticket_type['name'].split("/")[0]
                    if ticket_type_name not in new_ticket_types:
                        # This ticket type is not yet in the new list of ticket
                        # types, add it.
                        new_ticket_types.append(ticket_type_name)
                        # Fix URLs to the querys (we use unicode_quote_plus to
                        # replace the '/' with something URL safe (like the
                        # hrefs are)
                        new_hrefs = []
                        for interval_href in ticket_type['interval_hrefs']:
                            new_hrefs.append(interval_href.replace(unicode_quote_plus(ticket_type['name']), '^' + ticket_type_name))
                        ticket_type['stats_href'] = ticket_type['stats_href'].replace(unicode_quote_plus(ticket_type['name']), '^' + ticket_type_name)
                        ticket_type['interval_hrefs'] = new_hrefs
                        # Set the name to the base name (in case this originally
                        # is a sub ticket type.
                        ticket_type['name'] = ticket_type_name

                        new_groups.append(ticket_type)
                    else:
                        # This is a sub ticket type. Add the stats to the main ticket type.
                        # Note that above two lists are created. Whenever an
                        # item is added to one, an analogous one is added to
                        # the other. This code uses that logic.
                        core_ticket_type = new_groups[new_ticket_types.index(ticket_type_name)]
                        merged_stats = core_ticket_type['stats'] #TicketGroupStats from trac.ticket.roadmap
                        new_stats = ticket_type['stats']

                        # Bear with me as we go to this mess that is the group stats
                        # (or of course this hack, depending on who's viewpoint).
                        # First merge the totals
                        merged_stats.count += new_stats.count

                        # The stats are divided in intervals, merge these.
                        i = 0
                        for interval in merged_stats.intervals:
                            new_interval = new_stats.intervals[i]
                            interval['count'] += new_interval['count']
                            i += 1
                        merged_stats.refresh_calcs()

                # Now store the new milestone tickey type groups
                data['groups'] = new_groups

        return template, data, content_type


    # ....................................................................... #
    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        """Return the absolute path of a directory containing additional
        static resources (such as images, style sheets, etc).
        """
        return [('subtickettypes', resource_filename(__name__, 'htdocs'))]

    # ....................................................................... #
    # ITemplateProvider methods
    def get_templates_dirs(self):
        """Return the absolute path of the directory containing the provided
        ClearSilver templates.
        """
        return ""


    # ....................................................................... #
    # ITemplateStreamFilter method
    def filter_stream(self, req, method, filename, stream, data):

        # alternate matching possibilities
        # if req.path_info.startswith('/admin/ticket/type'):

        # Match to the admin ticket type detail editing panel of ticket type
        if      filename == "admin_enums.html" \
            and data['active_cat'] == u'ticket' \
            and data['active_panel'] == u'type' \
            and data['view'] == 'detail':

            # If ticket type has children, then add a checkbox to rename those
            if len(self._get_tickettype_children(data['enum'].name)) > 0:
                    stream |= Transformer("//div[@class='field'][1]").after(self._build_renamechildren_field())

        elif req.path_info.startswith('/query'):
            # We need to load our script after the initializeFilters() call done by Trac
            html = HTML('<script type="text/javascript" charset="utf-8" src="' +
                        req.href.base +
                        '/chrome/subtickettypes/tickettypeselect.js"></script>')
            stream |= Transformer('//head').append(html)
        return stream


    # ....................................................................... #
    # Helper function
    def _get_tickettype_children(self, name):
        tickettypes = model.Type.select(self.env)
        result = []
        for tickettype in tickettypes:
            if tickettype.name.startswith(name + "/") and tickettype.name != name:
                result.append(tickettype)
        return result

    # ....................................................................... #
    # Helper function
    def _build_renamechildren_field(self):
        return tag.div(tag.label(
            tag.input(_("Also rename children"), \
                        type='checkbox',
                        id='rename_children', \
                        name='rename_children',
                        checked='checked') \
                        ), \
                       class_='field')
