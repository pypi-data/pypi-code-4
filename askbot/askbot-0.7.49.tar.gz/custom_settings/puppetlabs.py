ASKBOT_EXTRA_SKINS_DIR = '/Users/evgenyfadeev/puppet-askbot/files'

LIVESETTINGS_OPTIONS = {
    1: {
        'DB': True,
        'SETTINGS': {
            'GENERAL_SKIN_SETTINGS': {
                'ASKBOT_DEFAULT_SKIN': 'themes',
                'SHOW_LOGO': True,
                'SITE_FAVICON': 'images/puppet-favicon.ico',
                'CUSTOM_HEADER': '',
            },
            'QA_SITE_SETTINGS': {
                'ENABLE_GREETING_FOR_ANONYMOUS_USER': False
            },
            'FORUM_DATA_RULES': {
                'TAG_SOURCE': 'user-input'
            }
        }
    }
}
