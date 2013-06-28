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

import zope.interface
from zope.contentprovider.interfaces import IContentProvider

# DOM id and name for json tree ``<UL>`` tag
JSON_TREE_ID = u'j01Tree'
JSON_TREE_VIEW_NAME = u'@@SelectedManagementView.html'

JSON_TOGGLE_ICON_COLLAPSED = 'j01TreeCollapsedIcon'
JSON_TOGGLE_ICON_EXPANDED = 'j01TreeExpandedIcon'
JSON_TOGGLE_ICON_STATIC = 'j01TreeStaticIcon'

JSON_LI_CSS_EXPANDED = u'j01TreeExpanded'
JSON_LI_CSS_COLLAPSED = u'j01TreeCollapsed'
JSON_LI_CSS_STATIC = u'j01TreeStatic'

STATE_EXPANDED = 'expanded'
STATE_COLLAPSED = 'collapsed'
STATE_STATIC = 'static'


class IDOMContentProvider(IContentProvider):

    state = zope.interface.Attribute(
        """The collapsed, expanded or static state .""")

    childTags = zope.interface.Attribute(
        """A list of rendered child tags.""")

    viewName = zope.interface.Attribute(
        """The view name which get called on the context.""")

    collapsedCSSName = zope.interface.Attribute(
        """Class name for the collapsed <LI> tag.""")
    expandedCSSName = zope.interface.Attribute(
        """Class name for the expanded <LI> tag.""")
    staticCSSName = zope.interface.Attribute(
        """Class name for the static <LI> tag.""")

    # context icon
    iconName = zope.interface.Attribute(
        """The icon name for the context icon.""")

    # toggle icon
    collapsedIconName = zope.interface.Attribute(
        """The icon name for the collapsed icon.""")
    expandedIconNamen = zope.interface.Attribute(
        """The icon name for the expanded icon.""")
    staticIconName = zope.interface.Attribute(
        """The icon name for the static icon.""")

    # properties
    className = zope.interface.Attribute(
        """The CSS class name for the rendered <LI> tag.""")

    toggleIcon = zope.interface.Attribute(
        """The toggle icon including settings for json url.""")

    icon = zope.interface.Attribute("""The icon for the given context.""")

    name = zope.interface.Attribute("""The context name""")

    url = zope.interface.Attribute("""The context url""")

    def update():
        """Must get called before render."""

    def render():
        """Render the template."""


# content provider using templates
class ILITagProvider(IDOMContentProvider):
    """Content provider for ``LI`` tag."""


class IULTagProvider(IDOMContentProvider):
    """Content provider for ``UL`` tag."""


class ITreeProvider(IDOMContentProvider):
    """Content provider for tree (main) ``UL`` tag."""


# tree renderer interfaces
class ITreeRenderer(zope.interface.Interface):
    """Knows how to render elements fo the tree items."""

    def renderLI(item):
        """Renders <LI> tags."""

    def renderUL(item, childTags=None):
        """Renders <li> tag including rendered child tags."""

    tree = zope.interface.Attribute(
        """Renders <ul> tree tag including rendered child tags.""")


class IPythonRenderer(ITreeRenderer):
    """Uses python methods for rendering the tree items."""


class ITemplateRenderer(ITreeRenderer):
    """Uses IContentProvider classes within templates for rendereing the items.
    """


class IIdGenerator(zope.interface.Interface):
    """Knows how to get ids for the tree items."""

    def getId(item):
        """Returns the DOM id for a given object.

        Note: we encode the upper case letters because the Dom element id are 
        not case sensitive in HTML. We prefix each upper case letter with ':'.
        """

    def id():
        """Returns the DOM id for a given context."""


class IJSONTree(ITreeRenderer, IIdGenerator):
    """Complete JSON tree definition.
    
    Don't care about the javascript part, just implement all methods define in 
    this interfaces.
    """


class ISimpleJSONTree(IJSONTree):
    """Simple JSON tree implementation.
    
    Simple JSON tree using inline methods for rendering elements and
    traversable path for item lookup.
    """


class IGenericJSONTree(IJSONTree):
    """Generic JSON tree implementation.
    
    IntId base object lookup and template base rendering.
    
    This implementation uses IContentProvider for element tag rendering.
    This content provider are resonsible for represent a node. This allows us 
    to embed html or javascript calls in the html representation in a smart 
    way.
    """
