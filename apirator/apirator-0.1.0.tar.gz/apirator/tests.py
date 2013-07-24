# -*- coding:utf-8 -*-

import os

from django.test import TestCase
from django.conf.urls import patterns, url

from apirator import router, expose


@expose()
def foo():
    return {"bar": "some"}


@expose("some/spam", "POST", basestring)
def spam(eggs="eggs"):
    return {"eggs": eggs}


urlpatterns = patterns("", url(r"^testapi/(.+)$", router("apirator.tests")))


class ApiratorTests(TestCase):

    urls = "apirator.tests"

    def test_get(self):
        from .utils import decoders, encoders

        for ctype in encoders.keys():
            resp = self.client.get("/testapi/foo", HTTP_ACCEPT=ctype)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp["Content-Type"], ctype)
            self.assertEqual({"bar": "some"}, decoders[ctype](resp.content))

        for ctype in encoders.keys():
            eggs = os.urandom(10).encode("hex")
            resp = self.client.post("/testapi/some/spam",
                                    data=encoders[ctype]({"eggs": eggs}),
                                    content_type=ctype,
                                    HTTP_ACCEPT=ctype)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp["Content-Type"], ctype)
            self.assertEqual({"eggs": eggs}, decoders[ctype](resp.content))
