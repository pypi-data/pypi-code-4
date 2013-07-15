#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, errno
import re
import sys
import time
import datetime
import gzip
import glob
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS

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
    ret = {}
    print fn
    i = Image.open(fn)
    info = i._getexif()
    try:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            ret[decoded] = value
    except:
        now = datetime.now()
        ret['DateTimeOriginal'] = now.strftime("%Y:%m:%d %H:%M:%S")

    try:
        str(ret['DateTimeOriginal'])
    except:
        now = datetime.now()
        ret['DateTimeOriginal'] = now.strftime("%Y:%m:%d %H:%M:%S")

    return ret


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

    ./manage.py dropbox_photosync

    1.- First time it connects with Dropbox and stores the token information in
        a token_file
    2.- Next times it read the token from file to connect Dropbox
    3.- Go to the shared folder and check if the image is already on database
    4.- If not, this script download the image, converting it to fit the web and
        save a record in the database.

    To run this script from a crontab task we should do something like this:

    */30 * * * * cd /path/to/rgallery-project/ ; source env/bin/activate ; cd src ; python manage.py dropbox_photosync > /dev/null

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
        destdir = os.path.join(conf.PROJECT_DIR, 'media', 'uploads', 'photos')
        if os.path.exists(dropboxdir) == False:
            mkdir_p(dropboxdir)
        if os.path.exists(destdir) == False:
            mkdir_p(destdir)

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
            print cont

        for cont in folder_metadata['contents']:
            try:
                str(cont['mime_type'])
            except:
                cont['mime_type'] = ''

            if cont['mime_type'] == 'image/jpeg':
                origen_name = os.path.basename(cont['path'])
                #print "origen_name=%s" % origen_name
                try:
                    im = mymodels.Photo.objects.get(origen=os.path.basename(cont['path']))
                    repetidas += 1
                    print "[***] Repetida: %s" % os.path.basename(cont['path'])
                except:
                    print "[***] La imagen %s No esta en bd, descargar y agregar a bbdd y hacer thumb" % os.path.basename(cont['path'])
                    nombre_imagen = str(cont['path']).replace('/', '').replace(' ','_').replace(':','-')

                    # Descargar
                    f, metadata = c.get_file_and_metadata(cont['path'])
                    out = open(dropboxdir + '/' + nombre_imagen, 'wb')
                    out.write(f.read())
                    out.close()
                    print "      Descargada"

                    # Meter
                    data_image = get_exif(dropboxdir + '/' + nombre_imagen)
                    capture_data = datetime.strptime(str(data_image['DateTimeOriginal']), "%Y:%m:%d %H:%M:%S")
                    im = mymodels.Photo(image="uploads/photos/" + nombre_imagen, origen=os.path.basename(cont['path']), insert_date=datetime.now(), capture_date=capture_data, status=True)
                    im.save()
                    print "      Agregada a bbdd"
                    im2 = Image.open(dropboxdir + '/' + nombre_imagen)

                    try:
                        # Rotar si es necesario
                        for orientation in ExifTags.TAGS.keys() :
                            if ExifTags.TAGS[orientation]=='Orientation' : break
                        exif=dict(im2._getexif().items())
                        if exif[orientation] == 3 :
                            im2=im2.rotate(180, expand=True)
                        elif exif[orientation] == 6 :
                            im2=im2.rotate(270, expand=True)
                        elif exif[orientation] == 8 :
                            im2=im2.rotate(90, expand=True)
                    except:
                        pass

                    im2.thumbnail(size, Image.ANTIALIAS)
                    if os.path.exists(destdir + '/' + nombre_imagen) == False:
                        im2.save(destdir + '/' + nombre_imagen)
                        print "      Thumbnail en: %s/%s" % (destdir, nombre_imagen)
                    else:
                        descargadas += 1
                        nombre_imagen_repe = str(cont['path']).replace('/','').replace(' ','_').replace(':','-').replace('.jpg','') + '_1.jpg'
                        im.image = "uploads/photos/" + nombre_imagen_repe
                        im.save()
                        im2.save(destdir + '/' + nombre_imagen_repe)
                        print "      Duplicada en disco, cambiado nombre a: %s" % nombre_imagen_repe
                total += 1
            #print "-"*80

        #print "*"*80

        print "[*** Resumen ***]"
        print "[***] Repetidas en db: %s" % repetidas
        print "[***] Repetidas en disco: %s" % descargadas
        print "[***] Total: %s" % total
