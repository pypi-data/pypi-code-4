# -*- coding: utf-8 -*-
import logging

from plone.app.layout.viewlets import common as base

from collective.liches import lichesMessageFactory as _
from collective.liches.interfaces import ILichesSettingsSchema

class BrokenLinksViewlet(base.ViewletBase):

    def get_js(self):
        template = """
        /*<![CDATA[*/
        $(document).ready(function() {
            var url =  '%s/@@liches-ajax-insert.html';
            jQuery.get(url,
                function(data) {
                    $('#liches-container').html(data);
            });
        });/*]]>*/"""
        return template % self.context.absolute_url()
