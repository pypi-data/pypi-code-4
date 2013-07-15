#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, errno
import re
import sys
import time
import datetime
import gzip
import glob

from hachoir_core.error import HachoirError
from hachoir_core.cmd_line import unicodeFilename
from hachoir_parser import createParser
from hachoir_core.tools import makePrintable
from hachoir_metadata import extractMetadata
from hachoir_core.i18n import getTerminalCharset

from shutil import copyfile
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings as conf
import rgallery.models as mymodels
from datetime import datetime
from pprint import pprint

from dropbox import client, rest, session


def get_exif(fn):
    """
    data = get_exif('img/2013-04-13 12.17.09.jpg')
    print data
    """

    filename = fn
    filename, realname = unicodeFilename(filename), filename
    parser = createParser(filename, realname)
    if not parser:
        print "[EEE] No puedo parsear %s" % filename
        exit(1)
    try:
        metadata = extractMetadata(parser)
    except HachoirError, err:
        print "[EEE] Metadata extraction error: %s" % unicode(err)
        metadata = None
    if not metadata:
        print "[EEE] Unable to extract metadata"
        exit(1)

    text = metadata.exportPlaintext()
    charset = getTerminalCharset()
    for line in text:
        mes = makePrintable(line, charset)
        if 'Creation date' in mes:
            return mes.split(": ")[1]

    #ret = {}
    #i = Image.open(fn)
    #info = i._getexif()
    #for tag, value in info.items():
    #    decoded = TAGS.get(tag, tag)
    #    ret[decoded] = value
    #return ret


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

# Class MUST be named 'Command'
class Command(BaseCommand):

    # Displayed from 'manage.py help mycommand'
    help = """
    Tool that tries to download and parse photos from a Dropbox shared folder,
    saving it on the database and converting the photos to fit the web:

    ./manage.py dropbox_videosync

    1.- First time it connects with Dropbox and stores the token information in
        a token_file
    2.- Next times it read the token from file to connect Dropbox
    3.- Go to the shared folder and check if the image is already on database
    4.- If not, this script download the image, converting it to fit the web and
        save a record in the database.

    To run this script from a crontab task we should do something like this:

    */30 * * * * cd /path/to/rgallery-project/ ; source env/bin/activate ; cd src ; python manage.py dropbox_videosync > /dev/null

    """

    def handle(self, *app_labels, **options):
        """
        The command itself
        """
        # Get your app key and secret from the Dropbox developer website
        APP_KEY = conf.DROPBOX_APP_KEY
        APP_SECRET = conf.DROPBOX_APP_SECRET

        # ACCESS_TYPE should be 'dropbox' or 'app_folder' as configured for your app
        ACCESS_TYPE = 'dropbox'

        # Creating dirs
        dropboxdir = os.path.join(conf.PROJECT_DIR, 'media', 'uploads', 'dropbox')
        destdir = os.path.join(conf.PROJECT_DIR, 'media', 'uploads', 'videos')
        photosvideos = os.path.join(conf.PROJECT_DIR, 'media', 'uploads', 'photos_videos')
        if os.path.exists(dropboxdir) == False:
            mkdir_p(dropboxdir)
        if os.path.exists(destdir) == False:
            mkdir_p(destdir)
        if os.path.exists(photosvideos) == False:
            mkdir_p(photosvideos)

        # First time
        TOKENS = os.path.join(conf.PROJECT_DIR, 'media', 'uploads', 'dropbox', 'dropbox_token.txt')
        if not os.path.exists(TOKENS):
            sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
            request_token = sess.obtain_request_token()
            url = sess.build_authorize_url(request_token)

            # Make the user sign in and authorize this token
            print "url:", url
            print "Please visit this website and press the 'Allow' button, then hit 'Enter' here."
            raw_input()

            # This will fail if the user didn't visit the above URL
            access_token = sess.obtain_access_token(request_token)

            token_file = open(TOKENS,'w')
            token_file.write("%s|%s" % (access_token.key,access_token.secret) )
            token_file.close()
        else:
            token_file = open(TOKENS)
            token_key,token_secret = token_file.read().split('|')
            token_file.close()
            sess = session.DropboxSession(APP_KEY,APP_SECRET, ACCESS_TYPE )
            sess.set_token(token_key,token_secret)

        c = client.DropboxClient(sess)

        #print "linked account:", c.account_info()

        repetidas = 0
        descargadas = 0
        total = 0
        size = 1000, 1000

        folder_metadata = c.metadata('/Web/')
        #print "*"*80
        #print "metadata:", folder_metadata
        #print "*"*80
        #print "contents:", folder_metadata['contents']

        print "-"*80
        for cont in folder_metadata['contents']:
            try:
                str(cont['mime_type'])
            except:
                cont['mime_type'] = ''

            if cont['mime_type'] == 'video/mp4' or cont['mime_type'] == 'video/3gpp':
                origen_name = os.path.basename(cont['path'])
                print "origen_name=%s" % origen_name
                try:
                    im = mymodels.Video.objects.get(origen=os.path.basename(cont['path']))
                    repetidas += 1
                    print "[***] Repetido: %s" % os.path.basename(cont['path'])
                except:
                    print "[***] El video %s No esta en bd, descargar y agregar a bbdd y hacer thumb" % os.path.basename(cont['path'])
                    nombre_imagen = str(cont['path']).replace('/', '').replace(' ','_').replace(':','-')

                    # Descargar
                    f, metadata = c.get_file_and_metadata(cont['path'])
                    out = open(dropboxdir + '/' + nombre_imagen, 'wb')
                    out.write(f.read())
                    out.close()
                    print "      [i] Descargado"

                    # Meter
                    data_image = get_exif(dropboxdir + '/' + nombre_imagen)
                    print "      [i] Nombre imagen: %s" % nombre_imagen
                    print "      [i] Exif data: %s" % data_image

                    # Convertir con FFMPEG      (en principio no hace falta convertir...)
                    # Hacer thumb               (...pero hace falta hacer thumb)

                    # ffmpeg -i [sourcefile.avi] -acodec mp3 -ar 22050 -ab 32 -f flv -s 320×240 [destfile.flv]
                    # flvtool2 -U [flvfile]
                    # ffmpeg -y -i [videofile] -vframes 1 -ss 00:00:02 -an -vcodec png -f rawvideo -s 320×240 [thumbnailimage.png]

                    #flvfile = conf.MEDIA_ROOT + 'video/flv/' + filename_wo_ext + '.flv'
                    #flvfile_url = conf.MEDIA_URL + 'video/flv/' + filename_wo_ext + '.flv'

                    video_filepath = conf.MEDIA_ROOT + '/uploads/dropbox/' + nombre_imagen
                    video_filepath_final = conf.MEDIA_ROOT + '/uploads/videos/' + nombre_imagen
                    video_filepath_final_url = conf.MEDIA_URL + 'uploads/videos/' + nombre_imagen

                    video_thumbfile = conf.MEDIA_ROOT + '/uploads/photos_videos/' + nombre_imagen + '.png'
                    video_thumbfile_url = 'uploads/photos_videos/' + nombre_imagen + '.png'

                    print "      [i] thumbfile: %s" % video_thumbfile
                    print "      [i] thumburl: %s" % video_thumbfile_url

                    """
                    #convertvideo = "%s -i %s -acodec %s -ar 22050 -ab 32 -f flv -s %s %s" % (conf.ZERO14_FFMPEG, video_filepath,
                    #                                                 conf.ZERO14_FFMPEG_ACODEC, conf.ZERO14_FFMPEG_VIDEO_SIZE,
                    #                                                 flvfile)
                    """
                    ZERO14_FFMPEG='/opt/local/bin/ffmpeg'
                    ZERO14_FFMPEG_VCODEC_THUMB='png'
                    ZERO14_FFMPEG_THUMB_SIZE='320x240'
                    grabimage = "%s -y -i %s -vframes 1 -ss 00:00:02 -an -vcodec %s -f rawvideo -s %s %s " % (ZERO14_FFMPEG, video_filepath,
                                                                      ZERO14_FFMPEG_VCODEC_THUMB,
                                                                      ZERO14_FFMPEG_THUMB_SIZE,
                                                                      video_thumbfile)
                    #os.system(convertvideo)
                    os.system(grabimage)

                    # Copiar video a ubicación correspondiente
                    copyfile(video_filepath, video_filepath_final)

                    # Agregar a base de datos
                    capture_data = datetime.strptime(str(data_image), "%Y-%m-%d %H:%M:%S")
                    vid = mymodels.Video(title=capture_data, image=video_thumbfile_url, video=video_filepath_final_url, origen=os.path.basename(cont['path']), insert_date=datetime.now(), capture_date=capture_data, status=True)
                    vid.save()
                    print "      Agregado a bbdd"

                total += 1
            #print "-"*80

        #print "*"*80

        print "[*** Resumen ***]"
        print "[***] Repetidos en db: %s" % repetidas
        print "[***] Repetidos en disco: %s" % descargadas
        print "[***] Total: %s" % total
