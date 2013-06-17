##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
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
"""Json directives

Directives of the 'http://namespaces.zope.org/json'
namespace

This is based on how it is done in Five, since we really want
to extend its behaviour only to allow traversals to json pages
"""
import os

from inspect import ismethod

from zope.interface import Interface
from zope.configuration.exceptions import ConfigurationError

from zope.publisher.interfaces.browser import IDefaultBrowserLayer

try:  # Plone 4.3
   from zope.browserpage.metaconfigure import _handle_for
   from zope.browserpage.metaconfigure import _handle_menu
except ImportError:  # Plone < 4.3
   from zope.app.publisher.browser.viewmeta import _handle_for, _handle_menu

try:
    from zope.component.zcml import handler
except ImportError:
    from zope.app.component.metaconfigure import handler

from Products.Five.browser import BrowserView
try: # Zope 2.13
    from AccessControl.security import CheckerPrivateId
    from AccessControl.security import getSecurityInfo
    from AccessControl.security import protectClass
    from AccessControl.security import protectName
    from App.class_init import InitializeClass
except ImportError:  # Zope < 2.13
    from Products.Five.security import CheckerPrivateId
    from Products.Five.security import getSecurityInfo
    from Products.Five.security import protectClass
    from Products.Five.security import protectName
    from Products.Five.security import initializeClass as InitializeClass

from Products.Five.metaclass import makeClass
from Products.Five.browser.metaconfigure import \
     ViewMixinForAttributes, makeClassForTemplate

from interfaces import IJsonRequest

def page(_context, name, permission, for_,
         layer=IDefaultBrowserLayer, template=None, class_=None,
         allowed_interface=None, allowed_attributes=None,
         attribute='__call__', menu=None, title=None,
         ):

    _handle_menu(_context, menu, title, [for_], name, permission)

    if not (class_ or template):
        raise ConfigurationError("Must specify a class or template")
    if allowed_attributes is None:
        allowed_attributes = []
    if allowed_interface is not None:
        for interface in allowed_interface:
            allowed_attributes.extend(interface.names(all=True))

    if attribute != '__call__':
        if template:
            raise ConfigurationError(
                "Attribute and template cannot be used together.")

        if not class_:
            raise ConfigurationError(
                "A class must be provided if attribute is used")

    if template:
        template = os.path.abspath(str(_context.path(template)))
        if not os.path.isfile(template):
            raise ConfigurationError("No such file", template)

    if class_:
        if attribute != '__call__':
            if not hasattr(class_, attribute):
                raise ConfigurationError(
                    "The provided class doesn't have the specified attribute "
                    )
        cdict = getSecurityInfo(class_)
        cdict['__name__'] = name
        if template:
            new_class = makeClassForTemplate(template, bases=(class_, ),
                                             cdict=cdict, name=name)
        elif attribute != "__call__":
            # we're supposed to make a page for an attribute (read:
            # method) and it's not __call__.  We thus need to create a
            # new class using our mixin for attributes.
            cdict.update({'__page_attribute__': attribute})
            new_class = makeClass(class_.__name__,
                                  (class_, ViewMixinForAttributes),
                                  cdict)

            # in case the attribute does not provide a docstring,
            # ZPublisher refuses to publish it.  So, as a workaround,
            # we provide a stub docstring
            func = getattr(new_class, attribute)
            if not func.__doc__:
                # cannot test for MethodType/UnboundMethod here
                # because of ExtensionClass
                if hasattr(func, 'im_func'):
                    # you can only set a docstring on functions, not
                    # on method objects
                    func = func.im_func
                func.__doc__ = "Stub docstring to make ZPublisher work"
        else:
            # we could use the class verbatim here, but we'll execute
            # some security declarations on it so we really shouldn't
            # modify the original.  So, instead we make a new class
            # with just one base class -- the original
            new_class = makeClass(class_.__name__,
                                  (class_, BrowserView), cdict)

    else:
        # template
        new_class = makeClassForTemplate(template, name=name)

    _handle_for(_context, for_)

    _context.action(
        discriminator = ('view', for_, name, IJsonRequest, layer),
        callable = handler,
        args = ('registerAdapter',
                new_class, (for_, layer), Interface, name, _context.info),
        )
    _context.action(
        discriminator = ('five:protectClass', new_class),
        callable = protectClass,
        args = (new_class, permission)
        )
    if allowed_attributes:
        for attr in allowed_attributes:
            _context.action(
                discriminator = ('five:protectName', new_class, attr),
                callable = protectName,
                args = (new_class, attr, permission)
                )
    # Make everything else private
    allowed = [attribute] + (allowed_attributes or [])
    private_attrs = [name for name in dir(new_class)
                     if (not name.startswith('_')) and
                        (name not in allowed) and
                        ismethod(getattr(new_class, name))]
    for attr in private_attrs:
        _context.action(
            discriminator = ('five:protectName', new_class, attr),
            callable = protectName,
            args = (new_class, attr, CheckerPrivateId)
            )
    # Protect the class
    _context.action(
        discriminator = ('five:initialize:class', new_class),
        callable = InitializeClass,
        args = (new_class,)
        )
