# -*- coding: utf-8 -*-
import os

from models import DEFAULT_AVAILABLE_MEDIA_EXTENSIONS, MusicDirModel

class BatchDirectoryError(Exception):
    pass

class BatchDirectory(object):
    """
    Search
    """
    available_media_extensions = DEFAULT_AVAILABLE_MEDIA_EXTENSIONS
    
    def __init__(self, callables=[], debug=False):
        """
        Initialisation
        """
        self.debug = debug
        self.collection = {}
        self.callables = callables
            
    def scan(self, root_directory, followlinks=False):
        """
        Recursively get all directories
        """
        self.collection = {}
        #To avoid scanning a home directory by mistake
        #no default value. An exception is raised
        if not root_directory:
            raise BatchDirectoryError, u"Il est nécessaire de spécifier au moins le répertoire à scanner."
        # Directory scan
        self._walker(root_directory, followlinks)

    def _walker(self, root_directory, followlinks):
        """
        Recursive fetch of the record sleeves in a given directory.
        Each file is added to the final queue
        """
        #print "DIR:", root_directory
        for path, dirs, files in os.walk(root_directory, followlinks=followlinks):
            # We get rid of all empty directories
            if len(files)>0:
                relative_path = os.path.relpath(path, root_directory)
                dirObject = MusicDirModel(relative_path, root_dir=root_directory, files=files)
                if dirObject.is_valid():
                    #print "-"*60
                    #print "* ITEM:", relative_path, len(dirObject.medias)
                    self.collection[relative_path] = dirObject
            
    def proceed(self):
        """
        Recursively get all directories
        """
        # Parsing of the directory
        for item in self.callables:
            item(self.collection, debug=self.debug).go()
