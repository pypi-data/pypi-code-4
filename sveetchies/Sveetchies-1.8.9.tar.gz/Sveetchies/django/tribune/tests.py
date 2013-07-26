"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.

from django.db import connection
from django.contrib.auth.models import User
from Sveetchies.django.tribune.models import Message, FilterEntry

def displaysql(items):
    for i, row in enumerate(items, 1):
        print "{0})".format(i), "Time: {0}s".format(row['time']), "SQL:", row['sql']

def getmax_identity(accumulated, current):
    if current['author'] and len(current['author__username'])>accumulated:
        return len(current['author__username'])
    elif len(current['user_agent'])>accumulated:
        return len(current['user_agent'])
    return accumulated

root = User.objects.get(username='root')
superman = User.objects.get(username='superman')

Message.objects.count()
Message.objects.orderize().flat()[:10]
Message.objects.orderize(38).flat()[:10]

root.filterentry_set.get_filters_args()
Message.objects.bunkerize(root).orderize().count()
Message.objects.bunkerize(root).orderize().flat()[:10]

superman.filterentry_set.get_filters_args()
Message.objects.bunkerize(superman).orderize().count()
Message.objects.bunkerize(superman).orderize().flat()[:10]

fields = ('id', 'created', 'clock', 'author_id', 'author__username', 'user_agent', 'ip', 'raw', 'web_render', 'remote_render')
stuff = Message.objects.bunkerize(superman).orderize().values(*fields)[:10]

#displaysql(connection.queries)
"""
from django.test import TestCase

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
