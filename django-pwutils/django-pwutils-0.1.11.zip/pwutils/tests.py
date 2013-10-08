# -*- coding: utf-8 -*-
from __future__ import with_statement

import os
from decimal import Decimal
from os.path import join, normpath

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import filepath_to_uri

from django.conf import settings
from django.db import models
from django.test import TestCase
from django.test.client import RequestFactory

from pwutils.models import TimeStampedModel, TimeStampedByUserModel
from pwutils.fields import CustomGenericForeingKey
from pwutils.forms import create_choices
from pwutils.middleware.threadlocals import get_current_user, ThreadLocals
from pwutils.middleware.exceptionuserinfo import ExceptionUserInfoMiddleware
from pwutils.middleware.requesttimelogging import RequestTimeLoggingMiddleware
from pwutils.utils import create_generic_filter, EmptyContext


class TestModel(models.Model):

    title = models.CharField(max_length=20)


class TestTimeStampedModel(TimeStampedModel):

    class Meta:
        pass


class TestTimeStampedByUserModel(TimeStampedByUserModel):

    title = models.CharField(max_length=20)

    class Meta:
        pass


class TestGenericFK(models.Model):

    content_type = models.ForeignKey(ContentType,
                             related_name="content_type_set_for_%(class)s",
                             limit_choices_to={'model__in': ['testmodel']})

    object_pk = models.PositiveIntegerField()

    content_object = CustomGenericForeingKey(ct_field="content_type",
                                             fk_field="object_pk")

    @property
    def ct_exception_model(self):
        return TestModel


class AdminTest(TestCase):

    def test_admin(self):
        from pwutils import admin


class UtilsTest(TestCase):

    def setUp(self):
        user = User.objects.create(username=1)
        user.save()
        self.user = user
        comment = TestGenericFK(content_object=user)
        comment.save()
        comment.content_object = user
        self.comment = comment

    def tearDown(self):
        self.comment.delete()
        self.user.delete()

    def test_create_generic_filter(self):

        filters = create_generic_filter(self.user,
                                        obj_id_field_name='object_pk')
        comment = TestGenericFK.objects.get(**filters)
        self.assertEquals(comment.content_object.id, self.user.id)

    def test_custom_generic_fk_content_type(self):

        obj = self.comment._meta.virtual_fields[0]
        self.assertEquals(obj.get_content_type(self.comment),
                          ContentType.objects.get_for_model(TestModel))
        self.assertEquals(obj.get_content_type(self.user),
                          ContentType.objects.get_for_model(User))

        user_type = ContentType.objects.get_for_model(User)
        self.assertEquals(obj.get_content_type(id=user_type.id),
                          user_type)

    def test_empty_context(self):
        context = EmptyContext()
        with context():
            pass

    def test_check_float(self):
        from pwutils.utils import check_float
        self.failUnlessEqual(check_float(5), True)
        self.failUnlessEqual(check_float(5.), True)
        self.failUnlessEqual(check_float('5'), True)
        self.failUnlessEqual(check_float('5,2'), True)
        self.failUnlessEqual(check_float(Decimal(5)), True)
        self.failUnlessEqual(check_float('aaa'), False)
        self.failUnlessEqual(check_float(object()), False)


class TimeStampedModelByUserTest(TestCase):

    def setUp(self):

        user = User.objects.create(username='test', password='pass')

        m = ThreadLocals()
        rf = RequestFactory()
        request = rf.get('/')
        request.user = user
        m.process_request(request)

        user2 = User.objects.create(username='test2', password='pass2')

        self.user1 = user
        self.user2 = user2
        self.request = request

    def teardown(self):

        self.user1.delete()
        self.user2.delete()
        m = ThreadLocals()
        rf = RequestFactory()
        request = rf.get('/')
        request.user = None
        m.process_request(request)

    def test_timestampedbyuser_model(self):

        t = TestTimeStampedByUserModel(title=u'Test_obj')
        t.save()

        self.assertEquals(t.created_by, self.user1)
        self.assertEquals(t.modified_by, self.user1)

        t.deleted = True
        self.assertEquals(t.deleted_by, self.user1)

        t.deleted = False
        self.assertEquals(t.deleted_by, None)

        m = ThreadLocals()
        self.request.user = self.user2
        m.process_request(self.request)

        t.title = u'Test'
        t.save()
        self.assertEquals(t.created_by, self.user1)
        self.assertEquals(t.modified_by, self.user2)

    def test_timestamped_model(self):

        t = TestTimeStampedModel()
        t.save()

        f = t._meta.get_field_by_name('deleted_date')[0]
        self.assertEquals(f.get_internal_type(), "DateTimeField")
        self.assertEquals(t.deleted, False)

        t.deleted = True
        self.assertEquals(t.deleted, True)

        t.deleted = False
        self.assertEquals(t.deleted, False)
        self.assertEquals(t.deleted_date, None)


class FormsTest(TestCase):

    def setUp(self):

        self.o1 = TestModel(title=u'Test1')
        self.o2 = TestModel(title=u'Test2')

        self.o1.save()
        self.o2.save()

    def tearDown(self):

        self.o1.delete()
        self.o2.delete()

    def test_create_choices(self):

        choices = create_choices(TestModel)
        right_value = [(1, self.o1), (2, self.o2)]
        self.assertEquals(choices, right_value)

        choices = create_choices(TestModel,
                                 TestModel.objects.filter(title=u'Test2'))
        right_value = [(2, self.o2)]
        self.assertEquals(choices, right_value)

        choices = create_choices(TestModel, empty=True)
        right_value = [('', u'------------'),
                       (1, self.o1),
                       (2, self.o2)]
        self.assertEquals(choices, right_value)

        choices = create_choices(TestModel, empty=True, order_by=('-title'))
        right_value = [('', u'------------'), (2, self.o2), (1, self.o1)]
        self.assertEquals(choices, right_value)


class MiddlwareTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test', password='pass')

    def tearDown(self):
        self.user.delete()

    def test_current_user(self):

        m = ThreadLocals()
        rf = RequestFactory()
        request = rf.get('/')
        request.user = None
        m.process_request(request)

        self.assertEquals(get_current_user(), None)

        m = ThreadLocals()
        rf = RequestFactory()
        request = rf.get('/')
        request.user = self.user
        m.process_request(request)

        self.assertEquals(get_current_user(), self.user)

    def test_timelogging(self):
        rf = RequestFactory()
        request = rf.get('/')
        request.user = self.user
        m = RequestTimeLoggingMiddleware()
        m.process_request(request)
        m.process_response(request, None)

    def test_exception(self):
        rf = RequestFactory()
        request = rf.get('/')
        request.user = self.user
        m = ExceptionUserInfoMiddleware()
        m.process_exception(request, Exception())

        self.assertTrue('USERNAME' in request.META)
        self.assertEquals(request.META['USERNAME'], 'test')


class StoragesTest(TestCase):
    def setUp(self):
        from pwutils.storage import BalancedFileSystemStorage
        self.storage = BalancedFileSystemStorage(base_url='/')

    def test_prefix(self):
        self.assertEquals(self.storage.prefix('abc'), ('a', 'b'))
        self.assertEquals(self.storage.prefix('UP'), ('U', 'P'))
        self.assertEquals(self.storage.prefix(']]'), ('a', 'a'))
        self.assertEquals(self.storage.prefix('??abc'), ('a', 'a'))
        self.assertEquals(self.storage.prefix(u'Русский'), ('R', 'u'))
        self.assertEquals(self.storage.prefix('1'), ('1', '1'))
        self.assertEquals(self.storage.prefix('5'), ('5', '5'))
        self.assertEquals(self.storage.prefix(u'№№'), ('#', '#'))
        self.assertEquals(self.storage.prefix(u'??'), ('a', 'a'))

    def test_path_and_url(self):
        self.assertEquals(self.storage.rel_path('images/abc.rar'),
                          os.path.join('images', 'a', 'b', 'abc.rar'))

        self.assertEquals(self.storage.path('images/abc.rar'),
                          normpath(join(settings.MEDIA_ROOT,
                                       'images', 'a', 'b', 'abc.rar')))

        self.assertEquals(self.storage.path('images/people/abc.rar'),
                          normpath(join(settings.MEDIA_ROOT,
                                        'images', 'people',
                                        'a', 'b', 'abc.rar')))

        self.assertEquals(self.storage.url('images/abc.rar'),
                          '/images/a/b/abc.rar')
        self.assertEquals(self.storage.url(u'архив.rar'),
                          '/a/r/' + filepath_to_uri(u'архив.rar'))


class TemplateTagsTest(TestCase):

    def test_flatten(self):
        from pwutils.templatetags.pwfilters import flatten
        self.assertEqual(flatten('aaa'), 'aaa')
        self.assertEqual(flatten(' aaa\n\n\n a'), 'aaa a')

    def test_external_url(self):
        from pwutils.templatetags.external_url import external_url

        self.assertEqual(external_url('http://e1.ru'), 'http://e1.ru')
        self.assertEqual(external_url('admin:index'),
                             'http://example.com/admin/')

        self.assertEqual(external_url('customer'),
                             'http://example.com/customer')

    def test_pwfilters(self):
        from pwutils.templatetags.pwfilters import (in_list,
                                                    not_none,
                                                    split,
                                                    split_str,
                                                    startswith,
                                                    hash)


        self.assertEqual(in_list('1', ['1','2']), True)
        self.assertEqual(in_list('3', ['1','2']), False)

        self.assertEqual(not_none(None), '')
        self.assertEqual(not_none('aaa'), 'aaa')

        self.assertEqual(startswith('aaabbb', 'aaa'), True)
        self.assertEqual(startswith('bbbaaa', 'aaa'), False)

        self.assertEqual(split('aaabbbccc', 'bbb'), 'ccc')

        self.assertEqual(split_str('aaabbbccc', 'bbb'), ['aaa', 'ccc'])

        self.assertEqual(hash({1:2}, 1), 2)

    def test_media(self):
        from pwutils.templatetags.media import media, static

        self.assertEqual(media('aaa'), '%saaa' % settings.MEDIA_URL)

        self.assertEqual(static('aaa'), '/static/aaa')

    def test_lightbox(self):
        from pwutils.templatetags.lightbox import lightbox
        lightbox('test.png', 'thumb.png')

    def test_navigation_path(self):
        from pwutils.templatetags.navigation_path import navigation_path

        context = {}

        self.assertEqual(navigation_path(context), {'parts': []})

        context['nav_path'] = ['aaa', 'bbb']
        self.assertEqual(navigation_path(context)['parts'][0], 'aaa')


class SearchTest(TestCase):
    def test_search_base(self):
        from pwutils.search.base import BaseSearchEngine

    #def test_yandex_search(self):
    #    pass

    #def test_sphinx_search(self):
    #    pass


class EmailTest(TestCase):

    def test_attachments(self):
        from pwutils.email import EmailMultiRelated

        email = EmailMultiRelated(subject='test',
                                  body='Hi',
                                  from_email='vsafronovich@gmail.com',
                                  to=['vsafronovich@gmail.com'])
        html = '<h1>Hi</h1>'
        email.alternatives = [(html, 'text/html')]
        email.attach_related_file(path=__file__, id='image_id')
        #msg.send(fail_silently=True)
