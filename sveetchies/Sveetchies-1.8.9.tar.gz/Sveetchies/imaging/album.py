# -*- coding: utf-8 -*-
"""
Pictures Albums
"""
import os

from Sveetchies.utils import endswith_in_list

from Sveetchies.imaging import __version__, PICTURES_FORMAT_EXT
from Sveetchies.imaging.picture import LAYOUT_HELP, PictureLayout, PictureAdapt

class AlbumImport(object):
    """
    Importe les images d'un répertoire vers un autre répertoire en adaptant les images 
    selon des options de "layout"
    """
    def __init__(self, logger, large_layout, thumb_layout, formats=PICTURES_FORMAT_EXT, thumb_prefix=None, debug=False):
        self.logger = logger
        self.debug = debug
        self.thumb_layout = PictureLayout.from_layout(thumb_layout)
        self.large_layout = PictureLayout.from_layout(large_layout)
        self.thumb_prefix = thumb_prefix
        self.picture_formats_extensions = ["."+item for item in formats]

        if not self.thumb_layout:
            self.logger.error("- Invalid thumb layout")
        if not self.large_layout:
            self.logger.error("- Invalid large layout")

    def fetch(self, source_path, large_destination_path, thumb_destination_path=None, excludes=[]):
        self.logger.info("* Source directory: %s"%source_path)
        self.logger.info("* Thumb layout: %s" % self.thumb_layout)
        self.logger.info("* Large layout: %s" % self.large_layout)
        
        if not thumb_destination_path:
            thumb_destination_path = large_destination_path
        
        for root, dirs, files in os.walk(source_path):
            files.sort()
            for item in files:
                if endswith_in_list(item.lower(), self.picture_formats_extensions) and item.lower() not in excludes:
                    source_filepath = os.path.join(root, item)
                    large_path = self.get_filepath(large_destination_path, item, prefix=None)
                    thumb_path = self.get_filepath(thumb_destination_path, item, prefix=self.thumb_prefix)
                    thumb_picture = self.adapt_picture(self.thumb_layout, source_filepath, thumb_path)
                    large_picture = self.adapt_picture(self.large_layout, source_filepath, large_path)
                    self._finish_item_step(source_filepath, thumb_picture, large_picture)

    def _finish_item_step(self, source_filepath, thumb_picture, large_picture):
        self.logger.info("* Source picture: {0}".format(source_filepath))
        if thumb_picture:
            self.logger.debug("  ~ Thumb: {0} ({1}x{2})".format(thumb_picture[0], *thumb_picture[1]))
        if large_picture:
            self.logger.debug("  ~ Large: {0} ({1}x{2})".format(large_picture[0], *large_picture[1]))

    def get_filepath(self, destination_path, filename, prefix=None):
        if prefix:
            filename = prefix + "_" + filename
        return os.path.join(destination_path, filename)

    def adapt_picture(self, layout, source, dest):
        if layout and layout.type != "None":
            new_picture = PictureAdapt(self.logger, layout, source, dest, debug=self.debug)
            return dest, new_picture.resize()
        return None
    
if __name__ == "__main__":
    from optparse import OptionParser, OptionGroup
    from Sveetchies.logger.terminal import TerminalLoggerInterface
    
    commandline_parser = OptionParser(version="Sveetchies.imaging.album %%prog %s"%__version__)
    
    contentgroup = OptionGroup(commandline_parser, "Content")
    layoutgroup = OptionGroup(commandline_parser, "Layout", LAYOUT_HELP)
    optsgroup = OptionGroup(commandline_parser, "Options")
    
    contentgroup.add_option("--source", dest="source_path", default=None, help=u"Path to the directory containing original pictures. [default: %default]", metavar="PATH")
    contentgroup.add_option("--destination", dest="destination_path", default=None, help=u"Path for the directory to create than will contain resized pictures. [default: %default]", metavar="PATH")
    contentgroup.add_option("--thumbpath", dest="thumb_path", default=None, help=u"Specify a different directory to store thumbs. If 'None', thumbs will be created in the same directory as large pictures. [default: %default]", metavar="KIND(WITHxHEIGHT)")
    layoutgroup.add_option("--thumb", dest="thumb_layout", default=None, help=u"Active thumb making by specifying their layout. Default is None layout so there will be no thumbs created. [default: %default]", metavar="KIND(WITHxHEIGHT)")
    layoutgroup.add_option("--large", dest="large_layout", default=None, help=u"Specify the layout for resizing original pictures. Default is Auto so the image will not be resized. [default: %default].", metavar="KIND(WITHxHEIGHT)")
    optsgroup.add_option("-d", "--debug", dest="debug", default=False, action="store_true", help="Debug mode don't write anything on disk. [default: %default]"),
    optsgroup.add_option('-v', '--verbosity', action='store', type="int", dest='verbosity', default=1, help=u'Verbosity level. [default: %default]')

    commandline_parser.add_option_group(contentgroup)
    commandline_parser.add_option_group(layoutgroup)
    commandline_parser.add_option_group(optsgroup)
    
    (commandline_options, commandline_args) = commandline_parser.parse_args()
    if not commandline_options.source_path or not commandline_options.destination_path or not commandline_options.thumb_layout or not commandline_options.large_layout:
        commandline_parser.error("You must supply a source, a destination and correct layout.")
    
    logger = TerminalLoggerInterface(
        passive=True,
        logger_id='sveetchies-imaging-album-logger',
        error_blocker=True
    )
    logger.configure_output('terminal', verbosity=commandline_options.verbosity)
    logger.connect(passive=False)
    
    a = AlbumImport(logger, commandline_options.large_layout, commandline_options.thumb_layout, formats=PICTURES_FORMAT_EXT, thumb_prefix="thumb", debug=commandline_options.debug)
    a.fetch(commandline_options.source_path, commandline_options.destination_path, thumb_destination_path=commandline_options.thumb_path)
