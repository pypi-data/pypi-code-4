from django.db import models
from django.template.loader import get_template_from_string
from django.template import Context

from preferences.models import Preferences
from ckeditor.fields import RichTextField
from south.modelsinspector import add_introspection_rules
from foundry.models import Menu, Navbar, Page


DRAFT_TEMPLATE = '''
{% load i18n %}
<html>
<body>

{% if navbars %}
    {% trans "Navbars" %}:
    <ul>
    {% for navbar in navbars %}
        <li>{{ navbar.title }}</li>
        <li>
            <ul>
                {% for link in navbar.links %}            
                    <li><a href="{{ link.get_absolute_url }}">{{ link.title }}</a></li>
                {% endfor %}
            </ul>
        </li>
    {% endfor %}
    </ul>
{% endif %}

{% if menus %}
    {% trans "Menus" %}:
    <ul>
    {% for menu in menus %}
        <li>{{ menu.title }}</li>
        <li>
            <ul>
                {% for link in menu.links %}            
                    <li><a href="{{ link.get_absolute_url }}">{{ link.title }}</a></li>
                {% endfor %}
            </ul>
        </li>
    {% endfor %}
    </ul>
{% endif %}

{% if pages %}
    {% trans "Pages" %}:
    <ul>
    {% for page in pages %}
        <li><a href="{{ page.get_absolute_url }}">{{ page.title }}</a></li>
    {% endfor %}
    </ul>
{% endif %}

</body>
<html>
'''


class HTMLSitemap(Preferences):
    content = RichTextField(null=True, blank=True)
    draft = RichTextField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'HTML Sitemap'

    def generate_draft(self):
        # Assemble navbars, menus and pages in a structure
        navbars = []
        for navbar in Navbar.objects.filter(sites__in=self.sites.all())\
            .order_by('title'):
            navbar.links = []
            for o in navbar.navbarlinkposition_set.select_related()\
                .all().order_by('position'):
                navbar.links.append(o.link)
            navbars.append(navbar)
        menus = []
        for menu in Menu.objects.filter(sites__in=self.sites.all())\
            .order_by('title'):
            menu.links = []
            for o in menu.menulinkposition_set.select_related().all()\
                .order_by('position'):
                menu.links.append(o.link)
            menus.append(menu)
        pages = Page.objects.filter(sites__in=self.sites.all())\
            .order_by('title')

        # Render
        template = get_template_from_string(DRAFT_TEMPLATE)
        c = dict(navbars=navbars, menus=menus, pages=pages)
        html = template.render(Context(c))

        # Save draft
        self.draft = html
        self.save()

    def make_draft_live(self):
        self.content = self.draft
        self.draft = ''
        self.save()


# Custom fields to be handled by south
add_introspection_rules([], ["^ckeditor\.fields\.RichTextField"])
