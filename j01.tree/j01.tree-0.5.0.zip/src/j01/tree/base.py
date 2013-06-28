##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

"""
$Id: __init__.py 6 2006-04-16 01:28:45Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import string
import zope.interface
import zope.component
from zope.pagetemplate.interfaces import IPageTemplate
from zope.traversing import api
from zope.security.interfaces import Unauthorized
from zope.security.interfaces import Forbidden
from zope.traversing.browser import absoluteURL
from zope.traversing.namespace import getResource
from zope.contentprovider.interfaces import IContentProvider
from zope.container.interfaces import IReadContainer
from zope.component import hooks

from z3c.template.template import getPageTemplate

from j01.tree import interfaces
from j01.tree.interfaces import JSON_TREE_ID
from j01.tree.interfaces import JSON_TREE_VIEW_NAME
from j01.tree.interfaces import JSON_TOGGLE_ICON_COLLAPSED
from j01.tree.interfaces import JSON_TOGGLE_ICON_EXPANDED
from j01.tree.interfaces import JSON_TOGGLE_ICON_STATIC
from j01.tree.interfaces import JSON_LI_CSS_EXPANDED
from j01.tree.interfaces import JSON_LI_CSS_COLLAPSED
from j01.tree.interfaces import JSON_LI_CSS_STATIC
from j01.tree.interfaces import STATE_EXPANDED
from j01.tree.interfaces import STATE_COLLAPSED
from j01.tree.interfaces import STATE_STATIC
from j01.tree import util


class TreeBase(object):
    """Tree iterator base implementation."""

    root = None
    childTags = None
    rootChilds = None
    items = []

    j01TreeId = JSON_TREE_ID
    j01TreeName = JSON_TREE_ID
    j01TreeClass = JSON_TREE_ID

    viewName = JSON_TREE_VIEW_NAME

    # LI tag CSS names
    expandedCSSName = JSON_LI_CSS_EXPANDED
    collapsedCSSName = JSON_LI_CSS_COLLAPSED
    staticCSSName = JSON_LI_CSS_STATIC

    # toggle icon names
    collapsedIconName = JSON_TOGGLE_ICON_COLLAPSED
    expandedIconNamen = JSON_TOGGLE_ICON_EXPANDED
    staticIconName = JSON_TOGGLE_ICON_STATIC

    def getRoot(self):
        if not self.root:
            self.root = hooks.getSite()
        return self.root

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getSubItems(self, item):
        items = []
        append = items.append
        if IReadContainer.providedBy(item):
            keys = list(item.keys())
        else:
            keys = []
        for name in keys:
            # Only include items we can traverse to
            subItem = api.traverse(item, name, None)
            if subItem is not None:
                append(subItem)
        return items

    def getIconURL(self, item, request, name='icon'):
        return util.getIconURL(item, request, name=name)

    def getParents(self):
        root = self.getRoot()
        return util.getParentsFromContextToObject(self.context, root)

    def hasSubItems(self, item):
        res = False
        if IReadContainer.providedBy(item):
            try:
                if len(item) > 0:
                    res = True
            except(Unauthorized, Forbidden):
                pass
        return res

    def update(self):
        """Setup HTML code for representing an <ul> tag tree with the 
        siblings and parents of an object.

        There is only one branch expanded, in other words, the tree is
        filled with the object, its siblings and its parents with
        their respective siblings. This tree is stateless.

        If we access the tree via a virtual host, the root is adjusted to
        the right root object.

        """
        childTags = None
        stackItem = self.context
        parents = self.getParents()

        for item in parents:
            tagList = []
            append = tagList.append

            for subItem in self.getSubItems(item):
                if self.hasSubItems(subItem):

                    if subItem == stackItem:
                        append(self.renderUL(subItem, childTags))
                    else:
                        append(self.renderUL(subItem))

                else:
                    append(self.renderLI(subItem))

            childTags = ' '.join(tagList)
            stackItem = item

        self.childTags = childTags


class PythonRendererMixin(object):
    """Mixin class for template less tree generation.
    
    This renderer is responsible for rendering all HTML elements for the items
    found in the tree. This means evrey item will be presented in the same way.
    Use this renderer only if you like to get the same representation for each
    item. If you need custom representation for each item, use the template 
    based renderer which allows you to define for each item a custom class and
    template.
    """

    startCollapsed = False

    @property
    def rootName(self):
        root = self.getRoot()
        name = api.getName(self.root)
        if not name:
            name = u'[top]'
        return name

    def isSelected(self, item):
        return False

    def getToggleIcon(self, item, state):
        """Returns a toggle icon including settings for json url."""
        if state == STATE_COLLAPSED:
            iconName = self.collapsedIconName
        elif state == STATE_EXPANDED:
            iconName = self.expandedIconNamen
        else:
            iconName = self.staticIconName
        icon = zope.component.getMultiAdapter((item, self.request), 
            name=iconName)
        resource = getResource(icon.context, icon.rname, self.request)
        src = resource()
        longDescURL = absoluteURL(item, self.request)
        return ('<img src="%s" alt="toggle icon" width="%s" height="%s" ' 
                'border="0" longDesc="%s" />' % (src, icon.width, 
                   icon.height, longDescURL))

    def renderLI(self, item):
        name = api.getName(item)
        url = absoluteURL(item, self.request) +'/'+ self.viewName
        iconURL = self.getIconURL(item, self.request)
        id = self.getId(item)
        if self.isSelected(item):
            aCSS = ' class="selected"'
        else:
            aCSS = ''

        res = u''
        toggleIcon = self.getToggleIcon(item, STATE_STATIC)
        res += '<li id="%s" class="j01TreeItem">%s' % (id, toggleIcon)
        if iconURL != '':
            res += '<img src="%s" width="16" height="16" />' % iconURL
        res += '<a href="%s"%s>%s</a>' % (url, aCSS, name)
        res += '</li>'
        return res

    def renderUL(self, item, childTags=None):
        """Renders <li> tag with already rendered child tags."""
        name = api.getName(item)
        url = absoluteURL(item, self.request) +'/'+ self.viewName
        iconURL = self.getIconURL(item, self.request)
        id = self.getId(item)

        if item == self.context:
            state = STATE_COLLAPSED
            liClass = self.collapsedCSSName
        else:
            state = STATE_EXPANDED
            liClass = self.expandedCSSName

        if childTags is None:
            state = STATE_COLLAPSED
            liClass = self.collapsedCSSName
        
        toggleIcon = self.getToggleIcon(item, state)

        res = u''
        res +=  '<li id="%s" class="%s">%s' % (id, liClass, toggleIcon)
        if iconURL != '':
            res += '<img src="%s" class="" width="16" height="16" />' % iconURL
        res += '<a href="%s">%s</a>' % (url, name)
        res += '  <ul>'
        if childTags is not None:
            res += '    %s' % childTags
        res += '  </ul>'
        res += '</li>'
        return res

    @property
    def tree(self):
        root = self.getRoot()
        if root is None:
            raise ValueError("Missing tree root object.")
        id = self.getId(root)
        rootName = self.rootName
        url = absoluteURL(root, self.request) +'/'+ self.viewName

        # setup root item
        if self.childTags is None:
            rootChilds = ''
            liClass = self.collapsedCSSName
            state = STATE_COLLAPSED
        elif self.startCollapsed:
            rootChilds = '<ul>%s</ul>' % self.childTags
            liClass = self.collapsedCSSName
            state = STATE_COLLAPSED
        else:
            rootChilds = '<ul>%s</ul>' % self.childTags
            liClass = self.expandedCSSName
            state = STATE_EXPANDED

        # setup root toggle icon
        toggleIcon = self.getToggleIcon(self.context, state)

        # setup root link
        rootLink = '<a href="%s">%s</a>' % (url, rootName)
        rootItem = '<li id="%s" class="%s">%s%s%s</li>' % \
            (id, liClass, toggleIcon, rootLink, rootChilds)

        # render the <ul> tag tree
        j01Tree = u''
        j01Tree += '<ul class="%s" id="%s" name="%s">%s</ul>' % (
            self.j01TreeClass, self.j01TreeId, self.j01TreeName, rootItem)
        return j01Tree


class TemplateRendererMixin(object):
    """Mixin class for template based tree generation.
    
    This implementation uses IContentProvider for element tag rendering. This 
    makes it very flexible.
    
    Note: Don't forget to define custom JSONTreeItems methods which reflect the
    custom rendering. Or you will get the default rendering behavior for JSON
    loaded items.
    """

    zope.interface.implements(interfaces.ITemplateRenderer)

    startCollapsed = False

    def renderLI(self, item):
        provider = zope.component.getMultiAdapter(
            (item, self.request, self), IContentProvider, 
            self.liProviderName)
        provider.state = STATE_STATIC
        provider.update()
        return provider.render()

    def renderUL(self, item, childTags=None):
        """Renders <li> tag with already rendered child tags."""
        if item == self.context:
            state = STATE_COLLAPSED
        else:
            state = STATE_EXPANDED

        if childTags is None:
            state = STATE_COLLAPSED

        provider = zope.component.getMultiAdapter(
            (item, self.request, self), IContentProvider, 
            self.ulProviderName)
        provider.childTags = childTags
        provider.state = state
        provider.update()
        return provider.render()

    @property
    def tree(self):
        root = self.getRoot()
        if root is None:
            raise ValueError("Missing tree root object.")

        if self.childTags is None:
            state = STATE_COLLAPSED
        elif self.startCollapsed:
            state = STATE_COLLAPSED
        else:
            state = STATE_EXPANDED

        provider = zope.component.getMultiAdapter(
            (root, self.request, self), IContentProvider, 
            self.treeProviderName)
        provider.childTags = self.childTags
        provider.state = state
        provider.update()
        return provider.render()


class IdGeneratorMixin(object):
    """This mixin class generates Object Ids based on the the objects path.

    Note: The objects must be traversable by it's path. You can implement a 
    a custom path traverse concept in the getObjectByPath it you need to use
    another traverse concept.

    This ids must conform the w3c recommendation described in:
    http://www.w3.org/TR/1999/REC-html401-19991224/types.html#type-name
    """

    def getId(self, item):
        """Returns the DOM id for a given object.

        Note: we encode the upper case letters because the Dom element id are 
        not case sensitive in HTML. We prefix each upper case letter with ':'.
        """
        path = api.getPath(item)
        newPath = u''
        for letter in path:
            if letter in string.uppercase:
                newPath += ':' + letter
            else:
                newPath += letter
        
        # we use a dot as a root representation, this also avoids to get the 
        # same id for the ul and the first li tag
        if newPath == '/':
            newPath = '.'
        # add additinal dot which separates the tree id and the path, this is
        # used for get the tree id out of the string in the javascript using 
        # ids = id.split("."); treeId = ids[0];
        id = self.j01TreeId +'.'+ newPath
        # convert '/' path separator to marker '::', because the path '/'' is  
        # not allowed as DOM id. See also:
        # http://www.w3.org/TR/1999/REC-html401-19991224/types.html#type-name
        return id.replace('/', '::')

    def id(self):
        """Returns the DOM id for a given context."""
        return self.getId(self.context)


class ProviderBase(object):
    """Base class for element provider."""

    template = getPageTemplate()

    state = None
    childTags = None
    viewName = u'@@SelectedManagementView.html'
    iconName = 'icon'

    # LI tag CSS names
    collapsedCSSName = JSON_LI_CSS_COLLAPSED
    expandedCSSName = JSON_LI_CSS_EXPANDED
    staticCSSName = JSON_LI_CSS_STATIC

    # toggle icon names
    collapsedIconName = JSON_TOGGLE_ICON_COLLAPSED
    expandedIconNamen = JSON_TOGGLE_ICON_EXPANDED
    staticIconName = JSON_TOGGLE_ICON_STATIC

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    @property
    def className(self):
        if self.state == STATE_COLLAPSED:
            return self.collapsedCSSName
        elif self.state == STATE_EXPANDED:
            return self.expandedCSSName
        else:
            return self.staticCSSName

    def isSelected(self, item):
        return False

    @property
    def aCSS(self):
        if self.isSelected(item):
            aCSS = ' class="selected"'
        else:
            aCSS = ''

    @property
    def toggleIcon(self):
        """Returns a toggle icon including settings for json url."""
        if self.state == STATE_COLLAPSED:
            iconName = self.collapsedIconName
        elif self.state == STATE_EXPANDED:
            iconName = self.expandedIconNamen
        else:
            iconName = self.staticIconName
        icon = zope.component.getMultiAdapter((self.context, self.request), 
            name=iconName)
        resource = getResource(icon.context, icon.rname, self.request)
        src = resource()
        longDescURL = absoluteURL(self.context, self.request)
        return ('<img src="%s" alt="toggle icon" width="%s" height="%s" ' 
                'border="0" longDesc="%s" />' % (src, icon.width, 
                   icon.height, longDescURL))

    def icon(self):
        """Returns a toggle icon including settings for json url."""
        icon = zope.component.queryMultiAdapter((self.context, self.request), 
            name=self.iconName)
        if icon is not None:
            resource = getResource(icon.context, icon.rname, self.request)
            src = resource()
            longDescURL = absoluteURL(self.context, self.request)
            return ('<img src="%s" alt="toggle icon" width="%s" height="%s" ' 
                    'border="0" />' % (src, icon.width, icon.height))
        return u''

    @property
    def name(self):
        return api.getName(self.context)

    @property
    def url(self):
        return absoluteURL(self.context, self.request) +'/'+ self.viewName

    def update(self):
        pass

    def render(self):
        template = zope.component.getMultiAdapter((self, self.request), 
            IPageTemplate)
        return template(self)

