import datetime

from django.utils import timezone
import factory

from . import models


class StreamFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = models.Stream


class StreamItemFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = models.StreamItem

    pub_date = factory.LazyAttribute(lambda a: timezone.now())
