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
import zopache.pagetemplate.interfaces

class ZopachePageTemplateEval(object):

    def index(self, **kw):
        """Call a Page Template"""

        template = self.context
        request = self.request

        request.response.setHeader('content-type',
                                   template.content_type)

        return template.render(request, **kw)


class EditForm(zope.formlib.form.EditForm):
    """Edit form for Page Templates."""

    form_fields = zope.formlib.form.Fields(
            zopache.pagetemplate.interfaces.IZopachePageTemplate,
            zopache.pagetemplate.interfaces.IRenderZopachePageTemplate,
            render_context=True).omit('evaluateInlineCode')

    def setUpWidgets(self, ignore_request=False):
        self.adapters = {}

        # We need to extract the data directly, as we can not pass on the
        # request for macro expansion otherwise.
        data = {}
        data['source'] = self.context.getSource(self.request)

        self.widgets = zope.formlib.form.setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            data=data, form=self, adapters=self.adapters,
            ignore_request=ignore_request)

