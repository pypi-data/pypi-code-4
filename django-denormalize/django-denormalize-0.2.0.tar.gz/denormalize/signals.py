from django.dispatch import Signal

# Called from backends whenever a collection was changed
# :param sender: Collection class
# :param backend: backend instance
# :param collection: collection instance
# :param key: id of changed document
# TODO: currently not sent yet
#collection_updated = Signal(providing_args=['backend', 'collection', 'key'])
