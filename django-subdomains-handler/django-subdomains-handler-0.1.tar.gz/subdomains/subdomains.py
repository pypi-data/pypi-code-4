from django.conf import settings


class SubDomainMiddleware(object):
    def process_request(self, request):
        """
        Override default URLConf if subdomain match settings
        """
        if [subsomain for subsomain in request.META['HTTP_HOST'].split('.')][0]\
                in settings.SUBDOMAINS_URLCONF:
            request.urlconf = settings.SUBDOMAINS_URLCONF[subsomain]
