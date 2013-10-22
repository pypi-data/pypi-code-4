# -*- coding: utf-8 -*-
"""
Commande en ligne d'importation d'albums
"""
import datetime, os, re
from optparse import OptionValueError, make_option
import Image

from django.conf import settings
from django.core.management.base import CommandError, BaseCommand
from django.template.defaultfilters import slugify

from django.contrib.auth.models import User

from Sveetchies.logger.terminal import TerminalLoggerInterface

from Sveetchies.imaging import PICTURES_FORMAT_EXT
from Sveetchies.imaging.picture import LAYOUT_HELP, PictureLayout, PictureAdapt
from Sveetchies.imaging.album import AlbumImport
from Sveetchies.django.gallery import (
    GALLERY_ALBUM_THUMB_LAYOUT,
    GALLERY_PICTURE_THUMB_LAYOUT,
    GALLERY_PICTURE_LARGE_LAYOUT,
    GALLERY_ALBUM_THUMB_UPLOADPATH,
    GALLERY_PICTURE_LARGE_UPLOADPATH,
    GALLERY_PICTURE_THUMB_UPLOADPATH
)
from Sveetchies.django.gallery.models import Album, Picture
from Sveetchies.django.filefield import content_file_name, get_unique_filename
#from Sveetchies.cli import unquote_string_argument

LOGGING_FILENAME = "album_import.log"

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("--title", dest="album_title", default=None, help="Title for album. [default: %default]", metavar="TITLE"),
        make_option("--invisible", dest="invisible_mode", default=False, action="store_true", help=u"Album will be invisible. By default this is False, the album will be visible. [default: %default]"),
        make_option("--album", dest="album_layout", default=GALLERY_ALBUM_THUMB_LAYOUT, help="Album layout. [default: %default]", metavar="LAYOUT"),
        make_option("--thumb", dest="thumb_layout", default=GALLERY_PICTURE_THUMB_LAYOUT, help="Thumb layout. [default: %default]", metavar="LAYOUT"),
        make_option("--large", dest="large_layout", default=GALLERY_PICTURE_LARGE_LAYOUT, help="Large picture layout. [default: %default]", metavar="LAYOUT"),
        make_option("--author", dest="album_author", default='root', help="Album's pictures owner user object, if not supplied default to root. [default: %default]", metavar="USERNAME"),
        make_option("-d", "--debug", dest="debug_mode", default=False, action="store_true", help="Debug mode don't write anything in database. [default: %default]"),
    )
    help = "Command to import album"

    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError("Command accept only one argument (album path)")
        if len(args) > 1:
            raise CommandError("Command need one argument (album path)")
        
        album_path = os.path.abspath(args[0])
        album_title = options.get('album_title')
        album_visible = not(options.get('invisible_mode'))
        album_author = options.get('album_author')
        album_layout = options.get('album_layout')
        thumb_layout = options.get('thumb_layout')
        large_layout = options.get('large_layout')
        debug_mode = options.get('debug_mode')
        excludes = []
        self.verbosity = int(options.get('verbosity'))
        
        # Parse préventif des layout pour les valider
        album_layout = PictureLayout.from_layout(album_layout)
        tmp_thumb_layout = PictureLayout.from_layout(thumb_layout)
        tmp_large_layout = PictureLayout.from_layout(large_layout)
        if not album_layout or not tmp_thumb_layout or not tmp_large_layout:
            raise CommandError("'--album', '--thumb' and '--large' options can't be empty, a layout is required.")
        if tmp_thumb_layout.type == 'Auto':
            raise CommandError("Thumb picture don't exist, his layout can't be Auto().")
        if album_layout.type == 'None' or tmp_thumb_layout.type == 'None' or tmp_large_layout.type == 'None':
            raise CommandError("Album thumb, Piture thumb and large picture are required, their layout can't be None().")
        
        # Auteur de l'album
        if not album_author:
            raise CommandError("'--author' option can't be empty, a username is required.")
        try:
            author_object = User.objects.get(username=album_author)
        except User.DoesNotExist:
            raise CommandError("Author USERNAME '%s' does not exist."%album_author)
        
        # Recherche vignette d'album
        album_picturepath = None
        for item in list(PICTURES_FORMAT_EXT)+[ext.upper() for ext in PICTURES_FORMAT_EXT]:
            if os.path.exists(os.path.join(album_path, 'album.'+item)):
                album_picturepath = os.path.join(album_path, 'album.'+item)
                break
        if not album_picturepath:
            raise CommandError("Album require a thumb picture file named 'album' with a format extension ({0}) like 'album.jpg'. Put this file in your album directory to import.".format(', '.join(PICTURES_FORMAT_EXT)))
        
        # Titre par défaut à partir du nom du répertoire source
        if not album_title:
            album_title = os.path.basename(album_path)
        # Détermine le "slug name"
        slug = slugify(album_title)

        # Init du logger
        starttime = datetime.datetime.now()
        self.logger = TerminalLoggerInterface(
            passive=True,
            logger_id='sveetchies-gallery-logger',
            error_blocker=False
        )
        self.logger.configure_output('terminal', verbosity=self.verbosity)
        self.logger.connect(passive=False)
        
        # Vignette de l'album
        albumthumb_destination_path = content_file_name(GALLERY_ALBUM_THUMB_UPLOADPATH, None, os.path.basename(album_picturepath))
        albumthumb_destination_path = os.path.join(settings.MEDIA_ROOT, albumthumb_destination_path)
        excludes.append(os.path.basename(album_picturepath))
        album_picture = PictureAdapt(self.logger, album_layout, album_picturepath, albumthumb_destination_path, debug=debug_mode)
        album_picture.resize()
        # Save album object
        album_object = Album(
            author=author_object,
            slug=slug,
            title=album_title,
            visible=album_visible
        )
        if not debug_mode:
            album_object.thumb = albumthumb_destination_path[len(settings.MEDIA_ROOT):]
            album_object.save()
        # Traitement de l'album à importer
        a = GalleryAlbumImport(self.logger, large_layout, thumb_layout, formats=PICTURES_FORMAT_EXT, thumb_prefix=None, debug=debug_mode)
        a.fetch(album_object, album_path, album_layout, excludes=excludes)
        
        endtime = datetime.datetime.now()
        self.logger.info("~~~ Durée : %s" % str(endtime-starttime))

class GalleryAlbumImport(AlbumImport):
    def fetch(self, album_object, source_path, album_layout, excludes=[]):
        self.album_object = album_object
        large_destination_path = content_file_name(GALLERY_PICTURE_LARGE_UPLOADPATH, None)
        thumb_destination_path = content_file_name(GALLERY_PICTURE_THUMB_UPLOADPATH, None)
        super(GalleryAlbumImport, self).fetch(source_path, large_destination_path, thumb_destination_path, excludes=excludes)
        
    def _finish_item_step(self, source_filepath, thumb_picture, large_picture):
        self.logger.info("* Source picture: {0}".format(source_filepath))
        rel_large = large_picture[0][len(settings.MEDIA_ROOT):]
        rel_thumb = thumb_picture[0][len(settings.MEDIA_ROOT):]
        #print "rel_large:", rel_large
        #print "rel_thumb:", rel_thumb
        if not self.debug:
            p = self.album_object.picture_set.create(
                title=os.path.basename(source_filepath),
                author=self.album_object.author,
                visible=True,
                large=rel_large,
                thumb=rel_thumb,
            )
        if thumb_picture:
            self.logger.debug("  ~ Thumb: {0} ({1}x{2})".format(thumb_picture[0], *thumb_picture[1]))
        if large_picture:
            self.logger.debug("  ~ Large: {0} ({1}x{2})".format(large_picture[0], *large_picture[1]))

    def get_filepath(self, destination_path, filename, prefix=None):
        # TODO: pour l'instant Sveetchies.imaging ne produit que du JPG donc 
        # l'extension est forcée
        filename = get_unique_filename(filename, new_extension="jpg")
        if prefix:
            filename = prefix + "_" + filename
        return os.path.join(settings.MEDIA_ROOT, destination_path, filename)


