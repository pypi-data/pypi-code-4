from greplin import scales
import json
import pyramid.config
import pytest
import webtest


STATS = scales.collection(
    '/',
    scales.IntStat('errors')
)
STATS.errors += 1


@pytest.fixture
def app():
    config = pyramid.config.Configurator()
    config.include('pyramid_scales')
    return config.make_wsgi_app()


@pytest.fixture
def browser(app):
    return webtest.TestApp(app)


def test_displays_metrics_as_html(browser):
    r = browser.get('/scales/', status=200)
    assert (
        '<span class="key">errors</span> <span class="int">1</span>' in r.body)


def test_displays_metrics_as_json(browser):
    r = browser.get('/scales/?format=json', status=200)
    assert {'errors': 1} == json.loads(r.body)['']
