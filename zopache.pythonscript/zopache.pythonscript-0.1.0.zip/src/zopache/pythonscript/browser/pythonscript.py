##############################################################################
#
# Copyright (c) 2013 Christopher Lozinski (lozinski@freerecruiting.com).
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
"""Define view component for Page Templates eval results."""
import zope.formlib.form
import zopache.pythonscript.interfaces

class EditForm(zope.formlib.form.EditForm):
    """Edit form for Page Templates."""

    form_fields = zope.formlib.form.Fields(
            zopache.pythonscript.interfaces.IPythonScript,
            render_context=True)

    #def setUpWidgets(self, ignore_request=False):
    #    self.adapters = {}
    #    data = {}
    #    self.widgets = zope.formlib.form.setUpWidgets(
    #        self.form_fields, self.prefix, self.context, self.request,
    #        data=data, form=self, adapters=self.adapters,
    #        ignore_request=ignore_request)

