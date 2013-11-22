from django.db.models import get_models, ManyToManyField
from django.db.models.signals import post_init, post_save
from threading import Lock

REGISTRY_LOCK = Lock()

REGISTRY = set()
NEW_MODEL_HASH = None


def register_all():
    models = get_models()
    for model in models:
        register(model)


def register(cls):
    with REGISTRY_LOCK:
        if cls in REGISTRY:
            return
        REGISTRY.add(cls)

    def _init_hash(sender, instance):
        if sender in REGISTRY:
            instance.__dirty_hash = cls._get_hash(instance)
        else:
            instance.__dirty_hash = NEW_MODEL_HASH

    def _convert_value(field, instance):
        # Ignoring many to many since django calls save
        # Trying to track this relationship causes performance issues
        if isinstance(field, ManyToManyField):
            return None
        else:
            return field.value_to_string(instance)

    def _get_hash(instance):
        if not instance.pk:
            return NEW_MODEL_HASH
        model_key_values = tuple(
            (
                (field.name, _convert_value(field, instance)) for field in
                (instance._meta.fields + instance._meta.many_to_many)
            )
        )
        return hash(model_key_values)

    def is_dirty(self):
        if self.__dirty_hash == NEW_MODEL_HASH:
            # initial state of a model is dirty
            return True
        return cls._get_hash(self) != self.__dirty_hash

    cls._init_hash = _init_hash
    cls._get_hash = _get_hash
    cls.is_dirty = is_dirty

    def _post_init(sender, instance, **kwargs):
        _init_hash(sender, instance)

    def _post_save(sender, instance, **kwargs):
        _init_hash(sender, instance)

    post_save.connect(_post_save, sender=cls, weak=False)
    post_init.connect(_post_init, sender=cls, weak=False)
