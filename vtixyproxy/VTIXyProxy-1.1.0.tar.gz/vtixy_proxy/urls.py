from django.conf import settings
from django.conf.urls import patterns, url
from django.views.decorators.cache import cache_page
from vtixy_proxy import views

urlpatterns = patterns('',
                       url(r'^shows/', cache_page(views.ShowsProxy.as_view(http_method_names=['get']),
                                                  settings.VTIXY_CACHE_TIMEOUT)),
                       url(r'^events/', cache_page(views.EventsProxy.as_view(http_method_names=['get']),
                                                   settings.VTIXY_CACHE_TIMEOUT)),
                       url(r'^ticket_set/(?P<pk>[0-9]+)/$', views.TicketSetProxy.as_view(http_method_names=['get'])),
                       url(r'^categories/$', views.PriceCategoriesProxy.as_view(http_method_names=['get'])),
                       url(r'^categories/(?P<pk>[0-9]+)/$',
                           views.PriceCategoriesDetailsProxy.as_view(http_method_names=['get'])),
                       url(r'^orders/$', views.OrdersProxy.as_view(http_method_names=['post'])),
                       url(r'^orders/(?P<pk>[0-9]+)/$', views.OrderDetailsProxy.as_view(http_method_names=['get'])),
                       )
