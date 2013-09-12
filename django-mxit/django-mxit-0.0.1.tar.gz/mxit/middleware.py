from HTMLParser import HTMLParser

from django.contrib.auth import middleware


class RemoteUserMiddleware(middleware.RemoteUserMiddleware):
    header = 'HTTP_X_MXIT_USERID_R'

    # Thanks Vumi Mxit transport
    def noop(self, key):
        return key

    def parse_location(self, location):
        return dict(zip([
            'country_code',
            'country_name',
            'subdivision_code',
            'subdivision_name',
            'city_code',
            'city',
            'network_operator_id',
            'client_features_bitset',
            'cell_id'
        ], location.split(',')))

    def parse_profile(self, profile):
        return dict(zip([
            'language_code',
            'country_code',
            'date_of_birth',
            'gender',
            'tariff_plan',
        ], profile.split(',')))

    def html_decode(self, html):
        """
        Turns '&lt;b&gt;foo&lt;/b&gt;' into u'<b>foo</b>'
        """
        return HTMLParser().unescape(html)

    def get_request_data(self, request):
        header_ops = [
            ('HTTP_X_DEVICE_USER_AGENT', self.noop),
            ('HTTP_X_MXIT_CONTACT', self.noop),
            ('HTTP_X_MXIT_USERID_R', self.noop),
            ('HTTP_X_MXIT_NICK', self.noop),
            ('HTTP_X_MXIT_LOCATION', self.parse_location),
            ('HTTP_X_MXIT_PROFILE', self.parse_profile),
            ('HTTP_X_MXIT_USER_INPUT', self.html_decode),
        ]
        data = {}
        for header, proc in header_ops:
            value = request.META.get(header, None)
            if value is not None:
                data[header.split('HTTP_X_', 1)[-1]] = proc(value)
        return data

    def process_request(self, request):
        resp = super(RemoteUserMiddleware, self).process_request(request)
        if resp:
            return resp

        request.mxit = self.get_request_data(request)
