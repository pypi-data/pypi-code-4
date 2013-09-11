from rest_framework_proxy.views import ProxyView
from vtixy_proxy import settings


class VTIXyProxyView(ProxyView):
    proxy_settings = settings.vtixy_uat_proxy_settings


class ShowsProxy(VTIXyProxyView):
    source = 'shows/'


class EventsProxy(VTIXyProxyView):
    source = 'events/'


class TicketSetProxy(VTIXyProxyView):
    source = 'ticket_set/%(pk)s/'


class PriceCategoriesProxy(VTIXyProxyView):
    source = 'categories/'


class PriceCategoriesDetailsProxy(VTIXyProxyView):
    source = 'categories/%(pk)s/'


class OrdersProxy(VTIXyProxyView):
    source = 'orders/'


class OrderDetailsProxy(VTIXyProxyView):
    source = 'orders/%(pk)s/'