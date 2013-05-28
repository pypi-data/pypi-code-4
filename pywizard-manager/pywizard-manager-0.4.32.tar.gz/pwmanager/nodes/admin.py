from django.contrib import admin
from django.contrib.admin.widgets import AdminTextInputWidget
from django.forms import ModelForm, TextInput
from suit.widgets import AutosizedTextarea, LinkedSelect
from pwmanager.nodes.models import Node, NodeGroup, Role, NodeAttributeValue, ProvisionPackage, GroupAttributeValue, RoleAttributeValue
from django.db import models


default_overrides = {
    models.CharField: {'widget': TextInput(attrs={'class': 'span5'})},
    models.TextField: {'widget': AutosizedTextarea(attrs={'rows': 3, 'class': 'span5'})},
    # models.ForeignKey: {'widget': LinkedSelect},
}

class NodeAttributeInline(admin.TabularInline):
    formfield_overrides = default_overrides
    extra = 10
    fields = ('name', 'value', 'inherited_value', 'inherited_from',)
    readonly_fields = ('inherited_value', 'inherited_from',)
    model = NodeAttributeValue


class NodeAdmin(admin.ModelAdmin):
    formfield_overrides = default_overrides
    list_filter = ('group',)
    list_display = ('group', 'name', 'format_full_name', 'config_link', 'node_link', 'role_list_display', 'group_role_list_display')
    list_display_links = ('name',)
    prepopulated_fields = {"short_name": ("name",)}

    fieldsets = (
        (None, {
            'fields': ('name', 'group', 'short_name', 'description', 'roles')
        }),
        # ('Context', {
        #     'classes': ('collapse', 'wide'),
        #     'fields': ('formatted_context',)
        # }),
    )

    readonly_fields = ('formatted_context',)
    inlines = [
        NodeAttributeInline,
    ]
admin.site.register(Node, NodeAdmin)


class NodePakcagesInline(admin.TabularInline):
    formfield_overrides = default_overrides
    model = ProvisionPackage
    readonly_fields = ('date_uploaded',)
    fields = ('date_uploaded',)
    extra = 0


class NodeGroupAttributesInline(admin.TabularInline):
    formfield_overrides = default_overrides
    extra = 10
    model = GroupAttributeValue


class NodeGroupAdmin(admin.ModelAdmin):
    formfield_overrides = default_overrides
    inlines = [
        NodeGroupAttributesInline,
        NodePakcagesInline,
    ]
    list_display = ('name', 'short_name', 'list_attrs', 'list_roles', 'list_nodes')

admin.site.register(NodeGroup, NodeGroupAdmin)


class RoleAttributesInline(admin.TabularInline):
    formfield_overrides = default_overrides
    extra = 10
    model = RoleAttributeValue


class RoleAdmin(admin.ModelAdmin):
    formfield_overrides = default_overrides
    inlines = [
        RoleAttributesInline,
    ]

admin.site.register(Role, RoleAdmin)