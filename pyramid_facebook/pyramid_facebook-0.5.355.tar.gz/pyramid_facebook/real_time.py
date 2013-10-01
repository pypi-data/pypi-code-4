# -*- coding: utf-8 -*-
import sys
import argparse
import logging
import urlparse
import json

from facepy import FacepyError, get_application_access_token, GraphAPI

from pyramid.httpexceptions import (
    HTTPForbidden,
    HTTPOk,
    HTTPInternalServerError,
    )
from pyramid.paster import bootstrap
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config

from pyramid_facebook.events import ChangeNotification
from pyramid_facebook.predicates import (
    headers_predicate,
    request_params_predicate,
    nor_predicate,
    )
from pyramid_facebook.security import UpdateSubscription, NotifyRealTimeChanges

log = logging.getLogger(__name__)


def includeme(config):
    """Adds routes related to real time updates.

    Routes Added:

    * ``facebook_real_time_subscription_verification`` associated to url
        /{namespace}/real-time

    * ``facebook_real_time_notification`` associated to url
        /{namespace}/real-time

    * ``facebook_real_time_subscriptions`` associated to url
        /{namespace}/real-time/subscriptions

    * ``facebook_real_time_subscriptions_update`` associated to url
        /{namespace}/real-time/subscriptions

    * ``facebook_real_time_subscriptions_delete`` associated to url
        /{namespace}/real-time/subscriptions
    """
    log.debug('Adding route "facebook_real_time_subscription_verification".')
    config.add_route(
        'facebook_real_time_subscription_verification',
        '/real-time',
        request_method='GET',
        custom_predicates=[
            request_params_predicate(
                'hub.challenge',
                'hub.verify_token',
                **{'hub.mode': 'subscribe'}
                ),
            ]
        )

    log.debug('Adding route "facebook_real_time_notification".')
    config.add_route(
        'facebook_real_time_notification',
        '/real-time',
        request_method='POST',
        factory='pyramid_facebook.security.RealTimeNotificationContext',
        custom_predicates=[
            headers_predicate(
                'X-Hub-Signature',
                **{'Content-Type': 'application/json'}
                )
            ]
        )

    log.debug('Adding route "facebook_real_time_subscriptions".')
    config.add_route(
        'facebook_real_time_subscriptions',
        '/real-time/subscriptions',
        request_method='GET',
        request_param='access_token',
        factory='pyramid_facebook.security.AdminContext',
        )

    log.debug('Adding route "facebook_real_time_subscriptions_update".')
    config.add_route(
        'facebook_real_time_subscriptions_update',
        '/real-time/subscriptions',
        request_method='POST',
        custom_predicates=[
            nor_predicate(object=('user', 'permissions', 'page', 'errors',
                                  'payment_subscriptions', 'payments',)),
            request_params_predicate('fields', 'access_token'),
            ],
        factory='pyramid_facebook.security.AdminContext',
        )

    log.debug('Adding route "facebook_real_time_subscriptions_delete".')
    config.add_route(
        'facebook_real_time_subscriptions_delete',
        '/real-time/subscriptions',
        request_method='DELETE',
        request_param='access_token',
        factory='pyramid_facebook.security.AdminContext',
        )

    config.scan(package='pyramid_facebook.real_time')


@view_config(route_name='facebook_real_time_subscription_verification')
def verify_real_time_subscription(request):
    verify_token = request.params['hub.verify_token']
    settings = request.registry.settings
    try:
        access_token = get_application_access_token(
            settings['facebook.app_id'],
            settings['facebook.secret_key'],
            )
        if access_token == verify_token:
            return Response(request.params['hub.challenge'])
    except FacepyError:
        log.exception('get_application_access_token failed')
    raise HTTPForbidden()


@view_config(context=FacepyError, renderer='json')
def render_facepy_error(exc, request):
    return dict(
        error=dict(
            type=exc.__class__.__name__,
            code=getattr(exc, 'code'),
            message=exc.message,
            )
        )


@view_config(
    route_name='facebook_real_time_subscriptions',
    renderer='json',
    permission=UpdateSubscription,
    )
def list_real_time_subscriptions(request):
    settings = request.registry.settings
    app_id = settings['facebook.app_id']
    secret_key = settings['facebook.secret_key']
    access_token = get_application_access_token(app_id, secret_key)
    return GraphAPI(access_token).get('%s/subscriptions' % app_id)


@view_config(
    route_name='facebook_real_time_subscriptions_update',
    renderer='json',
    permission=UpdateSubscription,
    )
def update_real_time_subscription(request):
    settings = request.registry.settings
    fb_object = request.params['object']
    fields = request.params['fields']
    access_token = get_application_access_token(
        settings['facebook.app_id'],
        settings['facebook.secret_key'],
        )
    # url of route named `facebook_real_time_subscription_verification`
    # is the same as route named `facebook_real_time_notification` but with
    # different predicates
    url = request.route_url('facebook_real_time_subscription_verification')
    return (GraphAPI(access_token).post(
        '%s/subscriptions' % settings['facebook.app_id'],
        object=fb_object,
        fields=fields,
        callback_url=url,
        verify_token=access_token
        ))


@view_config(
    route_name='facebook_real_time_subscriptions_delete',
    renderer='json',
    permission=UpdateSubscription,
    )
def delete_real_time_subscription(request):
    settings = request.registry.settings
    access_token = get_application_access_token(
        settings['facebook.app_id'],
        settings['facebook.secret_key'],
        )
    return GraphAPI(access_token).delete(
        '%s/subscriptions' % settings['facebook.app_id'],
        )


@view_config(
    route_name='facebook_real_time_notification',
    permission=NotifyRealTimeChanges,
    )
def process_real_time_notification(context, request):
    log.debug('process_real_time_notification json_body=%s', request.json_body)
    try:
        request.registry.notify(ChangeNotification(context, request))
    except Exception:
        log.exception(
            'process_real_time_notification - json_body: %s',
            request.json_body,
            )
        # raise an HTTP error so facebook will send back same update later
        raise HTTPInternalServerError()
    return HTTPOk()


@view_config(route_name='facebook_real_time_notification',
             context=HTTPForbidden)
def forbid_real_time_update(context, request):
    raise HTTPForbidden()


class ManageSubscriptions(object):
    """Manage real-time subscriptions.

    The easiest way to setup real time subscription is to define the
    `facebook.rt-subscriptions` setting in the ini file::

        facebook.rt-subscriptions =
            user = name, friends
            payments = actions, disputes


    Then run the setup command::

        $ pfacebook-real-time env.ini setup


    To list subscriptions::

        $ pfacebook-real-time env.ini list


    To update or create subscriptions without changing the config file::

        $ pfacebook-real-time env.ini update user=friends,name payments=actions


    To delete all subscriptions::

        $ pfacebook-real-time env.ini delete
    """
    def __init__(self, argv):
        self.setup_parsers()
        self.args = self.parser.parse_args(argv)

        self.env = bootstrap(self.args.config_uri)
        self.settings = self.env['registry'].settings
        self.request = self.env['request']

        self.app_id = self.settings['facebook.app_id']
        secret_key = self.settings['facebook.secret_key']

        self.graph_api = GraphAPI(get_application_access_token(self.app_id,
                                                               secret_key))
        self.base_host = self.get_application_base_host(self.graph_api,
                                                        self.app_id)

    def setup_parsers(self):
        self.parser = argparse.ArgumentParser(
            prog='pfacebook-real-time',
            description=self.__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        self.parser.add_argument(
            'config_uri',
            help='Paste config_uri string expecting the format inifile#name',
            )

        subparsers = self.parser.add_subparsers()

        setup_parser = subparsers.add_parser('setup')
        setup_parser.set_defaults(func=self.setup)

        list_parser = subparsers.add_parser('list')
        list_parser.set_defaults(func=self.list)

        update_parser = subparsers.add_parser('update')
        update_parser.set_defaults(func=self.update)
        update_parser.add_argument('rt_settings', nargs='*',
                                   metavar='object=field1,field2',
                                   help='Objects and fields to update '
                                        'subscription on.')

        delete_parser = subparsers.add_parser('delete')
        delete_parser.set_defaults(func=self.delete)

    def run(self):
        self.args.func()

    def setup(self):
        rt_settings = self.settings['facebook.rt-subscriptions'].split('\n')
        self.do_update_requests(rt_settings)
        self.list()

    def list(self):
        request = self.new_request()
        result = list_real_time_subscriptions(request)
        print json.dumps(result, indent=4)

    def update(self):
        self.do_update_requests(self.args.rt_settings)
        self.list()

    def delete(self):
        request = self.new_request('facebook_real_time_subscriptions_delete')
        delete_real_time_subscription(request)
        self.list()

    def get_application_base_host(self, graph_api, app_id):
        canvas_url = graph_api.get(app_id, fields='canvas_url')['canvas_url']
        return urlparse.urlparse(canvas_url).netloc

    def new_request(self, route_name=None, **kw):
        path = self.request.route_path(route_name) if route_name else ''
        request = Request.blank(path, POST=kw, environ=self.request.environ,
                                host=self.base_host)
        request.registry = self.request.registry
        return request

    def do_update_requests(self, rt_settings):
        for setting in rt_settings:
            setting = setting.replace(' ', '')
            if not setting:
                continue
            obj, fields = setting.split('=')
            req = self.new_request('facebook_real_time_subscriptions_update',
                                   object=obj, fields=fields)
            update_real_time_subscription(req)


def command_line_script():
    ManageSubscriptions(sys.argv[1:]).run()
