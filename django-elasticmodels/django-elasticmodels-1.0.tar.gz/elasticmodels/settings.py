from django.conf import settings
from django.db.models.loading import get_model

# Contains the URL to ElasticSearch
ELASTICSEARCH_HOST = getattr(
        settings, 'ELASTICSEARCH_HOST', 'http://localhost:9200/')

# Contains a list of models >> ['myapp.mymodel',]
ELASTICSEARCH_MODELS = getattr(settings, 'ELASTICSEARCH_MODELS', [])
ELASTICSEARCH_TO_INDEX = []

appmodels = map(lambda x:x.split('.'), ELASTICSEARCH_MODELS)

# Adds all the models to the ELASTICSEARCH_TO_INDEX list
for item in appmodels:
    ELASTICSEARCH_TO_INDEX.append(
        get_model(item[0], item[1])
    )

# Retrieves custom types >> "geo_location": {"type": "geo_point"}
ELASTICSEARCH_CUSTOM_TYPES = getattr(
    settings,
    'ELASTICSEARCH_CUSTOM_TYPES', {})

# Retrieves all non model fields >> {"snippet": {"type": "string"}}
ELASTICSEARCH_NON_MODEL_FIELDS = getattr(
    settings,
    'ELASTICSEARCH_NON_MODEL_FIELDS', []
)

