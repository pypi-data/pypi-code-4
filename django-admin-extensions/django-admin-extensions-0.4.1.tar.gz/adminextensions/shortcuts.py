from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.template.defaultfilters import truncatewords
from django.utils.html import escape


def model_search(text, model, args):
    """
    An object tool to link to a change list with a preloaded search term

    `text` is the label to use on the object tool, while `model` is the model
    class to link to. `args` is a callable that should return a `dict` of
    querystring arguments when passed an instance of the original model.

    Usage:

        class AuthorModelAdmin(ExtendedModelAdmin):
            object_tools = {
                'change': [model_search(
                    "Books", Book,
                    lambda author: {'author__id': author.id})]
            }
    """

    app_label = model._meta.app_label
    module_name = model._meta.module_name

    url_name = 'admin:%s_%s_changelist' % (app_label, module_name)

    def tool(context, link_class="model_search"):

        url = reverse(url_name)

        qd = QueryDict(None, mutable=True)
        qd.update(args(context['original']))

        query_string = qd.urlencode()
        search_url = url + '?' + query_string

        return print_link(text, search_url, link_class)
    tool.do_not_call_in_templates = True
    return tool


def model_link(text, model, pk_getter, action="change"):
    """
    An object tool to link to a related model from a models page
    Used in `list_display` to link to a related model instance's view/edit page

    `pk_getter` can be either a string naming the pk field of the related
    model, or a callable which returns the pk of the related model.

    `action` can be any of the admin actions: 'change', 'history', or 'delete'.
    The default is 'change'

    Usage:

        class BookModelAdmin(ExtendedModelAdmin):
            object_tools = {
                'change': [model_link("Author", Author, 'author_id')]
            }
    """

    app_label = model._meta.app_label
    module_name = model._meta.module_name

    if isinstance(pk_getter, basestring):
        pk_name = pk_getter
        pk_getter = lambda object: getattr(object, pk_name)

    def tool(context, link_class="model_search"):
        pk = pk_getter(context['original'])
        if pk:
            url = make_admin_url(model, pk=pk, action=action)
            return print_link(text, url, link_class)
        else:
            return ''
    tool.do_not_call_in_templates = True
    return tool


def make_admin_url(model, pk=None, action="change"):
    """
    Given a model and an action, make a url to the correct admin page

    If `model` is a model instance, that models `pk` is used as the instance to
    link to. Otherwise, a `pk` to link to must be provided. The function can
    thus be used with either a model instance, or a Model class and a `pk`.

    Usage:
        make_admin_url(Foo, pk=10)  # '/admin/app/foo/10/'

        foo = Foo.objects.get(pk=4)
        make_admin_url(foo)  # '/admin/app/foo/4/'
        make_admin_url(foo, action="delete")  # '/admin/app/foo/delete/4/'

    """
    app_label = model._meta.app_label.lower()
    module_name = model._meta.module_name
    url_name = "admin:%s_%s_%s" % (app_label, module_name, action)

    if pk is None:
        pk = model.pk

    url = reverse(url_name, args=(pk,))
    return url


def link_field(field, action="change", formatter=unicode,
               short_description=None):
    """
    An list field item that links to a related model instance from the
    changelist view

    `field` is the name of the related model on the source model.

    `action` can be any of the admin actions: 'change', 'history', or 'delete'.
    The default is 'change'

    `formatter` is used to transform the related model to a string. The default
    is to call the `__unicode__()` method on the instance.

    `short_description` is used as the column header. It defaults to the field
    name.

    Usage:

        class BookModelAdmin(ExtendedModelAdmin):
            list_display = ('name', link_field('author'))
    """

    if short_description is None:
        short_description = field

    def item(obj):
        related = getattr(obj, field)
        if related is None:
            return '(None)'

        url = make_admin_url(related, action=action)
        name = formatter(related)

        link = print_link(escape(name), url)

        return link

    item.short_description = short_description
    item.allow_tags = True
    return item


def serialized_many_to_many_field(field, formatter=unicode, joiner=', ',
                                  short_description=None, linked=False):
    """
    Display all the related instances in a ManyToMany relation

    `field` is the name of the relation on the source model.

    `formatter` is used to transform the related instance to a string. The
    default is to call the `__unicode__()` method on the instance.

    `joiner` is inserted between every instance. Defaults to ', '

    `short_description` is used as the column header. It defaults to the field
    name.

    If `linked` is True, each model instance is linked to its `change` view.

    Usage:

        class BookModelAdmin(ExtendedModelAdmin):
            list_display = ('name', serialized_many_to_many_field('publishers'))
    """
    if short_description is None:
        short_description = field

    old_formatter = formatter
    if linked:
        formatter = lambda obj: print_link(escape(old_formatter(obj)), make_admin_url(obj))
    else:
        formatter = lambda obj: escape(old_formatter(obj))

    item = lambda obj: joiner.join(formatter(x) for x in getattr(obj, field).all())
    item.allow_tags = True
    item.short_description = short_description

    return item


def truncated_field(field, length=20, short_description=None):
    """
    Display a truncated version of `field` in the list display

    The field is limited to `length` words, using Djangos `truncatewords`
    helper.

    `short_description` is used as the column header. It defaults to the field
    name.

    Usage:

        class BookModelAdmin(ExtendedModelAdmin):
            list_display = ('name', serialized_many_to_many_field('publishers'))
    """
    if short_description is None:
        short_description = field

    item = lambda obj: truncatewords(getattr(obj, field), length)
    item.short_description = short_description
    return item


def related_field(field, formatter=None, short_description=None):
    """
    Show a related field in `list_display`

    `field` is the double-underscore-delimited path to the field to display,
    such as `author__name`.

    `formatter` takes the value and formats it for display. The default is to
    just return the value. The Django admin is fairly sensible at formatting
    things.

    `short_description` is used as the column header. It defaults to `field`.
    """

    if short_description is None:
        short_description = field

    if formatter is None:
        formatter = lambda x: x

    field_path = field.split('__')

    item = lambda obj: formatter(reduce(getattr, field_path, obj))
    item.allow_tags = False
    item.short_description = short_description
    item.admin_order_field = field

    return item


def print_link(text, url, class_name=""):
    """
    Prints an HTML link, given the inner text, a url, and an optional class
    name. None of the inputs are escaped.
    """
    return u'<a href="%s" class="%s">%s</a>' % (url, class_name, text)
