from django.conf import settings

TWEETS_TEMPLATES = [('cms/plugins/switter/default.html', 'Default'), ]

if getattr(settings, 'CMS_PLUGIN_TEMPLATES'):
    TWEETS_TEMPLATES = settings.CMS_PLUGIN_TEMPLATES.get('SwitterTweetsPlugin', TWEETS_TEMPLATES)
