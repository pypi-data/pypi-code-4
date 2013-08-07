# encoding: utf-8
"""
Some template tags for the weblog app. To load it use:

    {% load weblog_extras %}

``category_posts``

Get a category’s and its subcategories’ posts. By default, it will create a
context variable called ``posts`` but you can specify your own name via ``as``:

    {% category_posts category %}
    {% for post in posts %}
        ...
    {% endfor %}


    {% category_posts category as category_posts %}
    {% for post in category_posts %}
        ...
    {% endfor %}


``post_count``

Get the number of posts in a category, tag or time span (year/month).

    Number of posts in {{ date|date:'F Y' }}: {% post_count
            month=date|date:'Ym' %}
    Number of posts in {{ date|date:'Y' }}: {% post_count year=date|date:'Y' %}
    Number of posts in {{ category.name }}: {% post_count
            category=category.slug %}
    Number of posts tagged {{ tag }}: {% post_count tag=tag %}

``get_sidebar_widgets``

Get the weblog’s widgets for a sidebar (e.g. category list, archive, …)

    {% get_sidebar_widgets as widgets %}
    {% for widget in widgets %}
    <div>
        <h2>widget.title</h2>
        widget.body
    </div>
    {% endfor %}

"""
import datetime

from django import template

from weblog.models import Category, Post


register = template.Library()


class CategoryPostsNode(template.Node):
    """Retrieve all posts and put them into a context variable."""
    def __init__(self, category, var_name):
        self.category = category
        self.var_name = var_name

    def render(self, context):
        category = self.category.resolve(context)
        context['posts'] = Post.published.in_category(category)
        return ''


class PostCountNode(template.Node):
    """Renders the number of posts."""
    def __init__(self, arg_name, arg_val):
        self.arg_name = arg_name
        self.arg_val = arg_val

    def render(self, context):
        """If ``self.arg_name`` is year, month, category or tag, call the
        corresponding by_-method, else return 0."""
        method = 'by_' + self.arg_name
        if hasattr(Post.count, method):
            return getattr(Post.count, method)(self.arg_val.resolve(context))
        else:
            return ''


class SidebarWidgetsNode(template.Node):
    """Renders the weblog’s sidebar widgets."""
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        # Categories widget
        t = template.loader.get_template('weblog/_widget_categories.html')
        categories_widget = {
            'title': 'Categories',
            'content': t.render(template.Context(
                    {'category_list': Category.objects.filter(parent=None)},
                    autoescape=context.autoescape)),
        }

        # Archive widget
        # Gets links for the last six months (26 weeks) and a link for each
        # year.
        t = template.loader.get_template('weblog/_widget_archive.html')
        now_minus_six = datetime.datetime.now() - datetime.timedelta(weeks=26)
        archive_widget = {
            'title': 'Archive',
            'content': t.render(template.Context({
                'months': Post.published.filter(
                        pub_date__gte=now_minus_six).dates('pub_date', 'month',
                        order='DESC'),
                'years': [date.year for date in Post.published.dates(
                            'pub_date', 'year', order='DESC')],
                }, autoescape=context.autoescape)),
        }

        context[self.var_name] = [categories_widget, archive_widget]
        return ''


@register.tag
def category_posts(parser, token):
    """Get all posts that are in the given category or its subcategories."""
    args = token.split_contents()
    if len(args) == 2:
        category = args[1]
        var_name = 'posts'
    elif len(args) == 4 and args[2] == 'as':
        category = args[1]
        var_name = args[3]
    else:
        raise template.TemplateSyntaxError(
                '%r tag requires one or three arguments.' % args[0])
    return CategoryPostsNode(template.Variable(category), var_name)


@register.tag
def post_count(parser, token):
    """
    Get the number of posts in a specified year/month, category of with a
    certain tag.

    """
    try:
        tag_name, args = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
                '%r tag requires a single argument' %
                token.contents.split()[0])
    try:
        arg_name, arg_val = args.split('=')
    except ValueError:
        raise template.TemplateSyntaxError(
                'Argument %r for %r tag must be specified as "arg=val"' %
                (tag_name, args))
    return PostCountNode(arg_name, parser.compile_filter(arg_val))


@register.tag
def get_sidebar_widgets(parser, token):
    """Get all sidebar widgets and store them in a template variable."""
    try:
        tagname, _as, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('%r tag requires two arguments.' %
                token.contents.split()[0])
    return SidebarWidgetsNode(var_name)
