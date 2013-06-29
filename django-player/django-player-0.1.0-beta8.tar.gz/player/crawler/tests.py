# -*- coding: utf-8 -*-
"""
Crawler tests. This test only the scraping tool and extracted data.
"""
import time
import socket
import SocketServer
import threading
import simplejson as json
from datetime import date
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from lxml.etree import XMLSyntaxError

# from django.conf import settings
from django.test import TestCase
from django.contrib.sites.models import Site
from django.utils.datastructures import SortedDict
from django.utils.html import strip_tags

from player.crawler import get_backend
from player.crawler.models import CrawlerCollection
from player.crawler.exceptions import CrawlerHttpException
from player.data.models import Collection, CollectionField, Item
from testwebsite.models import NewsItem

TEST_BACKEND = 'player.crawler.backends.mozenda'

MAPPED_FIELDS = SortedDict({
    'content-title': {
        'name': 'Content title',
        'type': 'text',
        'mapped_field': 'name',
        'is_matchup': True,
    },
    'content-description': {
        'name': 'Content description',
        'type': 'html',
        'mapped_field': 'short description',
        'is_matchup': False,
    },
    'content-body': {
        'name': 'Content body',
        'type': 'html',
        'mapped_field': 'long description',
        'is_matchup': False,
    },
})

# Note: previous mapping only works with a Collection defined as follows:
# Fields:
#  - "link": a link to the content.
#  - "short description": content description.
#  - "long description": content body.
#  - "name": the content title

RESPONSE_COLLECTION_GET_FIELDS = """
"""

RESPONSE_COLLECTION_GET_VIEWS = """
"""

RESPONSE_VIEW_GET_ITEMS = """
"""

RESPONSE_AGENT_GET_JOBS = """
"""


class FakeServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = 1    # Seems to make sense in testing environment

    def server_bind(self):
        """Override server_bind to store the server name."""
        SocketServer.TCPServer.server_bind(self)
        host, port = self.socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port


class FakeHandler(BaseHTTPRequestHandler):

    def get_datas(self, path, band):
        if band == 0:
            if 'Collection.GetViews' in path:
                datas = RESPONSE_COLLECTION_GET_VIEWS
            elif 'View.GetItems' in path:
                datas = RESPONSE_VIEW_GET_ITEMS
            elif 'Collection.GetFields' in path:
                datas = RESPONSE_COLLECTION_GET_FIELDS
            elif 'Agent.GetJobs' in path:
                datas = RESPONSE_AGENT_GET_JOBS
        else:
            datas = ''
        return datas

    def do_GET(self):
        if self.server.band <= 1:
            self.send_response(200)
        elif self.server.band == 2:
            self.send_response(500)
        elif self.server.band == 3:
            self.send_response(400)
        datas = self.get_datas(self.path, self.server.band)
        self.send_header('Content-type', 'text/xml; charset=utf-8')
        self.server.requests_processed.append(
            {'method': 'GET', 'path': self.path, 'data': datas})
        self.end_headers()
        self.wfile.write(datas)


class MyThread(threading.Thread):

    def __init__(self, band, number_of_requests=1, port=8000):
        super(MyThread, self).__init__()
        self.number_of_requests = number_of_requests
        self.requests_processed = []
        self.band = band
        self.port = port

    def run(self):
        fake_server = HTTPServer(('', self.port), FakeHandler)
        fake_server.requests_processed = []
        fake_server.band = self.band
        while self.number_of_requests > 0:
            fake_server.handle_request()
            self.number_of_requests -= 1
            self.requests_processed = fake_server.requests_processed
            self.band = fake_server.band
        fake_server.socket.close()


class CrawlerTest(TestCase):

    def setUp(self):
        self.backend = get_backend(TEST_BACKEND)
        self.site = Site.objects.get_current()
        self.crawler_collection = self.backend.create_test_crawler_collection()
        # uncomment next line if you want to run extraction jobs in test time (very very slow)
        #self.backend.run_test_extraction_process()
        self.collection = Collection.objects.create(
            name='test collection',
            crawler_collection=self.crawler_collection,
        )
        for field_slug, mapping in MAPPED_FIELDS.items():
            CollectionField.objects.create(
                name=mapping['name'],
                slug=field_slug,
                field_type=mapping['type'],
                mapped_field=mapping['mapped_field'],
                is_matchup=mapping['is_matchup'],
                collection=self.collection,
            )
        self.backend.extract_collection_data(self.crawler_collection)

    def test_crawled_data_schema(self):
        """
        Tests crawled data schema is correct
        """
        crawled_items = self.collection.item_set.all()
        for item in crawled_items:
            for field_name, value in item.content.items():
                # field_name must be in MAPPED_FIELDS keys (field slugs)
                self.failIf(field_name not in MAPPED_FIELDS)
                # do type checking
                mapping_type = MAPPED_FIELDS[field_name]['type']
                field_value = item.get_value(field_name)
                if mapping_type in ('text', 'html', 'url'):
                    self.failUnless(isinstance(field_value, unicode))
                elif mapping_type == 'date':
                    self.failUnless(isinstance(field_value, date))
                elif mapping_type == 'int':
                    self.failUnless(isinstance(field_value, int))

    def test_crawled_data(self):
        """
        Tests crawled data is correct
        """
        crawled_items = self.collection.item_set.all()
        collection_items = self.collection.item_set.values()
        newsitem_list = NewsItem.objects.all()

        for item_extract in crawled_items:
            for it in collection_items:
                if it['id'] == item_extract.id:
                    item_database = json.loads(it['content'])
            for it in newsitem_list:
                if it.title == item_extract.content['content-title']:
                    item_newitem = it

            for field_name, value in item_extract.content.items():
                self.failIf(field_name not in MAPPED_FIELDS)
                field_value = item_extract.get_value(field_name)
                self.assertEquals(field_value, item_database[field_name])
                if 'body' in field_name:
                    self.assertEquals(strip_tags(item_newitem.body),
                                      strip_tags(field_value))
                elif 'title' in field_name:
                    self.assertEquals(strip_tags(item_newitem.title),
                                      strip_tags(field_value))
                elif 'description' in field_name:
                    self.assertEquals(strip_tags(item_newitem.description),
                                      strip_tags(field_value))


def run_server(band, num_request):
        time.sleep(1)
        server = MyThread(band, num_request, 8000)
        server.start()
        time.sleep(2)

        return server


class ExtractDataTest(TestCase):

    def _fixture_setup(self):
        # we need to run the harvester server here because
        # the fixtures creates objects and the post-save
        # signals tries to connec to the harvester
        server = run_server(0, 4)
        super(ExtractDataTest, self)._fixture_setup()
        server.number_of_requests = 0
        server.join()

    def setUp(self):
        self.assertEquals(Item.objects.count(), 0)
        self.backend = get_backend(TEST_BACKEND)
        # self.site = Site.objects.get_current()
        self.crawler_collection = CrawlerCollection.objects.get_or_create(collection_code='1014')[0]

        # server = run_server(0, 1)
        # self.crawler_collection = self.backend.create_test_crawler_collection()
        # uncomment next line if you want to run extraction jobs in test time (very very slow)
        #self.backend.run_test_extraction_process()
        self.collection = Collection.objects.get_or_create(crawler_collection=self.crawler_collection)[0]
        # server.number_of_requests = 0
        # server.join()

    def test_extract_data_ok(self):
        server = run_server(0, 3)
        self.backend.extract_collection_data(self.crawler_collection)
        server.number_of_requests = 0
        server.join()
        # comprobar todos los items creados
        self.assertEqual(len(Item.objects.all()), 2)

    def test_extract_data_without_xml(self):
        server = run_server(1, 1)
        self.assertRaises(XMLSyntaxError,
                          self.backend.extract_collection_data,
                          (self.crawler_collection))
        # recibe una respuesta 200 con content-type: text/xml pero sin datos.
        server.number_of_requests = 0
        server.join()
        self.assertEqual(len(Item.objects.all()), 0)

    def test_extract_data_server_error(self):
        server = run_server(2, 1)
        self.assertRaises(CrawlerHttpException,
                          self.backend.extract_collection_data,
                          (self.crawler_collection))
        # server error (500)
        server.number_of_requests = 0
        server.join()

    def test_extract_data_client_error(self):
        server = run_server(3, 1)
        self.assertRaises(CrawlerHttpException,
                          self.backend.extract_collection_data,
                          (self.crawler_collection))
        # server error (400)
        server.number_of_requests = 0
        server.join()
