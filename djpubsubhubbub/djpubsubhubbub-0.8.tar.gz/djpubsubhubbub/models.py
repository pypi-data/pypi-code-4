import urllib2
import feedparser

from hashlib import sha1
from urllib import urlencode, quote
from datetime import datetime, timedelta

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch

from djpubsubhubbub import signals
from djpubsubhubbub.config import Config

try:
    from django.utils.timezone import now as use_now
except ImportError:
    use_now = datetime.now

DEFAULT_LEASE_SECONDS = 2592000 # 30 days in seconds


class SubscriptionManager(models.Manager):

    def do_action(self, topic, hub=None, callback=None, lease_seconds=None,
                  mode='subscribe', verify='sync', debug=False):
        config = Config()
        if hub is None:
            hub = self._get_hub(topic)

        if hub is None:
            raise TypeError(
                'hub cannot be None if the feed does not provide it')

        if lease_seconds is None:
            lease_seconds = getattr(settings, 'PUBSUBHUBBUB_LEASE_SECONDS',
                                   DEFAULT_LEASE_SECONDS)

        subscription, created = self.get_or_create(
            hub=hub, topic=topic)
        signals.pre_subscribe.send(sender=subscription, created=created)
        subscription.set_expiration(lease_seconds, run_save=False)
        token = subscription.generate_token(mode)
        headers = config.get_extra_hub_headers(topic, hub)

        if callback is None:
            try:
                callback_path = reverse('pubsubhubbub_callback',
                                        args=(subscription.pk,))
            except NoReverseMatch:
                raise TypeError(
                    'callback cannot be None if there is not a reversible URL')
            else:
                callback = '{0}://{1}{2}'.format(
                    config.get_default_callback_scheme(topic, hub),
                    config.get_default_callback_host(topic, hub),
                    callback_path
                )

        response = self._send_request(hub, {
                'mode': mode,
                'callback': callback,
                'topic': topic,
                'verify': verify,
                'verify_token': token,
                'lease_seconds': lease_seconds,
            }, headers, debug)

        info = response.info()
        info.status = response.code
        if debug:
            print('Info:\n{0}\n\n'.format(info))

        if info.status not in [204, 202]:
            # 204 is sync verification
            # 202 is async verification
            error = response.read()
            raise urllib2.URLError(
                'error with mode "{0}" to {1} on {2}:\n{3}'.format(
                    mode,
                    topic,
                    hub,
                    error,
                )
            )

        return subscription

    def status(self, topic, hub=None, debug=False):
        config = Config()
        if hub is None:
            hub = self._get_hub(topic)
        headers = config.get_extra_hub_headers(topic, hub)

        try:
            response = self._send_request(
                '{0}?hub.mode=status&hub.topic={1}'.format(hub, quote(topic)),
                {},
                headers,
                debug,
            )
        except urllib2.HTTPError as e:
            if e.code == 302:
               return True
        return False

    def retrieve(self, topic, hub=None, debug=False):
        config = Config()
        if hub is None:
            hub = self._get_hub(topic)
        headers = config.get_extra_hub_headers(topic, hub)

        response = self._send_request(
            '{0}?hub.mode=retrieve&hub.topic={1}'.format(hub, quote(topic)),
            {},
            headers,
            debug,
        )

        parsed = feedparser.parse(response.read())
        return parsed

    def subscribe(self, topic, **kwargs):
        return self.do_action(topic, mode='subscribe', **kwargs)

    def unsubscribe(self, topic, **kwargs):
        return self.do_action(topic, mode='unsubscribe', **kwargs)

    def _get_hub(self, topic):
        parsed = feedparser.parse(topic)
        for link in parsed.feed.links:
            if link['rel'] == 'hub':
                return link['href']

    def _send_request(self, url, data, headers={}, debug=False):
        def data_generator():
            for key, value in data.items():
                key = 'hub.' + key
                if isinstance(value, (basestring, int)):
                    yield key, str(value)
                else:
                    for subvalue in value:
                        yield key, value

        if data:
            encoded_data = urlencode(list(data_generator()))
            if debug:
                print('Sending:\n{0}\n{1}\n{2}\n\n'.format(
                    url,
                    encoded_data,
                    headers,
                ))
            req = urllib2.Request(url, encoded_data, headers=headers)
        else:
            if debug:
                print('Sending:\n{0}\n{1}\n\n'.format(url, headers))
            req = urllib2.Request(url, headers=headers)

        return urllib2.urlopen(req)


class Subscription(models.Model):
    hub = models.URLField()
    topic = models.URLField()
    verified = models.BooleanField(default=False)
    verify_token = models.CharField(max_length=60)
    lease_expires = models.DateTimeField(default=use_now)

    is_subscribed = models.BooleanField(default=False)

    date = models.DateTimeField(default=use_now)
    updated = models.DateTimeField(default=use_now)

    objects = SubscriptionManager()

    class Meta:
        ordering = ('id',)

    def __unicode__(self):
        if self.verified:
            verified = u'verified'
        else:
            verified = u'unverified'
        return u'to {0} on {1}: {2}'.format(
            self.topic,
            self.hub,
            verified,
        )

    def __str__(self):
        return str(unicode(self))

    def set_expiration(self, lease_seconds, run_save=True):
        self.lease_expires = use_now() + timedelta(seconds=lease_seconds)
        if run_save:
            self.save()

    def generate_token(self, mode, run_save=True):
        assert self.pk is not None, \
            'Subscription must be saved before generating token'
        token = '{0}{1}'.format(
            mode[:20],
            sha1('{0}{1}{2}'.format(
                settings.SECRET_KEY,
                self.pk,
                mode,
            )).hexdigest(),
        )
        self.verify_token = token
        if run_save:
            self.save()
        return token

    def save(self, *args, **kwargs):
        if self.id:
            self.updated = use_now()
        super(Subscription, self).save(*args, **kwargs)
