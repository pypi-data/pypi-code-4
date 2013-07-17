# -*- coding: utf-8 -*-
from shiva.media import MediaDir, MimeType

SECRET_KEY = ''  # Set this to something secret.
MEDIA_DIRS = (
    MediaDir('/home/alvaro/multimedia/music'),
)
# Add your own mimetypes here.
# MIMETYPES = (
#     MimeType(type='audio', subtype='mp3', extension='mp3',
#              acodec='libmp3lame'),
#     MimeType(type='audio', subtype='ogg', extension='ogg',
#              acodec='libvorbis'),
# )
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
CORS_ENABLED = True
CORS_ALLOWED_ORIGINS = '*'
# SERVER_URI = 'http://127.0.0.1:9002'
