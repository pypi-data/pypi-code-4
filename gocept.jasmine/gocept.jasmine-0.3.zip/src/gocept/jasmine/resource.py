# -*- coding: utf-8 -*-
# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

import fanstatic


MINIFIERS = {'.css': 'cssmin', '.js': 'jsmin'}
library = fanstatic.Library('gocept.jasmine', 'resources', minifiers=MINIFIERS)


jasmine_css = fanstatic.Resource(library, 'jasmine.css')
jasmine_js = fanstatic.Resource(library, 'jasmine.js')
jasmine_html = fanstatic.Resource(
    library, 'jasmine-html.js', depends=[jasmine_js])

jasmine = fanstatic.Resource(
    library,
    'setup_jasmine.js',
    depends=[jasmine_css, jasmine_html],
    bottom=False)
