"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import os

from django.test import TestCase
from django.test.client import Client
from django.http import Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Permission

from .models import Timeline, TimelineImporter


class TestTimelinePermissions(TestCase):

    def setUp(self):
        self.timeline = Timeline.objects.create(
                title='Test Timeline',
                slug='test-timeline',
        )
        self.c = Client()
        self.u = User.objects.create_user('test', password='test')
        self.u.is_staff = True
        self.u.save()
        p1 = Permission.objects.get_by_natural_key('view_private_timelines', 'timelinejs', 'timeline')
        p2 = Permission.objects.get_by_natural_key('add_timeline', 'timelinejs', 'timeline')
        self.u.user_permissions.add(p1)
        self.u.user_permissions.add(p2)

    def test_private_timelines_anonymous(self):
        """
        Test visibility of private timelines.
        """
        ts = Timeline.objects.visible_to_user()
        self.assertEquals(1, len(ts), "Anonymous user should see public timelines.")
        self.timeline.private = True
        self.timeline.save()
        ts = Timeline.objects.visible_to_user()
        self.assertEquals(0, len(ts), "Anonymous user should not see private timelines.")

    def test_private_timelines_anonymous_ui(self):
        """
        Test visibility of private timelines.
        """
        resp = self.c.get(reverse('timelines'))
        self.assertContains(resp, self.timeline.title)
        self.timeline.private = True
        self.timeline.save()
        resp = self.c.get(reverse('timelines'))
        self.assertNotContains(resp, self.timeline.title)

    def test_add_timelines_anonymous_ui(self):
        resp = self.c.get(reverse('timelines'))
        self.assertNotContains(resp, reverse('admin:timelinejs_timeline_add'))

    def test_add_timelines_authenticated_ui(self):
        self.c.login(username='test', password='test')
        resp = self.c.get(reverse('timelines'))
        self.assertContains(resp, reverse('admin:timelinejs_timeline_add'))

    def test_private_timelines_authenticated(self):
        self.timeline.private = True
        self.timeline.save()
        ts = Timeline.objects.visible_to_user(user=self.u)
        self.assertEquals(1, len(ts), "Authenticated user should see private timelines.")

    def test_private_timelines_authenticated_ui(self):
        """
        Test visibility of private timelines.
        """
        self.c.login(username='test', password='test')
        resp = self.c.get(reverse('timelines'))
        self.assertContains(resp, self.timeline.title)
        self.timeline.private = True
        self.timeline.save()
        resp = self.c.get(reverse('timelines'))
        self.assertContains(resp, self.timeline.title)

    def test_published_timelines(self):
        """
        Test visibility of published timelines.
        """
        ts = Timeline.objects.visible_to_user()
        self.assertEquals(1, len(ts), "Anonymous user should see public published timelines.")
        self.timeline.published = False
        self.timeline.save()
        ts = Timeline.objects.visible_to_user()
        self.assertEquals(0, len(ts), "Anonymous user should not see unpublished timelines.")
        ts = Timeline.objects.visible_to_user(user=self.u)
        self.assertEquals(0, len(ts), "Authenticated user should not see unpublished timelines.")

    def test_private_timeline_anon(self):
        # test public timeline with anonymous
        Timeline.objects.get_visible_to_user_or_404(slug=self.timeline.slug)
        # set to private
        self.timeline.private = True
        self.timeline.save()
        with self.assertRaises(Http404):
            Timeline.objects.get_visible_to_user_or_404(slug=self.timeline.slug)

    def test_private_timeline_auth(self):
        self.timeline.private = True
        self.timeline.save()
        Timeline.objects.get_visible_to_user_or_404(self.u, slug=self.timeline.slug)

    def test_unpublished_timeline_anon(self):
        # set to unpublished
        self.timeline.published = False
        self.timeline.save()
        with self.assertRaises(Http404):
            Timeline.objects.get_visible_to_user_or_404(slug=self.timeline.slug)

    def test_unpublished_timeline_auth(self):
        # set to unpublished
        self.timeline.published = False
        self.timeline.save()
        with self.assertRaises(Http404):
            Timeline.objects.get_visible_to_user_or_404(self.u, slug=self.timeline.slug)

    def test_unpublished_timeline_anon_ui(self):
        # set to unpublished
        self.timeline.published = False
        self.timeline.save()
        resp = self.c.get(reverse('timeline', args=[self.timeline.slug]))
        self.assertEquals(404, resp.status_code)

    def test_unpublished_timeline_auth_ui(self):
        # set to unpublished
        self.timeline.published = False
        self.timeline.save()
        self.c.login(username='test', password='test')
        resp = self.c.get(reverse('timeline', args=[self.timeline.slug]))
        self.assertEquals(404, resp.status_code)

class TestTimelineImport(TestCase):
    def setUp(self):
        self.timeline = Timeline.objects.create(
                title='Test Timeline',
                slug='test-timeline',
        )

    def test_timeline_import(self):
        timeline_json = open(os.path.join(os.path.dirname(__file__), 'fixtures/pastor_john_timeline.json')).readline()
        timeline_json.strip()
        importer = TimelineImporter(timeline_json, self.timeline)
        errors = importer.import_items()
        self.assertEquals(30, self.timeline.timelineitem_set.count())
        self.assertEquals(0, len(errors))
