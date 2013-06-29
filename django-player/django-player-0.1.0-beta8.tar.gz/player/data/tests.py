# -*- coding: utf-8 -*-

import time
import socket
import SocketServer
import threading
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from django.db import IntegrityError
from django.test import TestCase

from player.data.models import Collection, Item
from player.crawler import get_backend
from player.crawler.models import CrawlerCollection

TEST_BACKEND = 'player.crawler.backends.mozenda'


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
        # TODO: to implement
        return

    def do_GET(self):
        self.send_response(200)
        datas = self.get_datas(self.path, self.server.band)
        self.send_header('Content-type', 'text/xml; charset=utf-8')
        self.server.requests_processed.append(
            {'method': 'GET', 'path': self.path, 'data': datas})
        self.end_headers()
        self.wfile.write(datas)

    def do_POST(self):
        content_length = self.headers.getheader('content-length')
        self.rfile.read(int(content_length))

        self.send_response(200)
        self.end_headers()
        self.wfile.write('')


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


# ./manage.py test data.DuplicateItemsTests --settings=settings_test
class DuplicateItemsTests(TestCase):

    def _fixture_setup(self):
        # we need to run the harvester server here because
        # the fixtures creates objects and the post-save
        # signals tries to connec to the harvester
        self.run_server(0, 4)
        super(DuplicateItemsTests, self)._fixture_setup()
        self.server.number_of_requests = 0
        self.server.join()

    def run_server(self, band, num_request):
        time.sleep(1)
        self.server = MyThread(band, num_request, 8000)
        self.server.start()
        time.sleep(2)

    def setUp(self):
        self.crawler_collection = CrawlerCollection.objects.get_or_create(collection_code='1014')[0]

        self.assertEquals(Item.objects.count(), 0)

        self.crawler_collection.check_deleted = True
        self.crawler_collection.new_elements_threshold = '0'
        self.crawler_collection.modified_elements_threshold = '0'
        self.crawler_collection.deleted_elements_threshold = '0'

        self.run_server(0, 3)
        get_backend(TEST_BACKEND).extract_collection_data(self.crawler_collection)
        self.number_of_requests = 0
        self.server.join()

    def test_add_item_fail(self):
        print '\ntest_add_item_fail'
        self.run_server(1, 6)
        get_backend(TEST_BACKEND).extract_collection_data(self.crawler_collection)
        get_backend(TEST_BACKEND).extract_collection_data(self.crawler_collection)
        self.server.number_of_requests = 0
        self.server.join()

        self.assertEquals(Item.objects.count(), 3)
        self.assertEquals(len(Item.objects.all()), 2)
        self.assertEquals(len(Item.objects.invalids()), 1)

        # Validamos el elemento:
        item_no_valid = Item.objects.invalids()[0]
        item_no_valid.is_valid = True
        item_no_valid.save()

        self.assertEquals(Item.objects.count(), 3)
        self.assertEquals(len(Item.objects.all()), 3)
        self.assertEquals(len(Item.objects.invalids()), 0)

        self.run_server(1, 3)
        get_backend(TEST_BACKEND).extract_collection_data(self.crawler_collection)
        self.server.number_of_requests = 0
        self.server.join()

        self.assertEquals(Item.objects.count(), 3)
        self.assertEquals(len(Item.objects.all()), 3)
        self.assertEquals(len(Item.objects.invalids()), 0)

    def test_modify_item_fail(self):
        print '\ntest_modify_item_fail'

        self.run_server(2, 6)
        get_backend(TEST_BACKEND).extract_collection_data(self.crawler_collection)
        get_backend(TEST_BACKEND).extract_collection_data(self.crawler_collection)
        self.server.number_of_requests = 0
        self.server.join()

        self.assertEquals(Item.objects.count(), 3)
        self.assertEquals(len(Item.objects.all()), 2)
        self.assertEquals(len(Item.objects.invalids()), 1)

        # validamos el elemento
        item_no_valid = Item.objects.invalids()[0]
        if len(Item.objects.filter(uid=item_no_valid.uid,
                                   collection=item_no_valid.collection,
                                   is_valid=True, is_deleted=False)):
            Item.objects.get(uid=item_no_valid.uid,
                             collection=item_no_valid.collection,
                             is_valid=True, is_deleted=False).delete()
        item_no_valid.is_valid = True
        item_no_valid.save()

        self.assertEquals(Item.objects.count(), 2)
        self.assertEquals(len(Item.objects.all()), 2)
        self.assertEquals(len(Item.objects.invalids()), 0)

        self.run_server(2, 3)
        get_backend(TEST_BACKEND).extract_collection_data(self.crawler_collection)
        self.server.number_of_requests = 0
        self.server.join()

        self.assertEquals(Item.objects.count(), 2)
        self.assertEquals(len(Item.objects.all()), 2)
        self.assertEquals(len(Item.objects.invalids()), 0)

    def test_remove_item_fail(self):
        print '\ntest_remove_item_fail'
        self.run_server(3, 6)
        get_backend(TEST_BACKEND).extract_collection_data(self.crawler_collection)
        get_backend(TEST_BACKEND).extract_collection_data(self.crawler_collection)
        self.server.number_of_requests = 0
        self.server.join()

        self.assertEquals(Item.objects.count(), 3)
        self.assertEquals(len(Item.objects.all()), 2)
        self.assertEquals(len(Item.objects.invalids()), 1)

        # validamos el elemento
        item_no_valid = Item.objects.invalids()[0]
        if not item_no_valid.content:
            Item.objects.get(uid=item_no_valid.uid,
                             collection=item_no_valid.collection,
                             is_valid=True, is_deleted=False).delete()
            item_no_valid.delete()

        self.assertTrue(item_no_valid.is_deleted)

        self.assertEquals(Item.objects.count(), 1)
        self.assertEquals(len(Item.objects.all()), 1)
        self.assertEquals(len(Item.objects.invalids()), 0)

        self.run_server(3, 3)
        get_backend(TEST_BACKEND).extract_collection_data(self.crawler_collection)
        self.server.number_of_requests = 0
        self.server.join()

        self.assertEquals(Item.objects.count(), 1)
        self.assertEquals(len(Item.objects.all()), 1)
        self.assertEquals(len(Item.objects.invalids()), 0)
        self.assertTrue(item_no_valid.is_deleted)


# ./manage.py test data.IntegrityTests
class IntegrityTests(TestCase):

    def test_integrity_item(self):
        """
        Test items integrity, defined in unique_together Meta option for Item model...
        """
        collection = Collection.objects.create(name="foo-collection")
        Item.objects.create(collection=collection, uid="foo", is_valid=True, is_deleted=True)
        Item.objects.create(collection=collection, uid="foo", is_valid=True, is_deleted=False)
        try:
            Item.objects.create(collection=collection, uid="foo", is_valid=True, is_deleted=False)
        except Exception, e:
            if isinstance(e, IntegrityError):
                print "Pass"
            else:
                print "Fail with %s" % type(e)
