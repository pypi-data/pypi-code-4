from django.conf.urls import url
from django.http import HttpResponse
from django_helpers import add_app_url

__author__ = 'ajumell'
import urls
from editable import XEditable

_URL_PREFIX = 'x-editable-'

_EDITABLES = dict()


def create_reg(name):
    return "(?P<%s>.*)/" % name


def get_editable(name, pk):
    if name not in _EDITABLES:
        return None

    return _EDITABLES[name](pk=pk)


def save(request, name):
    if request.method != 'POST':
        return HttpResponse()

    gt = request.POST.get
    pk = gt('pk')
    editable = get_editable(name, pk)
    if editable is None:
        return HttpResponse()
    field_name = gt('name')
    results = editable.save(request, field_name)
    return results


def list_data(request, name, field_name):
    gt = request.POST.get
    pk = gt('pk')
    editable = get_editable(name, pk)
    if editable is None:
        return HttpResponse()
    results = editable.list(field_name)
    return results


def register(editable):
    add_app_url('data-table', urls)

    if isinstance(editable, XEditable):
        raise Exception("XEditable class is required not instance.")

    if not issubclass(editable, XEditable):
        raise Exception("A Sub class of XEditable is required.")

    name = getattr(editable, 'editable_id', None)
    if name is None:
        raise Exception("Editable ID is needed.")

    if not name.startswith(_URL_PREFIX):
        name = _URL_PREFIX + name

    if name in _EDITABLES:
        old_editable = _EDITABLES[name]

        new_name = str(editable)
        old_name = str(old_editable)

        if old_name == new_name:
            return editable

        msg = "You tried to register a editable with id " + name + " for " + new_name + ".\n"
        msg += "But " + name + " is already registered for " + old_name + ".\n"
        msg += "Try giving a new ID for " + new_name
        raise Exception(msg)

    setattr(editable, 'editable_id', name)
    _EDITABLES[name] = editable

    list_reg = "%s/" % name
    list_reg += create_reg('field_name')
    list_reg += "list/$"

    save_reg = "%s/" % name
    save_reg += "save/$"

    save_pattern = url(r"%s" % save_reg, save, name=name + '_save', kwargs={
        "name": name
    })

    list_pattern = url(r"%s" % list_reg, list_data, name=name + '_list', kwargs={
        "name": name
    })

    urls.urlpatterns.append(save_pattern)
    urls.urlpatterns.append(list_pattern)
    return editable