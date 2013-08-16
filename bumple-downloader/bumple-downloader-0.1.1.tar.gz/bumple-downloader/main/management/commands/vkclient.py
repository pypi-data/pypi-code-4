# coding=utf-8
import os
import shutil
from urllib import urlretrieve
from django.core.management import BaseCommand
from main import settings
from main.settings import DOWNLOAD_PATH, ITUNES_PATH
from main.vk_api import VkApi


class Command(BaseCommand):
    def handle(self, *args, **options):
        api = VkApi()
        tracks = api.get_all_tracks(settings.VK_USER_ID)
        for track in tracks:
            file_name = "%s - %s" % (track['artist'], track['title'])
            if not os.path.exists(DOWNLOAD_PATH + file_name):
                print "=> save %s" % (file_name)
                urlretrieve(track['url'], DOWNLOAD_PATH + file_name)
                shutil.copyfile(DOWNLOAD_PATH + file_name,
                                ITUNES_PATH + file_name)