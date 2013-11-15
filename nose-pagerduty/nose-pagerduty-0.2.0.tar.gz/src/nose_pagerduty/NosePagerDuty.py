import logging
import requests
import json
from nose.plugins import Plugin
from nose.plugins.attrib import get_method_attr
from types import ModuleType

log = logging.getLogger('nose.plugins.pagerduty')


def trigger_pagerduty(description, service_key):
    pagerduty_url = "https://events.pagerduty.com/generic/2010-04-15/create_event.json"

    data = {"description": description,
            "event_type": "trigger",
            "service_key": service_key}

    resp = requests.post(pagerduty_url,
                         headers={
                             "Content-Type": "application/json; charset=utf-8"},
                         data=json.dumps(data))
    resp.raise_for_status()

    return resp.json()


class NosePagerDutyPlugin(Plugin):
    name = 'pagerduty'

    def options(self, parser, env):
        super(NosePagerDutyPlugin, self).options(parser, env)

    def configure(self, options, conf):
        super(NosePagerDutyPlugin, self).configure(options, conf)
        if not self.enabled:
            return

    def handle_alert(self, test, err):

        is_module = isinstance(test.context, ModuleType)

        if is_module:
            is_on, service_key = self.get_attribs(test.test.test)
        else:
            method = getattr(test.context, test.test._testMethodName)
            is_on, service_key = self.get_attribs(method, test.context)

        if is_on:
            _, test_ex, _ = err
            try:
                description = "{test} - {test_ex}".format(test=test,
                                                          test_ex=test_ex)
                log.warn(
                    "Triggering PagerDuty alert with description: "
                    "\"{description}\" service key: \"{service_key}\"".format(
                        description=description,
                        service_key=service_key))

                ret = trigger_pagerduty(description, service_key)

                log.warn(
                    "Alert triggered with incident key: {incident_key}".format(
                        incident_key=ret[u'incident_key']))
            except Exception as ex:
                log.error(ex)
        return False

    def handleError(self, test, err):
        return self.handle_alert(test, err)

    def handleFailure(self, test, err):
        return self.handle_alert(test, err)

    @staticmethod
    def get_attribs(function, cls=None):
        is_on = get_method_attr(function, cls, 'trigger_pagerduty')
        service_key = get_method_attr(function, cls, 'service_key', None)
        return is_on, service_key
