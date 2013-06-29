from os import path

PLAYERDIR = path.dirname(path.abspath(__file__))

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'player.multimedia.middleware.MediaMiddleware',
    'player.block.middleware.RenderBlockMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'player.context_processors.collections',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'dbtemplates.loader.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

TEMPLATE_DIRS = (
    path.join(PLAYERDIR, 'templates'),
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # required by django-playerlayer
    'south',
    'sorl.thumbnail',
    'dbtemplates',
    'pagination',
    'inplaceeditform',
    'inlinetrans',
    'johnny',
    'oembed',
    'cmsutils',
    'compressor',
    'announcements',
    'dbresolver',
    'filebrowser',
    'debug_toolbar',
    'staging',
    'configfield',
    # django-playerlayer
    'player.base',
    'player.block',
    'player.crawler',
    'player.data',
    'player.dbtemplate',
    'player.dburl',
    'player.logicaldelete',
    'player.multimedia',
    'player.player_staging',
    'player.manage',
)

INTERNAL_IPS = ('127.0.0.1', )

LOCALE_PATHS = (
    path.join(PLAYERDIR, 'locale'),
)

SLUG_RE = r'[-_\.\w]+'

LOGIN_URL = '/manage/login/'

LOGOUT_URL = '/manage/logout/'

MEDIA_URL = '/media/'

STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = '/static/admin/'

# dbtemplates settings
DBTEMPLATES_USE_CODEMIRROR = True
DBTEMPLATES_MEDIA_PREFIX = STATIC_URL + 'codemirror/'
DBTEMPLATES_AUTO_POPULATE_CONTENT = False

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    #'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    #'debug_toolbar.panels.cache.CacheDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

CRAWLER_BACKENDS = (
    ('player.crawler.backends.mozenda', 'Mozenda'),
    ('player.crawler.backends.feed', 'Feed'),
)

STAGING_MODELS_TO_SAVE = (
    ('block', 'PlacedBlock'),
    ('data', 'CollectionGroup'),
    ('data', 'Collection'),
    ('data', 'CollectionField'),
    ('crawler', 'CrawlerCollection'),
    ('dbresolver', 'URLPattern'),
)

SERIALIZATION_MODULES = {
    "json": "player.serializers.json",
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'dbtemplates': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
