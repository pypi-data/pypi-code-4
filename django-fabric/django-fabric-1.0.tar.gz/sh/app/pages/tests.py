# -*- coding: utf-8 -*-
from datetime import datetime
from django.conf import settings
from sh.app.pages.models import Page, PageRevision
from sh.core.tests import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

class PagesTest(TestCase):

    def setUp(self):
        super(PagesTest, self).setUp()
        self.frontpage = Page.objects.create(
            id=settings.FRONTPAGE_ID,
            created_by_id=1,
            saved_by_id=1,
            date_created=datetime(2012,02,02, 02, 02, 00),
            date_saved=datetime(2012,02,02, 02, 02, 00),
            title='Super frontpage',
            content='Masse fint innhold',
            weight=0
        )

        self.client = Client()

    def testViews(self):
        self.assertEqual(self.frontpage.slug, 'super-frontpage')
        self.assertEqual(PageRevision.objects.all().count(), 1)

        response_with_slug = self.client.get(reverse('view_page', args=[self.frontpage.slug]))
        self.assertEqual(response_with_slug.status_code, 200)

        response_fp = self.client.get(reverse('view_page'))
        self.assertEqual(response_fp.status_code, 200)

        self.assertEqual(response_with_slug.context['page'], response_fp.context['page'])

    def tearDown(self):
        self.frontpage.delete()
        super(PagesTest, self).tearDown()