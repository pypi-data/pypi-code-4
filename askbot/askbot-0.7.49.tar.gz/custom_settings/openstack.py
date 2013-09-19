#ASKBOT_EXTRA_SKINS_DIR = '/Users/evgenyfadeev/windriver-theme'
ASKBOT_EXTRA_SKINS_DIR = '/Users/evgenyfadeev/askbot-themes/openstack'

LIVESETTINGS_OPTIONS = {
    1: {
        'DB': True,
        'SETTINGS': {
            'GENERAL_SKIN_SETTINGS': {
                'SHOW_LOGO': True,
                'SITE_LOGO_URL': 'images/open-stack-cloud-computing-logo-2.png',
                'ASKBOT_DEFAULT_SKIN': 'os',
            },
        }
    }
}

ASKBOT_MULTILINGUAL = True
ASKBOT_TRANSLATE_URL = False

LANGUAGES = (
    ('zh-cn', 'Chinese'),
    ('en', 'English')
)
