# -*- coding: utf-8 -*-

# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2011 R Pratap Chakravarthy

from pluggdapps.plugin import Interface

__all__ = [ 'ITTLBreadCrumbs', 'ITTLFooter' ]

class ITTLBreadCrumbs( Interface ):
    """Interface for template plugins providing breadcrumb navigation."""

    def render( navigate, crumbsmenu, **kwargs ):
        """Generate and return HTML for breadcrumb widget.

        ``navigate``,
            List of tuples (name, url) providing the name of the bread-crumb
            and optional url.

        ``breadmenu``,
            Map of breadcrumb name, provided in ``navigate`` attribute, and a
            list of tuple (name, url). Each tuple is rendered as a menu-item.

        Optional keyword arguments,

        ``id``,
            If specified will be used as **id** attribute for the widget node.
        """


class ITTLFooter( Interface ):
    """Interface to render pluggdapps official footer."""

    def render( counts, **kwargs ):
        """Generate and return HTML pluggdapps footer.

        ``counts``,
            A dictionary of, number of interfaces and number plugin count.

        Optional keyword arguments,

        ``id``,
            If specified will be used as **id** attribute for the widget node.
        """


