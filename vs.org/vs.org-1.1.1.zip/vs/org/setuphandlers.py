################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id: setuphandlers.py 2981 2011-03-16 10:54:12Z carsten $

import os
from sets import Set
from logging import getLogger
from cStringIO import StringIO
from config import PROJECTNAME

from Products.CMFCore.utils import getToolByName
from Products.Archetypes import atapi


class Generator(object):
    def setupVocabularies(self, p, out):
        def _setup(id, filename, title_vocab):
            portal_vocab = getToolByName(p, 'portal_vocabularies')
            if id in portal_vocab.objectIds():
                portal_vocab.manage_delObjects(id)
            portal_vocab.invokeFactory('SimpleVocabulary', id=id)
            vocab = portal_vocab[id]
            vocab.setTitle(title_vocab)
            vocab.setDescription(title_vocab)
            vocab.setLanguage('')
            vocab.reindexObject()

            filename = os.path.join(os.path.dirname(__file__), 'data', filename)
            for line in file(filename):
                if not '=' in line:
                    continue
                key, value = line.split('=')
                key = key.strip()
                value = value.strip()
                vocab.invokeFactory('SimpleVocabularyTerm', id=key)
                term = vocab[key]
                term.setTitle(value)
                term.setLanguage('')
                term.reindexObject()

        _setup('number_types_employee', 'numbers_employee.txt', 'Employee')
        _setup('number_types_institution', 'numbers_institution.txt', 'Institution')
        _setup('number_types_department', 'numbers_department.txt', 'Department')
        print >> out, " Vocabularies created%s \n" 


def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('vs.org_various.txt') is None:
        return
    # Add additional setup code here
    out = StringIO()
    site = context.getSite()
    gen = Generator()
    gen.setupVocabularies(site, out)
    logger = context.getLogger(PROJECTNAME)
    logger.info(out.getvalue())

