from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from StringIO import StringIO
from zope.interface import classProvides
from zope.interface import implements

import urllib2
import zipfile
import lxml


class CHMReader(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.name = name
        self.options = options

    def __iter__(self):
        for item in self.previous:
            yield item

        url = self.options.get('url', None)
        if url is not None:
            sock = urllib2.urlopen(url)
            zipinmemory = StringIO(sock.read())
            zip = zipfile.ZipFile(zipinmemory)
            glossary_data = None
            for filename in zip.namelist():
                if filename == 'glossary/translations.xml':
                    glossary_data = zip.read(filename)

            if glossary_data is not None:
                glossary = lxml.etree.fromstring(glossary_data)
                folders = glossary.xpath('//folder')
                for folder in folders:
                    item = {}
                    item['_type'] = 'PloneGlossaryDefinition'
                    item['_transitions'] = 'publish'
                    item['_path'] = '/chm_terms/' + folder.get('id')
                    item['title'] = folder.get('title')
                    item['definition'] = ' '
                    names = []
                    for name in folder.xpath('name/translation'):
                        dic = {
                            'language': name.get('lang'),
                            'term': name.text
                        }
                        names.append(dic)

                    item['term_translations'] = names
                    definitions = []
                    for definition in folder.xpath('definition/translation'):
                        dic = {
                            'language': definition.get('lang'),
                            'definition': definition.text
                        }
                        definitions.append(dic)

                    item['definition_translations'] = definitions
                    yield item

                    for element in folder.xpath('element'):
                        item = {}
                        item['_type'] = 'PloneGlossaryDefinition'
                        item['_transitions'] = 'publish'
                        item['_path'] = '/chm_terms/' + folder.get('id') + '/' +  element.get('id')
                        item['title'] = element.get('title')
                        item['definition'] = ' '
                        names = []
                        for name in element.xpath('name/translation'):
                            dic = {
                                'language': name.get('lang'),
                                'term': name.text
                            }
                            names.append(dic)

                        item['term_translations'] = names
                        definitions = []
                        for definition in element.xpath('definition/translation'):
                            dic = {
                                'language': definition.get('lang'),
                                'definition': definition.text
                            }
                            definitions.append(dic)

                        item['definition_translations'] = definitions
                        yield item
