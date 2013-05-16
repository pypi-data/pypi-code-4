# -*- coding: utf-8 -*-
from shiva.media import MediaDir

SECRET_KEY = ''  # Set this to something secret.
MEDIA_DIRS = (
    MediaDir('/home/alvaro/Musik', url='http://127.0.0.1:8000/'),
)
LASTFM_API_KEY = ''
SCRAPERS = {
    'lyrics': (
        'azlyrics.AZLyrics',
        'metrolyrics.MetroLyrics',
        'letrascanciones.MP3Lyrics',
    ),
}
METROLYRICS_API_KEY = '1234567890123456789012345678901234567890'
BANDSINTOWN_APP_ID = 'SHIVA_APP_ID'
# Here you can redefine anything you set in your settings.project file, like
# the database URI.
