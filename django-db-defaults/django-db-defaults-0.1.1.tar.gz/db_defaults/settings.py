from django.conf import settings

#db defaults should be added for all models ir-respective of custom defaults
DB_DEFAULTS_ENABLE_ALL_MODELS = getattr(settings, 'DB_DEFAULTS_ENABLE_ALL_MODELS', False)

#db defaults should be added for all fields ir-respective of custom defaults
#This is always True if DB_DEFAULTS_ENABLE_ALL_MODELS=True
DB_DEFAULTS_ENABLE_ALL_FIELDS = getattr(settings, 'DB_DEFAULTS_ENABLE_ALL_FIELDS', False)



