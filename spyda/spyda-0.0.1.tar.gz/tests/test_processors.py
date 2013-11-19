#!/usr/bin/env python

import pytest
pytest.importorskip("calais")

from os import path

import calais.calais
from spyda.processors import process_calais


@pytest.fixture()
def sample_response(request):
    return open(path.join(path.dirname(__file__), "sample.json"), "r").read()


def test_process_calais(monkeypatch, sample_response):
    def rest_POST(self, content):
        return sample_response
    monkeypatch.setattr(calais.calais.Calais, "rest_POST", rest_POST)

    result = process_calais("blah", key="foobar")
    assert result == {"people": [u"Jamil Alayan"]}
