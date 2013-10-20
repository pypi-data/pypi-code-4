# -*- coding: utf-8 -*-
import os

DEFAULT_AVAILABLE_MEDIA_EXTENSIONS = ['ogg', 'mp3', 'flac', 'wav']

class MusicDirModel(object):
    """
    Model of a directory for music pieces.
    """
    def __init__( self, directory, root_dir=None, files=[], cover=None, available_media_extensions=DEFAULT_AVAILABLE_MEDIA_EXTENSIONS ):
        self.directory = directory
        self.root_dir = root_dir
        self.files = files
        self.available_media_extensions = available_media_extensions
        self.medias = self.get_medias(files)
        self.cover = cover
        
        self.edited_cover = False
        self.edited_directory = False
        self.edited_medias = []
    
    def __str__(self):
        return self.directory
    
    def get_absolute_path(self):
        return os.path.join(self.root_dir, self.directory)
    
    def is_valid(self):
        return len(self.medias)>0
    
    def is_edited(self):
        return (self.edited_directory or self.edited_cover or len(self.edited_medias)>0)
    
    def get_medias(self, files):
        valid_items = []
        for item in files:
            ext = os.path.splitext(item)[-1]
            if ext and ext[1:] in self.available_media_extensions:
                valid_items.append(item)
        return valid_items
