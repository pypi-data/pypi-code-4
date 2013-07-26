# -*- coding: utf-8 -*-
import os
from PIL import Image

TEMPLATE_FILE=u"""[%s]
%s=%s
"""

class RenamerError(Exception):
    pass

class ModuleBase(object):
    def __init__(self, collection, debug=False, **kwargs):
        self.collection = collection
        self.debug = debug
        self.kwargs = kwargs
        
    def go(self):
        pass

class Cover(ModuleBase):
    """
    Setup for the album directories image
    """
    cover_filename = "cover"
    image_extensions = ('png', 'jpg', 'jpeg', 'gif')
    cover_images_format = {
        'JPEG':'jpg',
        'PNG':'png',
    }
    cover_format_key = 'PNG'
    cover_size = (128, 128)
    dirConfig_filename = ".directory"
    dirConfig_section = "Desktop Entry"
    dirConfig_option = "Icon"
    dirConfig_template = TEMPLATE_FILE
    
    auto_cover = True
        
    def go(self):
        for dirKey, dirObject in self.collection.items():
            cover_path, cover_ext = self.get_cover(dirObject)
            # Tries to find a cover  image 
            if not cover_path and self.auto_cover:
                images = []
                for item in dirObject.files:
                    for ext in self.image_extensions:
                        if item.endswith(ext):
                            images.append((item, ext))
                # Selects the first image found as cover
                if len(images)>0:
                    cover_filename = images[0][0]
                    cover_ext = images[0][1]
                    cover_path = os.path.join(dirObject.get_absolute_path(), "%s.%s" % (self.cover_filename, cover_ext))
                    # Rename the image
                    if not self.debug:
                        os.renames(os.path.join(dirObject.get_absolute_path(), cover_filename), cover_path)
            # Cover manipulation
            if cover_path:
                dirObject.cover = os.path.basename(cover_path)
                dirObject.edited_cover = True
                # Force conversion to PNG
                if cover_ext != self.cover_images_format[self.cover_format_key]:
                    cover_path = self.convert_cover(cover_path)
                    cover_ext = self.cover_images_format[self.cover_format_key]
                #If a cover is available, creates the directory file
                self.make_directories_config(dirObject, cover_path)
    
    def get_cover(self, dirObject):
        for ext in self.image_extensions:
            imgname = "%s.%s" % (self.cover_filename, ext)
            tmp = os.path.join(dirObject.get_absolute_path(), imgname)
            if os.path.exists(tmp):
                return tmp, ext
        return None, None
    
    def convert_cover(self, sourcepath):
        """
        Converts the record sleeve when it's not the right format'
        """
        directory = os.path.dirname(sourcepath)
        filename = os.path.basename(sourcepath).split(".")[0]
        filename = u"%s.%s" % (filename, self.cover_images_format[self.cover_format_key])
        thumbname = os.path.join(directory, filename)
        #
        if not self.debug:
            imObj = Image.open(sourcepath)
            need_resize = self.cover_size and (imObj.size[0] > self.cover_size[0] or imObj.size[1] > self.cover_size[1])
            if imObj.format != self.cover_format_key or need_resize:
                #If dimensions are set, and the source is bigger
                #We resize it, using anti-aliasing
                if need_resize:
                    imObj = imObj.resize( self.cover_size, Image.ANTIALIAS )
                #If the image is an 8-bits image, for instance an animated gif
                #we transform it in RGB for the JPEG conversion
                if imObj.mode == "P":
                    imObj.convert("RGB")
                # Save the thumbnail
                imObj.save(thumbname, self.cover_format_key)
                # Remove the old one
                os.remove(sourcepath)
                return thumbname
        
        return sourcepath
    
    def make_directories_config(self, dirObject, cover):
        """
        Creation of the config file for the directory where a cover has been found
        """
        dirconfig_file = os.path.join( dirObject.get_absolute_path(), self.dirConfig_filename )
        content = self.dirConfig_template % (self.dirConfig_section, self.dirConfig_option, cover)
        if not self.debug:
            configFile = open(dirconfig_file, 'w')
            configFile.write( content )
            configFile.close()
    
class Renamer(ModuleBase):
    """
    Renaming of the directories and media files
    """
    def go(self):
        for dirKey, dirObject in self.collection.items():
            #print "="*60
            #print "= ITEM:", dirObject, len(dirObject.medias)
            #print dirObject.files
            item_dir = dirObject.directory
            
            # Recursive cleanup of the direcory name
            new_dir, edited = self._conditionnal_rename(dirObject.root_dir, item_dir)
            if edited:
                dirObject.directory = new_dir
                dirObject.edited_directory = True
            
            # File cleanup
            i = 0
            #print "-"*60
            for item in dirObject.medias:
                new_dir, edited = self._conditionnal_rename(dirObject.get_absolute_path(), item)
                if edited:
                    dirObject.medias[i] = new_dir
                    dirObject.edited_medias.append(new_dir)
                i += 1
    
    def _conditionnal_rename(self, root_dir, src):
        dst = self._clean_chars(src)
        if src != dst:
            absolute_src = os.path.join(root_dir, src)
            absolute_dst = os.path.join(root_dir, dst)
            if os.path.exists(absolute_dst):
                # À transformer en warning via le logger
                raise RenamerError, 'Same clean path allready exists for : %s' % src
            else:
                if not self.debug:
                    os.renames(absolute_src, absolute_dst)
                #print " ", absolute_src, "=>", absolute_dst
                return dst, True
        return src, False
    
    def _clean_chars(self, value):
        res = '_'.join( value.lower().split() )
        res = res.replace('!', '')
        res = res.replace("'", '')
        res = res.replace('"', '')
        res = res.replace(',', '')
        res = res.replace('{', '(')
        res = res.replace('}', ')')
        return res

class Stats(ModuleBase):
    """
    Prints statistics on modified elements
    """
    def go(self):
        i = 0
        foo = []
        for k,v in self.collection.items():
            if v.is_edited():
                print "="*60
                print "=", v.directory, "(%s/%s)"%(len(v.edited_medias), len(v.medias))
                if v.edited_cover:
                    print "-", "COVER:", v.cover
                for media in v.medias:
                    if media in v.edited_medias:
                        print "", "*", media
                i += 1
            else:
                foo.append(v.directory)
        print "_"*60
        print "Proceeded MusicDir : %s/%s" % (i, len(self.collection))
        print
        if len(foo)>0:
            print "="*60
            print "= %s MusicDir has not been changed :" % len(foo)
            for item in foo:
                print "*", item
            print
