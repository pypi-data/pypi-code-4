"""
.. module:: __init__
   :synopsis: Registry

.. moduleauthor:: Artur Barseghyan <artur.barseghyan@gmail.com>
"""
import imp

from sirep.base import Report

# Sirep registry for the reports.
_registry = {}

def register(slug, cls):
    """
    Registers the report in the global sirep registry.

    :param str slug: Report slug.
    :param sirep.base.Report cls: Report class being registered.
    """
    _registry[slug] = cls

def get_report(slug):
    """
    Gets report from sirep global registry.

    :param str slug: Slug of the report.
    """
    try:
        return _registry[slug]
    except KeyError:
        raise Exception("No such report '%s'" % slug)

def all_reports():
    """
    Gets all reports registered in sirep registry.

    :return dict:
    """
    return _registry.items()

def autodiscover():
    """
    Autodiscovers the reports in project apps. Each report file which should be found by sirep, should be
    named "reports.py".
    """
    from django.conf import settings
    REPORTING_SOURCE_FILE =  getattr(settings, 'REPORTING_SOURCE_FILE', 'reports')
    for app in settings.INSTALLED_APPS:
        try:
            app_path = __import__(app, {}, {}, [app.split('.')[-1]]).__path__
        except AttributeError:
            continue

        try:
            imp.find_module(REPORTING_SOURCE_FILE, app_path)
        except ImportError:
            continue
        __import__('%s.%s' % (app, REPORTING_SOURCE_FILE))
