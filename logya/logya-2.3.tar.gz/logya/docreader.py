# -*- coding: utf-8 -*-
import os


class DocReader:
    """A class for reading content documents."""

    def __init__(self, dir_base, parser):
        """Recurse through content directory to add files to read and parse."""

        self.dir_base = dir_base
        self.parser = parser
        self.files = []
        for root, dirs, files in os.walk(self.dir_base):
            self.files.extend([os.path.join(root, f) for f in files])


    def get_docs(self):
        """Generator that reads all docs from base directory."""

        for f in self.files:
            yield self.parser.parse(f)
