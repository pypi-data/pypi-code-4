# coding=utf-8
from django.conf.urls import url
from django.http import HttpResponse

from django_helpers import add_app_url
import urls

from data_table import DataTable

_URL_PREFIX = 'data-table-'

_TABLES = dict()


def has_registered(name):
    return name in _TABLES


def get_table(name):
    if name not in _TABLES:
        return None

    return _TABLES[name]()


def get_data(request, name, **kwargs):
    table = get_table(name)
    if table is None:
        return HttpResponse()

    results = table.get_data(request, kwargs)
    return results


def save(request, name, **kwargs):
    if request.method != 'POST':
        return HttpResponse()

    table = get_table(name)
    if table is None:
        return HttpResponse()

    results = table.save(request, kwargs)
    return results


def create_reg(name):
    return "(?P<%s>.*)/" % name


def _table_name(table):
    return '%s.%s' % (table.__module__, table.__name__)


def register(data_table):
    add_app_url('data-table', urls)

    if isinstance(data_table, DataTable):
        raise Exception("DataTable class is required not instance.")

    if not issubclass(data_table, DataTable):
        raise Exception("A Sub class of DataTable is required.")

    name = getattr(data_table, 'table_id', None)
    if name is None:
        raise Exception("Table ID is needed.")

    if not name.startswith(_URL_PREFIX):
        name = _URL_PREFIX + name

    if name in _TABLES:
        old_table = _TABLES[name]

        new_name = _table_name(data_table)
        old_name = _table_name(old_table)

        if old_name == new_name:
            return data_table

        msg = "You tried to register a data table with id " + name + " for " + new_name + ".\n"
        msg += "But " + name + " is already registered for " + old_name + ".\n"
        msg += "Try giving a new ID for " + new_name
        raise Exception(msg)

    setattr(data_table, 'table_id', name)
    _TABLES[name] = data_table
    data_reg = "%s/" % name
    save_reg = "%s/" % name
    extra_url_parameters = data_table.url_search_parameters
    if extra_url_parameters is not None:
        for parameter in extra_url_parameters:
            data_reg += create_reg(parameter)
            save_reg += create_reg(parameter)
    data_reg += "$"
    save_reg += "save/$"

    data_pattern = url(r"%s" % data_reg, get_data, name=name, kwargs={
        "name": name
    })

    save_pattern = url(r"%s" % save_reg, save, name=name + '_save', kwargs={
        "name": name
    })

    urls.urlpatterns.append(data_pattern)
    urls.urlpatterns.append(save_pattern)
    return data_table