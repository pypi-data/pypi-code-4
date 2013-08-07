# encoding: utf-8
"""
Admin interface for the weblog app.

"""
from django import forms
from django.contrib import admin

from weblog import fields
from weblog.models import Category, Post


class CategoryForm(forms.ModelForm):
    """
    The category form helps to prevent circular references in parentships.

    """

    parent = fields.CategoryModelChoiceField(queryset=Category.objects.all(),
            required=False)

    class Meta:
        model = Category

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            # Filter out all categories that contain the current category in
            # their path to avoid circular references.
            self.fields['parent'].queryset = Category.objects.exclude(
                    path__contains=self.instance.slug)

    def clean_parent(self):
        """
        Check if the category is its own parent. If it is, iterate over all
        parents until the category isn’t its own parent any longer and return
        that parent.

        """
        parent = self.cleaned_data['parent']

        if not parent or self.cleaned_data['slug'] not in parent.path:
            return parent

        while parent and self.cleaned_data['slug'] in parent.path:
            parent = parent.parent
        return parent


class PostForm(forms.ModelForm):
    """Use a custom field for categories and the fancy widgegt."""

    categories = fields.CategoryModelMultipleChoiceField(
            queryset=Category.objects.all(), required=False,
            widget=admin.widgets.FilteredSelectMultiple(
                    Post.categories.field.verbose_name, False))

    class Meta:
        model = Post


class CategoryAdmin(admin.ModelAdmin):
    """Except for the form, there’s nothing special in the category admin."""
    list_display = ('form_display_name', 'path',)
    form = CategoryForm
    prepopulated_fields = {'slug': ('name',)}


class PostAdmin(admin.ModelAdmin):
    """
    Use a custom form for posts. The post author will be automatically added
    when the post is saved.

    """
    list_display = ('title', 'pub_date', 'modify_date', 'author', 'status',
            'enable_comments')
    list_filter = ('categories', 'status', 'author')
    date_hierarchy = 'pub_date'
    ordering = ['-pub_date']
    search_fields = ('title', 'body')
    # TODO: actions = ()

    form = PostForm
    fieldsets = (
        (None, {
            'fields': ('title', 'body', 'status'),
        }),
        ('Meta', {
            'fields': ('pub_date', 'slug', 'enable_comments'),
            'classes': ('collapse',),
        }),
        ('Categorization', {
            'fields': ('categories',),
        }),
    )
    prepopulated_fields = {'slug': ('title',)}
    radio_fields = {'status': admin.HORIZONTAL}
    # TODO: formfield_overrides = {
    #     models.TextField: {'widget': RichTextEditorWidget},
    # }

    def save_model(self, request, obj, form, change):
        """Set the currently logged in user as author for this post."""
        if not change:
            obj.author = request.user
        obj.save()


admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
