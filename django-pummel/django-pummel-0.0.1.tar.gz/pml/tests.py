from unittest import TestCase

from django.template import Template, Context
from django.test.client import Client
from BeautifulSoup import BeautifulSoup, Tag

from pml.utils import remove_comments, swap_tags, html_to_text


class PummelUtilTestCase(TestCase):

    def test_remove_comments(self):
        soup = BeautifulSoup('<!-- hello world --><b>bold</b>')
        self.assertEqual('<b>bold</b>',
                         remove_comments(soup).renderContents())

    def test_swap_tags(self):
        soup = BeautifulSoup('<b>bold</b>')
        soup = swap_tags(soup, [('b', 'strong')])
        self.assertEqual('<strong>bold</strong>',
                         soup.renderContents())

    def test_swap_tags_with_callable(self):
        def replace_with_p(soup, tag):
            replacement_tag = Tag(soup, 'p')
            replacement_tag.insert(0, '- %s' % tag.text)
            return replacement_tag

        soup = BeautifulSoup('<li>list</li>')
        soup = swap_tags(soup, [('li', replace_with_p)])
        self.assertEqual('<p>- list</p>',
                         soup.renderContents())

    def test_html_to_text(self):
        text = html_to_text(
            """
            <a href="#">hello world</a>
            <ul>
                <li>list item 1</li>
                <li>list item 2</li>
                <li>list item 3</li>
            </ul>
            """)
        self.assertEqual(text.strip(), (
            "<LINK href=\"#\">hello world</LINK>\n"
            "<p>"
            "- list item 1<br />"
            "- list item 2<br />"
            "- list item 3<br />"
            "</p>").strip())


class PummelTemplateTagTestCase(TestCase):

    def render_template(self, template_string, context):
        return Template(template_string).render(Context(context))

    def test_text_module_tag(self):
        response = self.render_template("""
            {% load pml_inclusion_tags %}
            {% spaceless %}
                {% text_module html="{{foo}}" %}
            {% endspaceless %}
            """, {'foo': 'bar'})
        self.assertEqual(response.strip(), (
            '<MODULE>'
            '<CONTAINER type="data">'
            '<TEXT><p>{{foo}}</p></TEXT>'
            '</CONTAINER>'
            '</MODULE>'
        ))

    def test_text_module_tag_with_var_as_html(self):
        response = self.render_template("""
            {% load pml_inclusion_tags %}
            {% spaceless %}
                {% with foo='bar' %}
                {% text_module html=foo %}
                {% endwith %}
            {% endspaceless %}
            """, {})
        self.assertEqual(response.strip(), (
            '<MODULE>'
            '<CONTAINER type="data">'
            '<TEXT><p>bar</p></TEXT>'
            '</CONTAINER>'
            '</MODULE>'
        ))

    def test_text_module_tag_with_template(self):
        response = self.render_template("""
            {% load pml_inclusion_tags %}
            {% spaceless %}
                {% text_module template="{{foo}}" %}
            {% endspaceless %}
            """, {'foo': 'bar'})
        self.assertEqual(response.strip(), (
            '<MODULE>'
            '<CONTAINER type="data">'
            '<TEXT><p>bar</p></TEXT>'
            '</CONTAINER>'
            '</MODULE>'
        ))

    def test_text_module_tag_with_link(self):
        response = self.render_template("""
            {% load pml_inclusion_tags %}
            {% spaceless %}
                {% text_module template="<small><a href='/about/'>About</a></small>" %}
            {% endspaceless %}
            """, {})
        self.assertEqual(response.strip(), (
            '<MODULE>'
            '<CONTAINER type="data">'
            '<TEXT><p><small><LINK href="/about/">About</LINK></small></p></TEXT>'
            '</CONTAINER>'
            '</MODULE>'
        ))

    def test_text_module_tag_with_html(self):
        response = self.render_template("""
            {% load pml_inclusion_tags %}
            {% spaceless %}
                {% text_module template="<small>&copy; {{year}}</small>" %}
            {% endspaceless %}
            """, {'year': 2013})
        self.assertEqual(response.strip(), (
            '<MODULE>'
            '<CONTAINER type="data">'
            '<TEXT><p><small>&#169; 2013</small></p></TEXT>'
            '</CONTAINER>'
            '</MODULE>'
        ))

    def test_text_module_tag_for_download(self):
        response = self.render_template("""
            {% load pml_inclusion_tags %}
            {% spaceless %}
                {% text_include template='pml/tests/download_inline_block.html' %}
            {% endspaceless %}
            """, {})
        self.assertEqual(response.strip(), (
            '<MODULE>'
            '<CONTAINER type="data">'
            '<TEXT><p>'
            '<LINK href="http://yal.pf.org/download/">'
            'Click here to download This Amazing download now!!!!'
            '</LINK>'
            '</p></TEXT>'
            '</CONTAINER>'
            '</MODULE>'
        ))

    def test_page_banner_include(self):
        response = self.render_template("""
            {% load pml_inclusion_tags %}
            {% spaceless %}
                {% page_banner_include image_url='/some/image/' template='pml/tests/object_detail_header_include.html' %}
            {% endspaceless %}
            """, {})

        self.assertEqual(response.strip(), (
            '<MODULE>'
            '<CONTAINER type="data">'
            '<GALLERY>'
            '<ITEM>'
            '<IMAGE href="/some/image/" float="true" align="" mime-type="image/jpeg" />'
            '<TEXT><p><color value="#E40BBA">Title</color><br />'
            '<color value="#666666">Published</color>'
            '</p></TEXT>'
            '</ITEM>'
            '</GALLERY>'
            '</CONTAINER>'
            '</MODULE>'
        ))

    def test_thumbnail_include_tag(self):
        response = self.render_template("""
            {% load pml_inclusion_tags %}
            {% spaceless %}
                {% thumbnail_include image_url='#' template="pml/tests/modelbase_block_include.html" %}
            {% endspaceless %}
            """, {})
        self.assertEqual(response.strip(), (
            '<MODULE>'
            '<CONTAINER type="data">'
            '<GALLERY>'
            '<ITEM>'
            '<IMAGE href="#" float="true" align="left" mime-type="image/jpeg" />'
            '<TEXT><p>'
            '<LINK href="/link/">Title</LINK><br />'
            '<small>Published date</small><br />'
            '<small>Comments</small>'
            '</p></TEXT>'
            '</ITEM>'
            '</GALLERY>'
            '</CONTAINER>'
            '</MODULE>'
        ))


    def test_clickable_banner_tag(self):
        response = self.render_template("""
            {% load pml_inclusion_tags %}
            {% spaceless %}
                {% clickable_banner_include image_url='#' link_url='/live/' template="pml/tests/promo_block_include.html" %}
            {% endspaceless %}
            """, {})
        self.assertEqual(response.strip(), (
            '<MODULE>'
            '<CONTAINER type="data">'
            '<TEXT>'
            '<LINK href="/live/">'
            '<IMAGE href="#" align="full" type="image/jpeg"/>'
            '<TEXT><p><LINK href="/live/">This</LINK> is a promo description\n'
            '</p></TEXT>'
            '</LINK>'
            '</TEXT>'
            '</CONTAINER>'
            '</MODULE>'
        ))

    def test_html_sanitize(self):
        def render_html(html):
            return self.render_template("""
                {% load pml_inclusion_tags %}
                {% spaceless %}
                    {% text_module template="{{html|safe}}" %}
                {% endspaceless %}
                """, {'html': html})
        response = render_html('&ldquo;Hello&rdquo;')
        self.assertEqual(response.strip(), (
            '<MODULE>'
            '<CONTAINER type="data">'
            '<TEXT>'
            '<p>"Hello"</p>'
            '</TEXT>'
            '</CONTAINER>'
            '</MODULE>'
        ))
        response = render_html('&lsquo;Hello&rsquo;')
        self.assertEqual(response.strip(), (
            '<MODULE>'
            '<CONTAINER type="data">'
            '<TEXT>'
            '<p>\'Hello\'</p>'
            '</TEXT>'
            '</CONTAINER>'
            '</MODULE>'
        ))
        response = render_html('&quot;Hello&quot;')
        self.assertEqual(response.strip(), (
            '<MODULE>'
            '<CONTAINER type="data">'
            '<TEXT>'
            '<p>"Hello"</p>'
            '</TEXT>'
            '</CONTAINER>'
            '</MODULE>'
        ))
        response = render_html('Hello&ndash;World')
        self.assertEqual(response.strip(), (
            '<MODULE>'
            '<CONTAINER type="data">'
            '<TEXT>'
            '<p>Hello-World</p>'
            '</TEXT>'
            '</CONTAINER>'
            '</MODULE>'
        ))
        response = render_html('Hello&ndash;World')
        self.assertEqual(response.strip(), (
            '<MODULE>'
            '<CONTAINER type="data">'
            '<TEXT>'
            '<p>Hello-World</p>'
            '</TEXT>'
            '</CONTAINER>'
            '</MODULE>'
        ))
        response = render_html('Hello&hellip;')
        self.assertEqual(response.strip(), (
            '<MODULE>'
            '<CONTAINER type="data">'
            '<TEXT>'
            '<p>Hello...</p>'
            '</TEXT>'
            '</CONTAINER>'
            '</MODULE>'
        ))


class PummeliMiddlewareTestCase(TestCase):
    def test_redirect_respects_ignore_paths(self):
        client = Client()
        response = client.get('/')
        self.assertEquals(response['Content-Type'], 'text/xml')

        response = client.get('/admin/')
        self.assertEquals(response['Content-Type'], 'text/html; charset=utf-8')

        response = client.get('/redirect/')
        self.assertEquals(response['Content-Type'], 'text/html; charset=utf-8')
