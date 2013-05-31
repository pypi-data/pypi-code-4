from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from rsbp.models import TextPost


def _valid_test_user(**kwargs):
    defaults = {
        'username': 'test',
        'password': 'test',
        'email': 'test@example.com'
    }
    defaults.update(kwargs)

    return get_user_model().objects.create(**defaults)


def _valid_text_post(**kwargs):
    defaults = {
        'title': 'A Test Post',
        'slug': 'a-test-post',
        'published': True,
        'text': 'Some test content',
    }

    if not 'created_by' in kwargs.keys():
        defaults.update({'created_by': _valid_test_user()})

    defaults.update(kwargs)

    return TextPost.objects.create(
        **defaults
    )


class PublishedTest(TestCase):

    def test_unpublished(self):
        text_post = _valid_text_post(published=False)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['object_list'].count(), 0)

    def test_unpublished_logged_in(self):
        text_post = _valid_text_post(published=False)
        superuser = _valid_test_user(
            username='super',
            email='super@example.com',
            is_superuser=True,
            is_staff=True,
        )
        self.client.login(username='super', password='password')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['object_list'].count(), 0)

    def test_published(self):
        text_post = _valid_text_post(published=True)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['object_list'].count(), 1)


class SlugsTest(TestCase):

    def test_slug(self):
        titled_post = _valid_text_post()

        response = self.client.get(reverse('post', args=(titled_post.id, 'a-test-post')))
        self.assertTrue(response.status_code, 200)

    def test_incomplete_slug(self):
        titled_post = _valid_text_post()

        incomplete_url = reverse('index') + '{0}/a-test-po'.format(titled_post.id)
        response = self.client.get(incomplete_url, follow=True)
        final_url = response.redirect_chain[-1][0]
        self.assertTrue(final_url.endswith('/a-test-post/'))

    def test_no_slug(self):
        untitled_post = _valid_text_post(title='', slug='')

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(untitled_post.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_title_no_slug(self):
        unslugged_post = _valid_text_post(slug='')

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(unslugged_post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
