# -*- coding: utf-8 -*-
""" GenericSetup import and export support
"""

from xml.dom.minidom import Document

from zope.interface import implements
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.interface import noLongerProvides

from zope.component import adapts
from zope.component import getSiteManager
from zope.component import queryMultiAdapter
from zope.component import getMultiAdapter

from zope.component.interfaces import IComponentRegistry

from zope.annotation.interfaces import IAnnotations

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import ISetupEnviron

from Products.GenericSetup.utils import XMLAdapterBase
from Products.CMFCore.utils import getToolByName

from redturtle.custommenu.factories.config import ANN_CUSTOMMENU_KEY
from redturtle.custommenu.factories.interfaces import ICustomMenuEnabled
from redturtle.custommenu.factories.exportimport.interfaces import \
    ICustomMenuFactoriesAssignment

# TODO:
# Move this adapter inside the adapters directory and rename
# it to be used in views and other places where is necessary
# access and manipulate the annotations.
class CustomMenuFactoriesAssignment(object):
    """Custom menu factories support
    """
    implements(ICustomMenuFactoriesAssignment)
    adapts(Interface)

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(self.context)

        self._metadata = annotations.get(ANN_CUSTOMMENU_KEY, None)
        if self._metadata is None:
            annotations[ANN_CUSTOMMENU_KEY] = ({'inherit': True}, [])
            self._metadata = annotations[ANN_CUSTOMMENU_KEY]

    def remove(self):
        """Disable local customizations, delete the annotation
        """
        annotations = IAnnotations(self.context)
        annotations.__delitem__(ANN_CUSTOMMENU_KEY)

    @property
    def inherit(self):
        """True if the custom menu factories is inheriting settings
        """
        return self._metadata[0]['inherit']

    def setInherit(self, inherit):
        """Change the inherit value
        """
        self._metadata[0]['inherit'] = inherit

    def addMenuEntry(self, item):
        """Add new custom menu entry
        """
        index = self._find(item)
        if index is None:
            item['index'] = len(self.listMenuEntries())
            self._metadata[1].append(item)
        else:
            self._override(index, item)

    def removeMenuEntry(self, item):
        """Remove a custom menu entry
        """
        index = self._find(item)
        if index is None:
            return

        xss = self._metadata[1][:index] + self._metadata[1][index+1:]
        if len(xss) > index:
            for idx in xrange(index, len(xss[1][index:]) + 1):
                xss[idx]['index'] = idx

        self._update(self.inherit, xss)

    def listMenuEntries(self):
        """List of the menu entries
        """
        return self._metadata[1]

    def _update(self, inherit, xss):
        """Update the tuple with a new list
        """
        annotations = IAnnotations(self.context)
        annotations[ANN_CUSTOMMENU_KEY] = ({'inherit': inherit}, xss)
        self._metadata = annotations[ANN_CUSTOMMENU_KEY]

    def _find(self, item):
        """Return the current index value of 'item' or None if is not there
        """
        index = None
        for entry in self.listMenuEntries():
            if entry['element-id'] == item['element-id']:
                index = entry['index']
                break

        return index

    def _override(self, index, item):
        """Override a entry
        """
        item['index'] = index
        xss = self._metadata[1][:index] + [item] + self._metadata[1][index+1:]
        self._update(self.inherit, xss)


class CustomMenuFactoriesXMLAdapter(XMLAdapterBase):
    """In- and exporter for a local custom menu configuration
    """
    implements(IBody)
    adapts(IComponentRegistry, ISetupEnviron)

    name = 'custommenu'
    _LOGGER_ID = 'custommenu.factories'

    #####################################
    #       Main control flow           #
    #####################################

    def _exportNode(self):
        """Export custom Menu settings
        """
        node = self._extractCustomMenu()
        self._logger.info('Custom Menu Factories exported')
        return node

    def _importNode(self, node):
        """Import custom menu settings
        """
        self._initCustomMenu([], node)
        self._logger.info('Custom Menu Factories imported')

    #####################################
    #           Importing               #
    #####################################

    def _initCustomMenu(self, path, node):
        """Walk recursively through the xml dom, and the portal site,
           to set the customm menues into the objects identified by the path.
        """
        name = node.getAttribute('name').lower()

        request = self.context.REQUEST
        portal = getMultiAdapter((self.context, request),
                                  name=u'plone_portal_state').portal()

        if not name and isinstance(node.parentNode, Document):
            path.append(portal.getId())
        elif not name:
            msg = "node object '%s' has no attribute 'name'" % node.nodeName
            raise AttributeError(msg)
        else:
            path.append(name)

        context = portal.restrictedTraverse(path)
        if context is None:
            msg = "object not fount: %s " % '/'.join(path)
            raise AttributeError(msg)

        if node.hasAttribute('purge'):
            purge = self._convertToBoolean(node.getAttribute('purge'))
            if purge:
                self._purgeCustomMenu(context)

        for child in node.childNodes:
            # set the inherit property
            if child.nodeName.lower() == 'property':
                self._initCustomMenuInheritProperty(context, child)

            # set custom menu entries
            elif child.nodeName.lower() == 'custommenu':
                self._initCustomMenuNode(context, child)

            # recursive down into the objects
            elif child.nodeName.lower() == 'object':
                self._initCustomMenu(path, child)

    def _initCustomMenuInheritProperty(self, context, node):
        """Enable the Custom Menu and set the inherit property in the context
        """
        if node.getAttribute('name').lower() == 'inherit':
            inherit = self._convertToBoolean(self._getNodeText(node))
            # set the inherit property in the container
            annotation = ICustomMenuFactoriesAssignment(context)
            alsoProvides(context, ICustomMenuEnabled)
            if not inherit:
                annotation.setInherit(False)
            context.reindexObject(idxs=['object_provides'])

    def _initCustomMenuNode(self, context, node):
        """Create a new menu entry and add it into the context
        """
        menuElement = {'element-id':      '',
                       'element-name':    '',
                       'element-descr':   '',
                       'icon-tales':      '',
                       'condition-tales': '',
                       'element-tales':   '',
                      }

        for child in node.childNodes:
            if child.nodeName.lower() == 'property':
                name = child.getAttribute('name').lower()
                if name in menuElement:
                    menuElement[name] = self._getNodeText(child)
        # TODO
        #self._validateCustomMenuElement(menuElement)

        context = ICustomMenuFactoriesAssignment(context)
        context.addMenuEntry(menuElement)

    #####################################
    #           Exporting               #
    #####################################

    def _extractCustomMenu(self):
        """Finds all objects marked with the ICustomMenuEnabled interface
           and export these, with their settings into a XML dom
        """
        request = self.context.REQUEST
        portal = getMultiAdapter((self.context, request),
                                  name=u'plone_portal_state').portal()
        portal_catalog = getToolByName(portal, 'portal_catalog')
        ppath = len(portal.getPhysicalPath())
        node = self._doc.createElement('object')
        node = self._exportCustomMenuNode(portal, [], node)

        query = dict(object_provides=ICustomMenuEnabled.__identifier__)
        brains = portal_catalog.searchResults(query)
        for brain in brains:
            obj = brain.getObject()
            path = list(obj.getPhysicalPath()[ppath:])
            node = self._exportCustomMenuNode(obj, path, node)

        return node

    def _exportCustomMenuNode(self, obj, path, node):
        """Create the xml dom recursively until found node for the current
           object, then export the settings from the object into the node.
        """
        if path:
            name = path.pop(0)
            subnode = None
            for child in node.childNodes:
                if child.nodeName == 'object' \
                and child.getAttribute('name') == name:
                    subnode = child
                    break

            if subnode is None:
                subnode = self._doc.createElement('object')
                subnode.setAttribute('name', name)

            node.appendChild(self._exportCustomMenuNode(obj, path, subnode))

        else:
            node = self._exporNodeSettings(obj, node)

        return node

    def _exporNodeSettings(self, obj, node):
        """Export the object settings into a node
        """
        annotation = ICustomMenuFactoriesAssignment(obj)
        property = self._doc.createElement('property')
        property.setAttribute('name', 'inherit')
        text = self._doc.createTextNode(unicode(annotation.inherit))
        property.appendChild(text)
        node.appendChild(property)

        for entry in annotation.listMenuEntries():
            custommenu = self._doc.createElement('custommenu')
            for name, value in entry.iteritems():
                if name != 'index':
                    property = self._doc.createElement('property')
                    property.setAttribute('name', name)
                    text = self._doc.createTextNode(value)
                    property.appendChild(text)
                    custommenu.appendChild(property)

            node.appendChild(custommenu)

        return node

    #####################################
    #           Purge                   #
    #####################################

    def _purgeCustomMenu(self, context):
        """Remove the interface and annotation from an object
        """
        if ICustomMenuEnabled.providedBy(context):
            annotation = ICustomMenuFactoriesAssignment(context)
            annotation.remove()
            noLongerProvides(context, ICustomMenuEnabled)
            context.reindexObject(idxs=['object_provides'])

    #####################################
    #           Helpers                 #
    #####################################
    # TODO
    # Helper
    #def _validateCustomMenuElement(self, element):
    #    return True


def importCustomMenuFactories(context):
    """Import custommenu configurations
    """
    sm = getSiteManager(context.getSite())
    if sm is None or not IComponentRegistry.providedBy(sm):
        logger = context.getLogger('custommenu.factories')
        logger.info("Can not register components - no site manager found.")
        return

    importer = queryMultiAdapter((sm, context), IBody,
                                  name=u'redturtle.custommenu.factories')
    if importer:
        filename = '%s%s' % (importer.name, importer.suffix)
        body = context.readDataFile(filename)
        if body is not None:
            importer.filename = filename  # for error reporting
            importer.body = body


def exportCustomMenuFactories(context):
    """Export custommenu configuration
    """
    sm = getSiteManager(context.getSite())
    if sm is None or not IComponentRegistry.providedBy(sm):
        logger = context.getLogger('custommenu.factories')
        logger.info("Nothing to export.")
        return

    exporter = queryMultiAdapter((sm, context), IBody,
                                 name=u'redturtle.custommenu.factories')
    if exporter:
        filename = '%s%s' % (exporter.name, exporter.suffix)
        body = exporter.body
        if body is not None:
            context.writeDataFile(filename, body, exporter.mime_type)
