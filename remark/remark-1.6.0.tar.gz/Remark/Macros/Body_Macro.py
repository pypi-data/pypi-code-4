# -*- coding: utf-8 -*-

# Description: Body macro
# Detail: Reads a document from file.

# Remark 1.6.0
# Copyright (c) 2009 - 2013 
# Kalle Rutanen
# Distributed under the MIT license (see license.txt).

from Remark.FileSystem import readFile, globalOptions
from Remark.Macro_Registry import registerMacro

class Body_Macro(object):
    def name(self):
        return 'Body'

    def expand(self, parameter, remark):
        document = remark.document
        fileName = remark.documentTree.fullName(document);

        text = readFile(fileName, globalOptions().maxFileSize)

        return text
    
    def outputType(self):
        return 'remark'

    def expandOutput(self):
        return True
    
    def htmlHead(self, remark):
        return []                

    def postConversion(self, remark):
        None

registerMacro('Body', Body_Macro())
