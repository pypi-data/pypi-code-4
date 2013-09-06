#-*- coding:utf-8 -*-
#Module name: nameForBash
#Description: given a filename(could be include path),return a useful filename for bash
#Example : /home/user/file#\*?.name   ==>  "/home/user/file\#\\\*\?.name
#version:1.6
import re


#modify file name and file path, for bash
class nameForBash():
    def __init__(self, fileName):
        self.fileName = fileName
        if re.search('[\'"*?\\\\~`!\#$&()|\[\]{};<> ]', self.fileName):
            self.bashName = self.fileName.replace('\\', '\\\\') \
                                                 .replace('[', '\[') \
                                                 .replace("\'", "\\'") \
                                                 .replace('\"', '\\"') \
                                                 .replace('*', '\*') \
                                                 .replace('?', '\?') \
                                                 .replace('~', '\~') \
                                                 .replace('`', '\`') \
                                                 .replace('!', '\!') \
                                                 .replace("#", "\#") \
                                                 .replace('$', '\$') \
                                                 .replace('&', '\&') \
                                                 .replace('(', '\(') \
                                                 .replace(')', '\)') \
                                                 .replace('|', '\|') \
                                                 .replace(']', '\]') \
                                                 .replace('{', '\{') \
                                                 .replace('}', '\}') \
                                                 .replace(';', '\;') \
                                                 .replace('<', '\<') \
                                                 .replace('>', '\>') \
                                                 .replace(' ', '\ ')
        else:
            self.bashName = fileName
