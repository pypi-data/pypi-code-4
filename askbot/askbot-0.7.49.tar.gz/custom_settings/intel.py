from custom_settings.windriver_intel import *
SITE_ID = 2

ASKBOT_EXTRA_SKINS_DIR = '/Users/evgenyfadeev/askbot-themes/intel-theme/'
STATICFILES_DIRS += (ASKBOT_EXTRA_SKINS_DIR,)

LIVESETTINGS_OPTIONS = {
    2: {
        'DB': True,
        'SETTINGS': {
            'GENERAL_SKIN_SETTINGS': {
                'ASKBOT_DEFAULT_SKIN': 'intel',
            },
            'FORUM_DATA_RULES': {
                'EDITOR_TYPE': 'tinymce',
                'SPACES_ENABLED': True,
            },
        }
    }
}

