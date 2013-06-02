import logging

from zope.component import getUtility
from zope.interface import implements
from zope.browsermenu.interfaces import IBrowserMenu
from zope.browsermenu.menu import BrowserMenu

from p4a.subtyper.interfaces import ISubtyper

#try:
#    from zope.component.interface import interfaceToName
#except ImportError, err:
#    from zope.app.component.interface import interfaceToName


logger = logging.getLogger('p4a.subtyper.menu')


class SubtypesMenu(BrowserMenu):
    """A menu with items representing all possible subtypes for the current
    context.
    """

    implements(IBrowserMenu)

    def _get_menus(self, object, request):
        subtyper = getUtility(ISubtyper)
        existing = subtyper.existing_type(object)

        result = []
        for subtype in subtyper.possible_types(object):
            descriptor = subtype.descriptor

            selected = existing is not None and subtype.name == existing.name

            d = {'title': descriptor.title,
                 'description': descriptor.description or u'',
                 'action': '%s/@@subtyper/change_type?subtype=%s' % \
                     (object.absolute_url(), subtype.name),
                 'selected': selected,
                 'icon': getattr(descriptor, 'icon', u''),
                 'extra': {'id': descriptor.type_interface.__name__,
                           'separator': None,
                           'class': selected and 'actionMenuSelected' or ''},
                 'submenu': None,
                 'subtype': subtype}
            result.append(d)

        return result

    def getMenuItems(self, object, request):
        try:
            return self._get_menus(object, request)
        except Exception, e:
            # it can be very difficult to troubleshoot errors here
            # because sometimes it bubbles up as AttributeError's which
            # the zope2 publisher handles in a very bizarre manner

            logger.exception(e)
            raise
