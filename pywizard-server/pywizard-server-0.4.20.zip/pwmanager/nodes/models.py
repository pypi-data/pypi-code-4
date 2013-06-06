"""
Nodes are separated by groups. Groups are not visible to each other.
Node may have one or several roles.

Node property is a text value.
Node property may be assigned on several levels: role, group, node.
Node properties are collected from all levels and sorted by weight.
If priorities are equal, then the following priorities are take place: node > role > group

"""

from collections import defaultdict
import json
from django.db import models
from django.db.models.signals import post_init, pre_save, post_save, m2m_changed, post_delete
from django.dispatch import receiver
from django.utils.safestring import mark_safe
from pwmanager.settings import PROVISION_PACKAGE_UPLOAD_DIRECTORY


class Node(models.Model):
    name = models.CharField(max_length=150)
    short_name = models.SlugField(max_length=150, db_index=True)
    description = models.TextField(blank=True)
    roles = models.ManyToManyField('Role', related_name='nodes', blank=True)
    group = models.ForeignKey('NodeGroup', related_name='nodes')

    class Meta:
        unique_together = (
            ("name", "group"),
            ("short_name", "group"),
        )
        ordering = ('group', 'name',)

    def __unicode__(self):
        return '%s > %s' % (self.group, self.name)

    def collect_role_names(self):
        return set([role.short_name for role in self.collect_roles()])

    def role_list_display(self):
        return ', '.join([x.name for x in self.roles.all()])

    role_list_display.short_description = 'Roles'

    def group_role_list_display(self):
        return ', '.join([x.name for x in self.group.roles.all()])

    group_role_list_display.short_description = 'Group roles'

    def collect_roles(self):
        return list(self.roles.all()) + list(self.group.roles.all())

    def collect_attribute_values(self):

        collected = {}

        for val in self.attributes.all():
            collected[val.name] = val.value or val.inherited_value

        return dict(collected)

    def _compile_context(self):
        roles = list(self.collect_role_names())
        try:
            uploaded__package = self.group.provisionpackage_set.latest(field_name='date_uploaded').package.path
        except ProvisionPackage.DoesNotExist:
            uploaded__package = None

        context = {
            'name': self.format_full_name(),
            'full_name': self.name,
            'group_name': self.group.name,
            'package': uploaded__package,
            'vagrant-mode': False,
            'log-level': "DEBUG",
            'roles': roles,
        }

        for key, val in self.collect_attribute_values().iteritems():
            if not key in context:
                context[key] = val

        return context

    def config_link(self):
        return mark_safe('<a href="/node-cfg/%s" target="_blank">context</a>' % self.format_full_name())

    def node_link(self):
        return mark_safe('<a href="/node/%s" target="_blank">console</a>' % self.group.short_name)

    def formatted_context(self):
        return mark_safe('<pre>%s</pre>' % json.dumps(self.get_context(), indent=True))

    def get_group_context(self):
        return [node._compile_context() for node in self.group.nodes.all()]

    def get_context(self):
        return {
            'me': self._compile_context(),
            'all': self.get_group_context(),
        }

    def format_full_name(self):
        return '%s::%s' % (self.group.short_name, self.short_name)

    format_full_name.short_description = 'Full name'

    def recalculate_attributes(self):

        # NodeAttributeValue.objects.filter(ref=self, value=None).delete()
        # NodeAttributeValue.objects.filter(ref=self, value='').delete()

        my = [a.name for a in self.attributes.all()]

        other_attrs = []

        for role in self.collect_roles():
            other_attrs += list(role.attributes.all())

        other_attrs += list(self.group.attributes.all())
        other_attrs += list(self.attributes.all())

        for attr in other_attrs:
            if not attr.name in my:
                val = NodeAttributeValue()
                val.name = attr.name
                val.value = None
                val.ref = self
                val.inherited_from = '%s: %s' % (
                    'Group' if isinstance(attr.ref, NodeGroup) else 'Role', unicode(attr.ref)
                )
                val.inherited_value = attr.value
                val.save()
                self.attributes.add(val)
                my.append(attr.name)
                pass


class ProvisionPackage(models.Model):
    date_uploaded = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey('NodeGroup')
    package = models.FileField(upload_to=PROVISION_PACKAGE_UPLOAD_DIRECTORY, )


class NodeGroup(models.Model):
    name = models.CharField(max_length=150)
    short_name = models.SlugField(max_length=150, unique=True)
    roles = models.ManyToManyField('Role', related_name='groups', blank=True)
    description = models.TextField(blank=True)

    def list_roles(self):
        if self.roles.count() == 0:
            return '-'
        return ', '.join([role.name for role in self.roles.all()])

    list_roles.short_description = 'Roles'

    def list_nodes(self):
        if self.nodes.count() == 0:
            return '-'
        return ', '.join([node.name for node in self.nodes.all()])

    list_nodes.short_description = 'Nodes'

    def list_attrs(self):
        if self.attributes.count() == 0:
            return '-'
        return ', '.join([attr.name for attr in self.attributes.all()])

    list_attrs.short_description = 'Attributes'

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.short_name)


class Role(models.Model):
    name = models.CharField(max_length=150, unique=True)
    short_name = models.SlugField(max_length=150, unique=True)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.name


class AttributeValue(models.Model):
    name = models.CharField(max_length=150)
    value = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return '%s: %s' % (self.name, self.value)


class NodeAttributeValue(AttributeValue):
    ref = models.ForeignKey(Node, related_name='attributes')
    inherited_from = models.CharField(max_length=150, blank=True, null=True, default='-')
    inherited_value = models.CharField(max_length=1000, blank=True, null=True)


class RoleAttributeValue(AttributeValue):
    ref = models.ForeignKey(Role, related_name='attributes')


class GroupAttributeValue(AttributeValue):
    ref = models.ForeignKey(NodeGroup, related_name='attributes')


@receiver(post_save, sender=Node)
def update_node_attributes(sender, instance, **kwargs):
    instance.recalculate_attributes()

@receiver(post_delete,  sender=RoleAttributeValue)
@receiver(post_save,  sender=RoleAttributeValue)
def update_role_attributes(sender, instance, **kwargs):

    for node in instance.ref.nodes.all():
            node.recalculate_attributes()

    for group in instance.ref.groups.all():
        for node in group.nodes.all():
            node.recalculate_attributes()

@receiver(post_delete,  sender=GroupAttributeValue)
@receiver(post_save,  sender=GroupAttributeValue)
def update_group_attributes(sender, instance, **kwargs):
    for node in instance.ref.nodes.all():
        node.recalculate_attributes()

