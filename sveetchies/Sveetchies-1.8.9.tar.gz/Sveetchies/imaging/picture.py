# -*- coding: utf-8 -*-
"""
Pictures

TODO: * Availility to convert to Gif or PNG
      * Option to preserve original format
"""
import os, re, Image
from Sveetchies.imaging import __version__

LAYOUT_HELP = u"""Layout specify how to resize the picture. There is four layout kind : Auto, None, Square, Fixed. 'Fixed' resize to a fixed size, no matter what is the picture ratio. 'Square' resize your picture to fit the square size with keeping his original image ratio, note that it will not resize picture if it is not bigger than the square size. 'Auto' keep the original size and 'None' don't do anything, so there are not useful. Syntax is KIND(WxH) where KIND is the layout kind name, W the witdh and H the height both joined by a 'x', like "Square(128x96)". [default: %default]"""

class PictureLayout(object):
    """
    Layout à respecter pour le redimensionnement
    """
    filter_names = ('Auto', 'Fixed', 'None', 'Square')
    empty_filters = ('Auto', 'None')
    
    def __init__(self, typec, width=0, height=0):
        self.type, self.width, self.height = typec, width, height
        
    def is_resizable(self):
        return not(self.type == 'None')
        
    def __repr__(self):
        size = ""
        if self.type not in PictureLayout.empty_filters:
            size = "{width}x{height}".format(width=self.width, height=self.height)
        return "{type}Layout({size})".format(type=self.type, size=size)
    
    @staticmethod
    def from_layout(layout):
        kwargs = PictureLayout.parse_layout(layout)
        if kwargs and 'key' in kwargs:
            if kwargs['key'] in PictureLayout.filter_names:
                if kwargs['key'] in PictureLayout.empty_filters:
                    return PictureLayout(kwargs['key'], width=0, height=0)
                elif 'width' in kwargs and 'height' in kwargs:
                    return PictureLayout(kwargs['key'], width=int(kwargs['width']), height=int(kwargs['height']))
            #else:
                #self.logger.error("Invalid filter name: '{0}'.".format(kwargs['key']))
        #else:
            #self.logger.error("Invalid syntax.")
        return None
    
    @staticmethod
    def parse_layout(layout):
        """
        Parse un format de layout
        
        Méthode à utiliser en appel statique uniquement.
        
        Format d'un layout :
        
            KEY(WIDTHxHEIGHT)
        
        Keys : 
        
        * 'Auto': keep the picture at his original size, don't do anything
        * 'None': no picture for this layout type
        * 'Square': resize picture to fit square zone size, keep the original picture ratio
        * 'Fixed': resize to a fixed size, don't preserve the original picture ratio
        """
        m = re.match("^(?P<key>\w+)\(((?P<width>\d+)x(?P<height>\d+))*\)", layout)
        if m:
            kwargs = m.groupdict()
            return kwargs
        return None

    def get_size_from(self, source_size):
        """
        Retourne une dimension calculée selon le type de layout à partir de la dimension 
        d'origine de l'image
        """
        methodname = "_size_adapt_filter_{0}".format(self.type.lower())
        return getattr(self, methodname)(source_size)

    def _size_adapt_filter_none(self, source_size):
        """
        Dimension nulle
        """
        return None

    def _size_adapt_filter_auto(self, source_size):
        """
        Dimension identique à l'original
        """
        return source_size

    def _size_adapt_filter_fixed(self, source_size):
        """
        Dimension selon une taille fixe
        """
        return self.width, self.height

    def _size_adapt_filter_square(self, source_size):
        """
        Calcul une dimension proportionelle au ratio qui rentre dans les dimensions 
        d'un carré
        
        @source_size: un tuple (width[int], height[int])
        """
        labels = ("width","height")
        source_width, source_height = source_size
        max_part = labels[source_size.index(max(source_size))]
        # Ratio original
        ratio = float(source_width)/float(source_height)
        # Calcul de dimensions proportiennelles
        new_width = source_width
        new_height = source_height
        # Image carrée
        if source_width == source_height:
            ref = min(self.width, self.height)
            new_width = new_height = ref
        # Image rectangulaire
        else:
            if max_part == "width" and source_width > self.width:
                new_width = self.width
                new_height = int(float(new_width)/ratio)
            if max_part == "height" and source_height > self.height:
                new_height = self.height
                new_width = int(float(new_height)*ratio)
        
        return new_width, new_height

class PictureAdapt(object):
    """
    TODO: * Permettre d'utiliser un pointeur de fichier(ou PIL?) comme source au lieu d'un chemin;
          * Une méthode pour vérifier que le redimensionnement est bien nécessaire;
          * Ne pas rouvrir un nouveau pointeur de PIL à chaque fois;
    """
    def __init__(self, logger, layout, source_path, destination_path, debug=False, file_chmod=0755, dirs_chmod=0777):
        self.logger = logger
        # layout can be a layout string to parse or directly a "PictureLayout" object
        if isinstance(layout, PictureLayout):
            self.layout = layout
        else:
            self.layout = PictureLayout.from_layout(layout)
            if not self.layout:
                self.logger.error("- Invalid layout")
        self.source_path = source_path
        self.destination_path = destination_path
        self.file_chmod = file_chmod
        self.dirs_chmod = dirs_chmod
        self.debug = debug

    def resize(self, quality=100, target_format='JPEG'):
        source_image = Image.open(self.source_path)
        new_size = self.layout.get_size_from(source_image.size)
        
        
        if self.layout.is_resizable():
            try:
                target_image = source_image.resize(new_size, Image.ANTIALIAS)
            except IOError, e:
                self.logger.error("    - Error: %s"%e)
            else:
                self.logger.debug("    - {0} scaled to {1}".format('x'.join([str(a) for a in source_image.size]), 'x'.join([str(i) for i in new_size])), lv=3)
                # Conversion en RGB forcée
                if target_image.mode not in ('L', 'RGB', 'RGBA'):
                    target_image = target_image.convert('RGB')
                # Correction d'erreur de typage du format
                if target_format.upper()=='JPG':
                    target_format = 'JPEG'
                if not self.debug:
                    # Créé les répertoires nécessaires au chemin donné si besoin
                    exist_or_create_path(os.path.dirname(self.destination_path), permissions=self.dirs_chmod)
                    # Sauve le fichier de l'image adapté
                    target_image.save(self.destination_path, target_format, quality=quality)
                    if self.file_chmod:
                        os.chmod(self.destination_path, self.file_chmod)
                return new_size
        else:
            self.logger.error("- This layout kind is not resizable : %s" % str(self.layout))
        
        return None

def exist_or_create_path(path, permissions=0777):
    """
    Vérifie qu'un chemin de répertoire existe, si oui ne fait rien, si non le créé 
    automatiquement
    """
    if not os.path.exists( path ):
        os.makedirs(path, permissions)
    elif not os.path.isdir( path ):
        # Le chemin existe et n'est pas un répertoire
        raise IOError("'%s' exists and is not a directory." % path)
    
if __name__ == "__main__":
    from optparse import OptionParser, OptionGroup
    from Sveetchies.logger.terminal import TerminalLoggerInterface
    
    commandline_parser = OptionParser(version="Sveetchies.imaging.picture %%prog %s"%__version__)
    
    commandline_parser.add_option("--source", dest="source_path", default=None, help=u"Path to the original picture. [default: %default]", metavar="PATH")
    commandline_parser.add_option("--destination", dest="destination_path", default=None, help=u"Path for the new picture. [default: %default]", metavar="PATH")
    commandline_parser.add_option("--layout", dest="layout", default=None, help=LAYOUT_HELP, metavar="KIND(WITHxHEIGHT)")
    commandline_parser.add_option("-d", "--debug", dest="debug", default=False, action="store_true", help="Debug mode don't write anything on disk. [default: %default]"),
    commandline_parser.add_option('-v', '--verbosity', action='store', type="int", dest='verbosity', default=1, help=u'Verbosity level. [default: %default]')

    (commandline_options, commandline_args) = commandline_parser.parse_args()
    if not commandline_options.source_path or not commandline_options.destination_path or not commandline_options.layout:
        commandline_parser.error("You must supply a source, a destination and a layout.")
    
    logger = TerminalLoggerInterface(
        passive=True,
        logger_id='sveetchies-imaging-picture-logger',
        error_blocker=True
    )
    logger.configure_output('terminal', verbosity=commandline_options.verbosity)
    logger.connect(passive=False)
    
    p = PictureAdapt(logger, commandline_options.layout, commandline_options.source_path, commandline_options.destination_path, debug=commandline_options.debug)
    
    logger.info("Resizing '{0}' {1}".format(p.source_path, p.layout))
    p.resize()
