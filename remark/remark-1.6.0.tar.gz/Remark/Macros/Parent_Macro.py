# -*- coding: utf-8 -*-

# Description: Parent macro
# Detail: Generates a link to the parent documentation.

# Remark 1.6.0
# Copyright (c) 2009 - 2013 
# Kalle Rutanen
# Distributed under the MIT license (see license.txt).

from Remark.Macro_Registry import registerMacro
from Remark.FileSystem import unixRelativePath
from Remark.DocumentType_Registry import outputDocumentName

class Parent_Macro(object):
    def name(self):
        return 'Parent'

    def expand(self, parameter, remark):
        text = []

        document = remark.document
        parent = document.parent

        text = [remark.remarkLink('Back to ' + parent.linkDescription(),
                                  document, parent)]

        return text

    def outputType(self):
        return 'remark'

    def expandOutput(self):
        return False

    def htmlHead(self, remark):
        return []                

    def postConversion(self, remark):
        None

registerMacro('Parent', Parent_Macro())

