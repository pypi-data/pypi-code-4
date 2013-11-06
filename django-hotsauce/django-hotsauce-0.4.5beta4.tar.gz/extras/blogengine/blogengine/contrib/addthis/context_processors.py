#!/usr/bin/env python
"""Template context processor for adding AddThis markup
into a web page."""

from string import Template

from django.utils.html import escape as html_escape
from notmm.utils.django_settings import LazySettings

_settings = LazySettings()

__all__ = ['addthis_widget']

def addthis_widget(request):
    template = Template("""
    <!-- AddThis Button BEGIN -->
    <script type="text/javascript">var addthis_config = {data_track_clickback:true};</script>
    <a class="addthis_button"
    href="http://addthis.com/bookmark.php?v=250&amp;username=$u"><img
    src="http://s7.addthis.com/static/btn/v2/lg-bookmark-en.gif" width="125"
    height="16" alt="Bookmark and Share" style="border: none" /></a>
    <script type="text/javascript"
    src="http://s7.addthis.com/js/250/addthis_widget.js#username=$u"></script>
    <!-- AddThis Button END -->
    """)

    html = template.substitute(u=_settings.BLOGENGINE['ADDTHIS_USERNAME'])
    return {'addthis_widget' : html}

