### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT ulthar.net>
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


# import standard packages

# import Zope3 interfaces

# import local interfaces
from ztfy.thesaurus.interfaces.loader import IThesaurusLoaderConfiguration, IThesaurusUpdaterConfiguration, \
                                             IThesaurusExporterConfiguration

# import Zope3 packages
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

# import local packages


class ThesaurusLoaderConfiguration(object):
    """Thesaurus loader configuration"""

    implements(IThesaurusLoaderConfiguration)

    name = FieldProperty(IThesaurusLoaderConfiguration['name'])
    data = FieldProperty(IThesaurusLoaderConfiguration['data'])
    format = FieldProperty(IThesaurusLoaderConfiguration['format'])
    import_synonyms = FieldProperty(IThesaurusLoaderConfiguration['import_synonyms'])
    language = FieldProperty(IThesaurusLoaderConfiguration['language'])
    encoding = FieldProperty(IThesaurusLoaderConfiguration['encoding'])

    def __init__(self, data={}):
        if data:
            name = data.get('name')
            if name:
                self.name = name
            self.data = data.get('data')
            self.format = data.get('format')
            self.import_synonyms = data.get('import_synonyms')
            self.language = data.get('language')
            self.encoding = data.get('encoding')


class ThesaurusUpdaterConfiguration(ThesaurusLoaderConfiguration):
    """Thesaurus updater configuration"""

    implements(IThesaurusUpdaterConfiguration)

    clear = FieldProperty(IThesaurusUpdaterConfiguration['clear'])
    conflict_suffix = FieldProperty(IThesaurusUpdaterConfiguration['conflict_suffix'])

    def __init__(self, data={}):
        super(ThesaurusUpdaterConfiguration, self).__init__(data)
        if data:
            self.clear = data.get('clear')
            self.conflict_suffix = data.get('conflict_suffix')


class ThesaurusExporterConfiguration(object):
    """Thesaurus exporter configuration"""

    implements(IThesaurusExporterConfiguration)

    filename = FieldProperty(IThesaurusExporterConfiguration['filename'])
    format = FieldProperty(IThesaurusExporterConfiguration['format'])
    extract = FieldProperty(IThesaurusExporterConfiguration['extract'])

    def __init__(self, data={}):
        if data:
            self.filename = data.get('filename')
            self.format = data.get('format')
            self.extract = data.get('extract')
