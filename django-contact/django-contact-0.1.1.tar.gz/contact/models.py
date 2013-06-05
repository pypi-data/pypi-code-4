from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes import generic
from model_utils.managers import InheritanceManager
from django.db import models

# TODO: Look into adapting this to use GIS data when possible
# TODO: Consider whether "location" is the best name for these properties

class LocationType(models.Model):
    """ Represents a type of location that specific contact information
        might be related to. For instance, someone might have both an
        "office" and a "home" phone number. This represents two location
        types, "office" and "home".

    """

    name = models.CharField(max_length=16)

    def __unicode__(self):
        return self.name

class WebSite(models.Model):
    """ A website that is affiliate with this contact """

    name = models.CharField(max_length=64, null=True, blank=True)
    url = models.URLField(max_length=128)
    location = models.ForeignKey(LocationType, related_name='websites', null=True, blank=True)

    def __unicode__(self):
        if not self.name is None:
            return self.name

        return self.url

class Phone(models.Model):
    """ Represents a phone. This phone has a number and a location. """

    number = models.CharField(max_length=17) # TODO: Use localflavor for phone numbers?
    location = models.ForeignKey(LocationType, related_name='phones', null=True, blank=True)

    def __unicode__(self):
        return self.number

class Address(models.Model):
    """ Represents a location on Earth. My apologies in the case that you
        live on another planet.

    """

    class Meta(object):
        verbose_name_plural = 'addresses'

    location = models.ForeignKey(LocationType, null=True, blank=True)

    def __unicode__(self):
        return 'Not yet implemented.'

class Email(models.Model):
    """ Represents an email's address and the location data relative to it. """

    address = models.EmailField()
    location = models.ForeignKey(LocationType, related_name='emails', null=True, blank=True)

    def __unicode__(self):
        return '%s (%s)' % (self.address, self.location)

class Date(models.Model):
    """ In case someone wants to remember an important date, we provide a date model. """

    name = models.CharField(max_length=64)
    date = models.DateTimeField()

    def __unicode__(self):
        return self.name

class CustomData(models.Model):
    """ This is a simple type of field data that can be linked to an identity
        so that "unsupported" types of data are able to be linked to your
        contacts if ever required.

    """

    class Meta(object):
        verbose_name_plural = 'custom data'

    key = models.CharField(max_length=32)
    value = models.CharField(max_length=192)
    location = models.ForeignKey(LocationType, related_name='custom_data', null=True, blank=True)

    def __unicode__(self):
        return '%s %s' % (self.key, self.location)

class IdentityData(models.Model):
    """ Arbitrary data that can be linked to a contact. """

    class Meta(object):
        verbose_name_plural = 'identity data'

    # This is used to wrap our ManyToManyField to a generic relation
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    def __unicode__(self):
        return self.content_object.__unicode__()

class Identity(models.Model):
    field_data = models.ManyToManyField(IdentityData, related_name='identity', blank=True)

    objects = InheritanceManager()

    def get_field_data(self, model=None):
        field_list = []

        for item in self.field_data.all():
            if model is None or (item.content_type.app_label == model._meta.app_label and item.content_type.model == model._meta.object_name.lower()):
                field_list.append(item.content_object)

        return field_list

class Person(Identity):
    """ An identity that is a person, or possibly is masquerading as one! """

    class Meta(object):
        verbose_name_plural = 'people'

    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=128)
    nickname = models.CharField(max_length=64)

    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def __unicode__(self):
        return self.full_name()

class Company(Identity):
    """ An organization or other entity that has an identity but is not a person. """

    class Meta(object):
        verbose_name_plural = 'companies'

    name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name

class Group(models.Model):
    """ Allows identities to be added to different groups in the system. """

    name = models.CharField(max_length=32)
    members = models.ManyToManyField(Identity, blank=True)

    def __unicode__(self):
        return self.name

