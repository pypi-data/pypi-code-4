# Copyright (c) 2012-2013 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import os.path
import pkg_resources
import pkginfo
import shutil
import sys


AUTOSUMMARY_OUTPUT = './_api/'


def set_defaults(egg=True):
    _confpy = sys._getframe(1).f_locals

    author = 'gocept'
    if egg:
        _dist = pkginfo.Develop(os.path.join('..', 'src'))
        project = _dist.name
        author = _dist.author

        release = _dist.version
        version = []
        for x in release:
            try:
                version.append(str(int(x)))
            except ValueError:
                break
        version = '.'.join(version)

    _year = datetime.date.today().year
    _year_started = _confpy.get('_year_started', _year)
    if str(_year) != str(_year_started):
        _year = u'%s-%s' % (_year_started, _year)
    copyright = u'%s %s' % (_year, author)

    source_suffix = '.txt'
    master_doc = 'index'

    needs_sphinx = '1.0'
    extensions = [
        'sphinx.ext.autosummary',
        'sphinx.ext.viewcode',
        ]

    autosummary_generate = ['api.txt']
    _autosummary_output = AUTOSUMMARY_OUTPUT

    templates_path = [
        pkg_resources.resource_filename(
            'gocept.package', 'themes/gocept/templates'),
        ]

    html_theme_path = [
        pkg_resources.resource_filename('gocept.package', 'themes')]
    html_theme = 'gocept'

    _default_sidebars = ['globaltoc.html', 'searchbox.html']
    if egg:
        _default_sidebars.insert(0, 'project-links.html')
    html_sidebars = {
        '**': _default_sidebars,
    }

    html_context = {}

    html_logo = pkg_resources.resource_filename(
        'gocept.package', 'themes/gocept/static/gocept.png')
    html_favicon = pkg_resources.resource_filename(
        'gocept.package', 'themes/gocept/static/favicon.ico')
    html_show_sourcelink = False

    for key, value in locals().items():
        if key not in _confpy:
            _confpy[key] = value

    # We use the autosummary extension to build API docs from source code.
    # However, this extension doesn't update the generated docs if the source
    # files change. Therefore, we need to remove the generated stuff before
    # each run. The _autosummary_output variable tells the relative path to
    # the directory that autosummary uses to put its generated files and which
    # we, therefore, need to remove. It must be the same that the autosummary
    # directive in api.txt points to.

    if os.path.isdir(_autosummary_output):
        shutil.rmtree(_autosummary_output)
    elif os.path.exists(_autosummary_output):
        raise RuntimeError('Expected %s to be a directory.' %
                           os.path.abspath(_autosummary_output))
    os.mkdir(_autosummary_output)
