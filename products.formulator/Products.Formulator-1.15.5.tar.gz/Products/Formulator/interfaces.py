# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: interfaces.py 50862 2013-05-23 11:53:50Z sylvain $

from zope import interface


class IField(interface.Interface):
    """A formulator field.
    """


class IForm(interface.Interface):
    """A formulator form.
    """

