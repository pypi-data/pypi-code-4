from django.utils import unittest
from django.test.client import Client, RequestFactory
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.conf import settings

from preferences import preferences
from foundry.models import Navbar, Menu, Page, Link, NavbarLinkPosition, \
    MenuLinkPosition


class TestCase(unittest.TestCase):

    @classmethod  
    def setUpClass(cls):
        cls.request = RequestFactory()
        cls.client = Client()

        # Add an extra site
        site = Site.objects.create(name='mobi', domain='mobi.com')

        # Links
        web_navbar_link = Link.objects.create(
            title='Web navbar link', url='/web-navbar-link'
        )
        mobi_navbar_link = Link.objects.create(
            title='Mobi navbar link', url='/mobi-navbar-link'
        )
        web_menu_link = Link.objects.create(
            title='Web menu link', url='/web-menu-link'
        )
        mobi_menu_link = Link.objects.create(
            title='Mobi menu link', url='/mobi-menu-link'
        )

        # Navbars
        navbar = Navbar.objects.create(title='Wev navbar', slug='web-navbar')
        navbar.sites = [1]
        navbar.save()
        pos = NavbarLinkPosition.objects.create(
            navbar=navbar, link=web_navbar_link, position=1
        )
        navbar = Navbar.objects.create(title='Mobi navbar', slug='mobi-navbar')
        navbar.sites = [2]
        navbar.save()
        pos = NavbarLinkPosition.objects.create(
            navbar=navbar, link=mobi_navbar_link, position=1
        )

        # Menus
        menu = Menu.objects.create(title='Web menu', slug='web-menu')
        menu.sites = [1]
        menu.save()
        pos = MenuLinkPosition.objects.create(
            menu=menu, link=web_menu_link, position=1
        )
        menu = Menu.objects.create(title='Mobi menu', slug='mobi-menu')
        menu.sites = [2]
        menu.save()
        pos = MenuLinkPosition.objects.create(
            menu=menu, link=mobi_menu_link, position=1
        )

        # Pages
        page = Page.objects.create(title='Web page', slug='web-page')
        page.sites = [1]
        page.save()
        page = Page.objects.create(title='Mobi page', slug='mobi-page')
        page.sites = [2]
        page.save()

    def test_xml(self):
        xml = self.client.get(reverse('sitemap')).content
        self.failUnless('web-navbar-link' in xml)
        self.failIf('mobi-navbar-link' in xml)
        self.failUnless('web-menu-link' in xml)
        self.failIf('mobi-menu-link' in xml)

    def test_html(self):
        # Create html sitemap
        hsm = preferences.HTMLSitemap
        hsm.generate_draft()
        hsm.make_draft_live()

        # Test rendering
        html = self.client.get(reverse('html-sitemap')).content
        self.failUnless('web-navbar-link' in html)
        self.failIf('mobi-navbar-link' in html)
        self.failUnless('web-menu-link' in html)
        self.failIf('mobi-menu-link' in html)
