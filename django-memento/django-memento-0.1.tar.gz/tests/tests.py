# -*- coding: utf8 -*-
from random import randint
from django.test.utils import override_settings
from django.utils import unittest
import time
from memento.helpers import Logger
from memento.models import LogEntry, LogEvent
from models import Message


class TestLoginCodes(unittest.TestCase):
    def setUp(self):
        self.obj = Message()
        self.obj.save()
        self.simple_message = "this is a simple message"

    def test_log_simple_message(self):
        Logger.log(self.simple_message)

        self.assertEqual(len(LogEntry.objects.all()), 1)
        self.assertEqual(len(LogEvent.objects.all()), 1)

    def test_log_simple_message_multiple_times(self):
        Logger.log(self.simple_message)
        Logger.log(self.simple_message)
        Logger.log(self.simple_message)

        self.assertEqual(len(LogEntry.objects.all()), 1)
        self.assertEqual(len(LogEvent.objects.all()), 3)

    def test_log_object_message(self):
        message = "this is random test message %s" % randint(0, 100)
        Logger.log(message, self.obj)
        self.assertEqual(LogEntry.objects.all()[0].message, message)

    def test_get_log_object_message(self):
        message = "this is random test message %s" % randint(0, 100)
        Logger.log(message, self.obj)

        self.assertEqual(Logger.get_log_entry(self.obj)[0].message, message)

    def test_last_timestamp(self):
        Logger.log(self.simple_message)
        timestamp1 = LogEntry.objects.get(message=self.simple_message).last_timestamp
        time.sleep(1)
        Logger.log(self.simple_message)
        timestamp2 = LogEntry.objects.get(message=self.simple_message).last_timestamp
        self.assertGreater(timestamp2, timestamp1)

    @override_settings(MEMENTO_SEVERITY_DEFAULT=3)
    def test_severity_settings(self):
        Logger.log(self.simple_message)
        self.assertEqual(LogEntry.objects.get(message=self.simple_message).severity, 3)

    def tearDown(self):
        LogEntry.objects.all().delete()
        LogEvent.objects.all().delete()