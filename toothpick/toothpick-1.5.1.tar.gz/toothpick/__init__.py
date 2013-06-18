import inflection
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Suppress output by default - add more handlers to enable logging
logger.addHandler(logging.NullHandler())


DEFAULT = object()


_model_registry = {}
def register_model(name, cls):
    if name not in _model_registry:
        _model_registry[name] = cls

    return _model_registry[name]

def find_model(name):
    return _model_registry[name]

def models():
    return _model_registry.values()

from toothpick.base import Base
from toothpick.base import EmbeddedBase

from toothpick.resources import EmbeddedResource
from toothpick.resources import JSONResource
from toothpick.resources import MongoResource
from toothpick.resources import TSVResource
from toothpick.resources import JSONFileResource

from toothpick.associations import has_a
from toothpick.associations import has_many
from toothpick.associations import belongs_to
from toothpick.associations import belongs_to_many
from toothpick.associations import embeds_a
from toothpick.associations import embeds_many

from toothpick.validations import validator

from toothpick.errors import Errors

embeds_an = embeds_a
has_an = has_a

def embedded_owner(self):
    return self._embedded_owner
embedded_owner = property(embedded_owner)

