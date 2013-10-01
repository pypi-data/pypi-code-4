# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required, permission_required
from rwiki.views import PageDetailView, PageAdd, PageUpdate, PageDel, revert

# Llamamos al registro a traves del formulario RegisterForm que hemos creado
urlpatterns = patterns('',
    url(r'^$',                              PageDetailView.as_view(), {'slug': 'start'}, 'app_wiki-detail'),
    url(r'^add/$',                          permission_required('rwiki.add_page')(PageAdd.as_view()), {}, 'app_wiki-add'),
    url(r'^revert/(?P<objid>\d+)/(?P<revid>\d+)/$', permission_required('rwiki.reverse')(revert), {}, name='app_wiki-revert'),
    url(r'^(?P<slug>[-\w/]+?)/del/$',      permission_required('rwiki.del_page')(PageDel.as_view()), {}, 'app_wiki-del'),
    url(r'^(?P<slug>[-\w/]+?)/edit/$',      permission_required('rwiki.change_page')(PageUpdate.as_view()), {}, 'app_wiki-edit'),
    url(r'^(?P<slug>[-\w/]+?)/$',           PageDetailView.as_view(), {}, 'app_wiki-detail'),
)
