

session.create_entity('NerProcess', name=u'dbpedia38-en', host=u'ner',
                      type=u'rql', lang=u'en',
                      request=u'Any U WHERE X label %(token)s, X cwuri U, '
                      'X ner_source NS, NS name "dbpedia38-en"')
