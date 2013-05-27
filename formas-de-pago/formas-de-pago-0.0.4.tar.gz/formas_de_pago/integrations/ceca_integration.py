from django.conf import settings
from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.http import HttpResponse

from billing import Integration, IntegrationNotConfigured
from billing.signals import transaction_was_successful, transaction_was_unsuccessful

from ..forms.ceca import CecaPaymentForm
from ..models.ceca import CecaResponse

csrf_exempt_m = method_decorator(csrf_exempt)
require_POST_m = method_decorator(require_POST)

URL_LIVE = "https://pgw.ceca.es/cgi-bin/tpv"
URL_TEST = "http://tpv.ceca.es:8000/cgi-bin/tpv"

class CecaIntegration(Integration):
    display_name = "Ceca"
    template = "billing/ceca.html"
    def __init__(self):
        super(CecaIntegration, self).__init__()
        merchant_settings = getattr(settings, "MERCHANT_SETTINGS")
        if not merchant_settings or not merchant_settings.get("ceca"):
            raise IntegrationNotConfigured("The '%s' integration is not correctly "
                                           "configured." % self.display_name)

        self.url_notification = merchant_settings['ceca']['url_notificacion']

    def form_class(self):
        return CecaPaymentForm

    def generate_form(self):
        return self.form_class()(initial=self.fields)

    def get_urls(self):
        urlpatterns = patterns('',
           url("^%s$" % self.url_notification, self.notify_handler, name="ceca_notify")
        )
        return urlpatterns

    @property
    def service_url(self):
        if self.test_mode:
            return URL_TEST
        return URL_LIVE


    @csrf_exempt_m
    @require_POST_m
    def notify_handler(self, request):
        post_data = request.POST.copy()
        data = {}

        resp_fields = {
            'MerchantID': 'merchant_id',
            'AcquirerBIN': 'acquirer_bin',
            'TerminalID': 'terminal_id',
            'Num_operacion': 'num_operacion',
            'Importe': 'importe',
            'TipoMoneda': 'tipo_moneda',
            'Referencia': 'referencia',
            'Firma': 'firma',
            'Num_aut': 'numero_autorizacion',
            'Idioma': 'idioma',
            'Pais': 'pais',
            'Descripcion': 'descripcion',
        }

        for (key, val) in resp_fields.iteritems():
            data[val] = post_data.get(key, '')

        try:
            resp = CecaResponse.objects.create(**data)
            # TODO: Make the type more generic
            transaction_was_successful.send(sender=self.__class__, type="purchase", response=resp)
            status = "$*$OKY$*$"
        except:
            transaction_was_unsuccessful.send(sender=self.__class__, type="purchase", response=post_data)
            status = "FAILURE"

        return HttpResponse(status)
