### -*- coding: utf-8 -*- ####################################################

import os
import fnmatch
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files import File
from django_softlayer import SoftLayerStorage
from django.http import Http404

class Command(BaseCommand):
    '''Walks the directory specified in MEDIA_FOLDER and uploads mp3 files to storage'''
    args = ''
    help = 'Walks the directory and uploads mp3 files to cloud storage container'
    
    option_list = BaseCommand.option_list + (
        make_option('--mediaroot',
            default=settings.MEDIA_ROOT,
            help='A source directory to copy files from, e.g. "/home/djangoprojects/myproject/media".'),
        make_option('--mask',
            default='*.mp3',
            help='A file mask, e.g. "*.mp3".'),
        make_option('--noreplace',
            default='',
            action='store_true',
            dest='noreplace',
            help='Skip and do not replace existing files in the storage'),
    )
    
    def handle(self, mediaroot, mask, noreplace, *args, **options):
        
        verbosity = int(options.get('verbosity', 1))

        storage = SoftLayerStorage()
        total = 0
        for root, dirnames, filenames in os.walk(mediaroot):
            for filename in fnmatch.filter(filenames, mask):
                file_name = os.path.abspath(os.path.join(root, filename))
                relative_name = os.path.relpath(file_name, mediaroot)
                skipped = False
                if not noreplace:
                    with open(file_name, 'rb') as _file:
                        storage.save(relative_name, File(_file))
                else:
                    try:
                        stored_obj = storage.container.get_object(relative_name)
                        if stored_obj.props.get('size') is 0:
                            raise Exception(404, 'Null size')
                        skipped = True
                    # Uncatchable exception format
                    except Exception, e:
                        if e[0] == 404:
                            with open(file_name, 'rb') as _file:
                                storage.save(relative_name, File(_file))
                        else:
                            skipped = True
                            print e
    
                if verbosity > 1:
                    total += 1
                    print '{0}: {1}, skipped: {2}'.format(total, file_name, skipped)
