# encoding: utf-8
"""
Tests for the Django weblog app.

"""
from django.template import TemplateSyntaxError
from django.test import TestCase
import mock

from weblog.models import Category, Post
import weblog.templatetags.weblog_extras as weblog_tags


class CategoryTestCase(TestCase):

    fixtures = ['weblog.json']

    def setUp(self):
        self.p1 = Category.objects.get(pk=1)
        self.c1 = Category.objects.get(pk=2)

    def test_basic(self):
        self.assertEqual(self.p1.name, u'P1')
        self.assertEqual(self.p1.slug, u'p1')
        self.assertEqual(self.p1.parent, None)

        self.assertEqual(self.c1.name, u'C1')
        self.assertEqual(self.c1.slug, u'c1')
        self.assertEqual(self.c1.parent, self.p1)

    def test_illegal_parenthood(self):
        def do_parent():
            self.p1.parent = self.p1
            self.p1.save()
        self.assertRaises(ValueError, do_parent)

        def do_grandparent():
            self.p1.parent = self.c1
            self.p1.save()
        self.assertRaises(ValueError, do_grandparent)

    def test_path_items(self):
        self.assertEqual(self.p1.path_items, [self.p1])
        self.assertEqual(self.c1.path_items, [self.p1, self.c1])

    def test_parent_count(self):
        self.assertEqual(self.p1.parent_count, 0)
        self.assertEqual(self.c1.parent_count, 1)

    def test_create_path(self):
        self.assertEqual(self.p1.path, u'p1/')
        self.assertEqual(self.c1.path, u'p1/c1/')
        self.assertEqual(self.p1._create_path(), u'p1/')
        self.assertEqual(self.c1._create_path(), u'p1/c1/')
        sub = self.c1.subcategories.create(name='Sub')
        self.assertEqual(sub.path, u'p1/c1/sub/')
        self.p1.slug = 'foo'
        self.p1.save()
        c1 = self.p1.subcategories.all()[0]
        sub = c1.subcategories.all()[1]
        self.assertEqual(self.p1.path, u'foo/')
        self.assertEqual(c1.path, u'foo/c1/')
        self.assertEqual(sub.path, u'foo/c1/sub/')

    def test_form_display_name(self):
        self.assertEqual(self.p1.form_display_name, u'P1')
        self.assertEqual(self.c1.form_display_name, u'– C1')


class PostTestCase(TestCase):

    fixtures = ['weblog.json']

    def setUp(self):
        self.p1 = Post.objects.get(pk=1)
        self.p2 = Post.objects.get(pk=2)
        self.p3 = Post.objects.get(pk=3)

    def test_year(self):
        self.assertEqual(self.p1.year, '2009')

    def test_month(self):
        self.assertEqual(self.p1.month, '10')

    def test_day(self):
        self.assertEqual(self.p1.day, '06')

    def test_published_posts(self):
        self.assertEqual(Post.published.count(), 2)

    def test_posts_in_category(self):
        c = Category.objects.get(pk=2)
        self.assertEqual(Post.published.in_category(c).count(), 1)
        self.assertEqual(Post.published.in_category(c)[0], self.p2)

    def test_post_by_date_and_slug(self):
        self.assertEqual(Post.published.by_date_and_slug(2009, 10, 7, 'post2'),
                self.p2)

    def test_post_count(self):
        self.assertEqual(Post.count.by_year(2009), 2)
        self.assertEqual(Post.count.by_year('2009'), 2)
        self.assertEqual(Post.count.by_year(2010), 0)
        self.assertEqual(Post.count.by_month(2009, 10), 2)
        self.assertEqual(Post.count.by_month('200910'), 2)
        self.assertEqual(Post.count.by_month(2010, 1), 0)
        self.assertEqual(Post.count.by_category(Category.objects.get(pk=1)), 1)
        self.assertEqual(Post.count.by_category(None), 1)
        # TODO: self.assertEqual(Post.count.by_tag('eggs'), 1)


class TemplateTagsTestCase(TestCase):
    """Test the template tags."""

    fixtures = ['weblog.json']

    def setUp(self):
        self.parser = mock.Mock(spec=['compile_filter'])
        self.token = mock.Mock(spec=['split_contents'])

    @mock.patch('django.template.Variable')
    def test_category_posts(self, Variable):
        tag = 'post_count'
        var_names = ['posts', 'category_posts']
        args = (
            ('category',),
            ('category', 'as', var_names[1]),
        )
        for arg, var_name in zip(args, var_names):
            self.token.split_contents.return_value = (tag,) + arg
            node = weblog_tags.category_posts(self.parser, self.token)

            self.assertEqual(node.category, Variable.return_value)
            self.assertEqual(Variable.call_args, (arg[0:1], {}))
            self.assertEqual(node.var_name, var_name)

    def test_category_posts_node(self):
        context = {}
        var_name = 'posts'
        category = mock.Mock(spec=['resolve'])
        category.resolve.return_value = Category.objects.get(pk=1)
        node = weblog_tags.CategoryPostsNode(category, var_name)
        node.render(context)

        self.assertTrue(var_name in context)
        self.assertEqual(len(context[var_name]), 1)
        self.assertTrue(Post.objects.get(pk=2) in context[var_name])

    @mock.patch('django.template.Variable')
    def test_post_count(self, Variable):
        tag = 'post_count'
        arg = 'year=date|date:"Y"'
        self.parser.compile_filter.return_value = Variable(arg)
        self.token.split_contents.return_value = (tag, arg)

        node = weblog_tags.post_count(self.parser, self.token)
        self.assertEqual(node.arg_name, 'year')
        self.assertEqual(node.arg_val, Variable.return_value)
        self.assertEqual(Variable.call_args, ((arg,), {}))

        self.token.split_contents.return_value = ('post_count', 'year', 'date')
        self.token.contents = 'post_count'
        try:
            node = weblog_tags.post_count(self.parser, self.token)
            self.fail()
        except TemplateSyntaxError:
            pass

        self.token.split_contents.return_value = ('post_count', 'date')
        try:
            node = weblog_tags.post_count(self.parser, self.token)
            self.fail()
        except TemplateSyntaxError:
            pass

    @mock.patch('django.template.Variable', spec=['resolve'])
    def test_post_count_node(self, Variable):
        data = (
            ('year', '2009', 2),
            ('month', '200910', 2),
            ('category', None, 1),
            # TODO: ('tag', 'tag', 'spam'),
        )
        context = {}

        for arg_name, ret_val, result in data:
            node = weblog_tags.PostCountNode(arg_name, Variable())
            node.arg_val.resolve.return_value = ret_val
            self.assertEqual(node.render(context), result)

        node = weblog_tags.PostCountNode('foo', 'bar')
        self.assertEqual(node.render(context), '')

    def test_get_sidebar_widgets(self):
        tag = 'get_sidebar_widgets'
        var_name = 'widgets'
        self.token.split_contents.return_value = (tag, 'as', var_name)

        node = weblog_tags.get_sidebar_widgets(self.parser, self.token)
        self.assertEqual(node.var_name, var_name)

    @mock.patch('django.template.loader.get_template')
    @mock.patch('django.template.Context')
    def test_sidebar_widgets_node(self, get_template, Context):
        class ContextMock(dict):
            autoescape = object()
        context = ContextMock()
        # template = get_template.return_value

        var_name = 'widgets'
        node = weblog_tags.SidebarWidgetsNode(var_name)
        node.render(context)

        self.assertTrue(var_name in context)
        for widget in context[var_name]:
            self.assertTrue('title' in widget)
            self.assertTrue('content' in widget)


# class URLTestCase(unittest.TestCase):
#     """Test the weblog urls."""
#
#     def test_urls(self):
#         urls = (
#             '/page/1/',
#             '/page/12/',
#             '/arcive/',
#             '/2009/10/11/foo/df'
#         )
#         c = client.Client()
#         for url in urls:
#             response = c.post(url)
#             self.assertEqual(response.status_code, 200, 'Url: %s' % url)
