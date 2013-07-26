#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
__title__ = "Batch directories cover Class"
__version__ = "0.2.0"
__author__ = "Thenon David"
__copyright__ = "Copyright (c) 2008-2009 sveetch.biz"
__license__ = "GPL"

import os, re, sys
from PIL import Image

TEMPLATE_FILE=u"""[%s]
%s=%s
"""

class BatchDirCovers:
    """
    Moulinette qui cherche récursivement toute les 'jaquettes' d'un répertoire.
    Pour chaque répertoire, analyse si il trouve une jaquette, si oui il crée 
    un '.directory' pour y renseigner le fichier de la jaquette.
    
    TODO: Utiliser PIL si il est installé, pour convertir à la volée les 
    jaquettes dans le bon format
    """
    def __init__( self, directory=None, cover_filename="cover", ini_filename=".directory", 
                    section_name="Desktop Entry", option_name="Icon", template=TEMPLATE_FILE, 
                    cover_format='JPEG', cover_size=(48, 48), debug_mode=False ):
        """
        Initialisation
        """
        self.directory = directory
        # Pour éviter le scan de tout un home par erreur, pas de valeure par 
        # défaut, de plus on lève une erreure.
        if not self.directory:
            raise BatchDirCoversError, u"Il est nécessaire de spécifier au moins le répertoire à scanner."
            #sys.exit(0)
        self.cover_filename = cover_filename
        self.image_extensions = ('jpg', 'jpeg', 'png', 'gif')
        self.cover_images_format = {
            'JPEG':'jpg',
            'PNG':'png',
        }
        self.debug_mode = debug_mode
        
        # Attributs internes
        self.target_covers = []
        self.warnings = []
        self.template = template
        self.cover_format_key = cover_format
        self.cover_size = cover_size
        self.dirConfig_filename = ini_filename
        self.dirConfig_section = section_name
        self.dirConfig_option = option_name
        
        # Lance le scan
        self.scan_target()
            
    def scan_target(self):
        """
        Récupère récursivement toute les jaquettes de répertoires, les ajoutes 
        dans la file de traitement, puis lance le traitement dessus.
        """
        # Scan du répertoire
        os.path.walk(self.directory, self.walker_append_target, False)
        
        # Traitement
        self.make_directories_config()
        
        # Affichage des alertes et message de fin
        if len(self.warnings)>0:
            for warn in self.warnings:
                print warn
            print "-"*60
        print "%s jaquette(s) trouvée(s) et mise(s) en place. Fin des opérations." % len(self.target_covers)

    def walker_append_target( self, arg, dirname, names ):
        """
        Récupération récursive des jaquettes d'un répertoire, chaque fichier 
        est mis dans la queue finale.
        """
        for f in names:
            filepath = os.path.join(dirname, f)
            filename, extension = os.path.splitext( f.lower() )
            # On recherche les jaquettes ayant un nom et une extension 
            # correspondant aux motifs et on les convertit si besoin
            if not os.path.isdir(filepath) and filename == self.cover_filename and extension[1:] in self.image_extensions:
                self.target_covers.append( self.convert_cover(filepath) )
    
    def convert_cover(self, sourcepath):
        """
        Convertit une jaquette de couverture si elle n'est pas déja au bon 
        format
        """
        directory = os.path.dirname(sourcepath)
        filename = os.path.basename(sourcepath).split(".")[0]
        filename = u"%s.%s" % (filename, self.cover_images_format[self.cover_format_key])
        thumbname = os.path.join(directory, filename)
        #
        imObj = Image.open(sourcepath)
        need_resize = self.cover_size and (imObj.size[0] > self.cover_size[0] or imObj.size[1] > self.cover_size[1])
        if imObj.format != self.cover_format_key or need_resize:
            # Si on a des dimensions spécifiés et que la source est plus grande que
            # ces dimensions, on redimensionne avec un anti-aliasing
            if need_resize:
                imObj = imObj.resize( self.cover_size, Image.ANTIALIAS )
            # Si on a une image en 8bits genre un gif animé, on transforme en
            # RGB pour la conversion en JPEG
            if imObj.mode == "P":
                imObj.convert("RGB")
            # Sauve la vignette créée
            imObj.save(thumbname, self.cover_format_key)
            return thumbname
        
        return sourcepath
    
    def make_directories_config(self):
        """
        Création/modification des fichiers de config des répertoires où une 
        jaquette à été trouvée.
        """
        for cover in self.target_covers:
            dirconfig_file = os.path.join( os.path.split( cover )[0], self.dirConfig_filename )
            # Init du ConfigParser
            configFile = open(dirconfig_file, 'w')
            # Ecriture a partir du template
            configFile.write( self.template % (self.dirConfig_section, self.dirConfig_option, cover) )
            # Fermeture
            configFile.close()

class BatchDirCoversError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

# Test
if __name__ == "__main__":
    
    # Attributs d'appel
    directory = "/home/thenonda/Essais/sound_of_white_noise"
    cover_filename = "cover"
    
    #> Ouverture de la classe
    o = BatchDirCovers( directory=directory, cover_filename=cover_filename, debug_mode=True)
