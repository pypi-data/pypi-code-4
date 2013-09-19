from custom_settings.windriver_intel import *
SITE_ID = 1

ASKBOT_EXTRA_SKINS_DIR = '/Users/evgenyfadeev/askbot-themes/windriver-theme/'
STATICFILES_DIRS += (ASKBOT_EXTRA_SKINS_DIR,)

LIVESETTINGS_OPTIONS = {
    1: {
        'DB': True,
        'SETTINGS': {
            'GENERAL_SKIN_SETTINGS': {
                'ASKBOT_DEFAULT_SKIN': 'windriver',#'os',#'ros', #'os',#'default',#'default',#themes',
            },
            'FORUM_DATA_RULES': {
                'EDITOR_TYPE': 'tinymce',
                'SPACES_ENABLED': True,
            },
        }
    }
}

