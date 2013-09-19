import site
ASKBOT_EXTRA_SKINS_DIR = '/Users/evgenyfadeev/askbot-themes/visionsmarts-theme/'
site.addsitedir(ASKBOT_EXTRA_SKINS_DIR)
from settings import *

INSTALLED_APPS += ('appforum',)
DATABASES['appdata'] = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    'NAME': 'appdata',                      # Or path to database file if using sqlite3.
    'USER': 'askbot',                      # Not used with sqlite3.
    'PASSWORD': '',                  # Not used with sqlite3.
    'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
    'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
}
DATABASE_ROUTERS = (
    'appforum.routers.AppForumRouter',
)
LIVESETTINGS_OPTIONS = {
    1: {
        'DB': True,
        'SETTINGS': {
            'GENERAL_SKIN_SETTINGS': {
                'ASKBOT_DEFAULT_SKIN': 'visionsmarts',#'os',#'ros', #'os',#'default',#'default',#themes',
            },
            'GROUP_SETTINGS': {
                'GROUPS_ENABLED': False,
            },
            'FORUM_DATA_RULES': {
                'ACCEPTING_ANSWERS_ENABLED': False,
                'EDITOR_TYPE': 'tinymce',
                'ASK_BUTTON_ENABLED': False,
                'LIMIT_ONE_ANSWER_PER_USER': False,
                'MIN_QUESTION_BODY_LENGTH': 0,
                'QUESTION_BODY_EDITOR_MODE': 'open',
                'WIKI_ON': False,
            },
            'QUESTION_LISTS': {
                'ALL_SCOPE_ENABLED': False,
                'UNANSWERED_SCOPE_ENABLED': False,
                'FOLLOWED_SCOPE_ENABLED': True
            },
            'KARMA_AND_BADGE_VISIBILITY': {
                'KARMA_MODE': 'private',
                'BADGES_MODE': 'hidden'
            },
            'LICENSE_SETTINGS': {
                'USE_LICENSE': False
            },
            'SOCIAL_SHARING': {
                'RSS_ENABLED': False,
                'ENABLE_SHARING_IDENTICA': False,
                'ENABLE_SHARING_GOOGLE': False,
                'ENABLE_SHARING_TWITTER': False,
                'ENABLE_SHARING_FACEBOOK': False,
                'ENABLE_SHARING_LINKEDIN': False
            }
        }
    }
}
ASKBOT_NEW_ANSWER_FORM = 'appforum.forms.NewAnswerForm'
ASKBOT_EDIT_ANSWER_FORM = 'appforum.forms.EditAnswerForm'
ASKBOT_EDIT_ANSWER_PAGE_EXTRA_CONTEXT = 'appforum.context.get_edit_answer_page_context'
ASKBOT_QUESTION_PAGE_EXTRA_CONTEXT = 'appforum.context.get_question_page_context'
ASKBOT_QUESTIONS_PAGE_EXTRA_CONTEXT = 'appforum.context.get_questions_page_context'
ASKBOT_QUESTION_SUMMARY_EXTRA_CONTEXT = 'appforum.context.get_question_summary_context'
ASKBOT_TAGS_PAGE_EXTRA_CONTEXT = 'appforum.context.get_tags_page_context'
ASKBOT_USER_PROFILE_PAGE_EXTRA_CONTEXT = 'appforum.context.get_user_profile_page_context'

ENABLED_LOGIN_PROVIDERS = (
    'local',
    'google',
    'yahoo',
    'twitter',
    'facebook'
)

DISABLED_LOGIN_PROVIDERS = (
    'AOL',
    'Blogger',
    'ClaimID',
    'Flickr',
    'LinkedIn',
    'LiveJournal',
    #'myOpenID',
    'OpenID',
    'Technorati',
    'Wordpress',
    'Vidoop',
    'Verisign',
    'identi.ca',
    'LaunchPad'
)

TINYMCE_DEFAULT_CONFIG['content_css'] = STATIC_URL + 'visionsmarts/media/style/tinymce_content.css'

LOGIN_PROVIDERS_ENABLED = dict()
for provider in ENABLED_LOGIN_PROVIDERS:
    name = 'SIGNIN_%s_ENABLED' % provider.upper()
    LOGIN_PROVIDERS_ENABLED[name] = True

for provider in DISABLED_LOGIN_PROVIDERS:
    name = 'SIGNIN_%s_ENABLED' % provider.upper()
    LOGIN_PROVIDERS_ENABLED[name] = False

LIVESETTINGS_OPTIONS[1]['SETTINGS']['LOGIN_PROVIDERS'] = LOGIN_PROVIDERS_ENABLED

ASKBOT_USE_LOCAL_FONTS = True
