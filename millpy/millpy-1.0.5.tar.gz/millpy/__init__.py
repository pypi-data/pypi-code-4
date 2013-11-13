import requests
import urllib
import datetime
from .exceptions import (
    AuthorizationError, TransactionError, ServiceUnavailableError,
    UnexpectedResponseError, ResourceNotFoundError, RefundedAmountTooHighError,
)


api_key = None
"""Global API key.
"""


__version__ = '1.0.0'
"""millpy version.
"""


PAYMILL_BASE_URL = 'https://api.paymill.de/v2/'
UTC_EPOCH = datetime.datetime(1970, 1, 1)
ORDER_ASC = 'asc'
ORDER_DESC = 'desc'

parse_datetime = lambda x: UTC_EPOCH + datetime.timedelta(seconds=x)
parse_datetime_if_not_none = lambda x: UTC_EPOCH + \
    datetime.timedelta(seconds=x) if x is not None else None
parse_int_if_not_none = lambda x: int(x) if x else None
compose_datetime = lambda x: int((x - UTC_EPOCH).total_seconds())


class ApiResource(object):
    """Abstract API resource base class.
    """

    def __init__(self, id, api_key):
        """Initialize a resource representation.

        :param id: Resource ID.
        :param api_key: API key using which the resource was retrieved.
        """

        self.__dict__['_properties'] = {}
        self.__dict__['_changed'] = []

        self.__dict__['id'] = id
        self.__dict__['_api_key'] = api_key

    def update_from_json(self, properties, api_key=None):
        """Update the resource's properties from raw JSON data.

        :param properties: Resource properties.
        :param api_key: API key using which the refreshed data was retrieved.
        """

        if api_key:
            self.__dict__['_api_key'] = api_key
        self.__dict__['_changed'] = []
        self.__dict__['_properties'] = self.parse_data(properties)

    def parse_data(self, properties):
        """Parse the resource's properties from raw JSON data.

        Must be implemented by each resource implementation.

        :param properties: JSON data.
        :returns: a :class:`dict` mapping properties to values.
        """

        raise NotImplementedError

    @classmethod
    def compose_properties(cls, properties):
        """Compose resource's properties to serializeable data.

        Must be implemented by each resource implementation.

        :param properties: The resource's properties.
        :returns: a :class:`dict` mapping properties to POST parameters.
        """

        raise NotImplementedError

    @classmethod
    def deserialize(cls, data, used_api_key=None):
        """Deserialize a resource from raw JSON data

        :param data: JSON representation of the resource.
        :param used_api_key: API key used for data retrieval. Default ``None``.
        """

        # Extract the resource ID if possible.
        id = data.get(u'id', None)

        # Construct the resource.
        resource = cls(id=id,
                       api_key=used_api_key or api_key)
        resource.update_from_json(data)

        return resource

    @classmethod
    def request(cls,
                method='GET',
                params=None,
                url=None,
                id=None,
                key=None):
        """Perform the actual request.

        :param method: HTTP request method. Default ``GET``.
        :param params: Request parameters. Default ``None``.
        :param url:
            Request URL. If ``None``, the URL for the resource is used.
            Default ``None``.
        :param id: Resource ID. Default ``None``.
        :param key:
            Optional alternative API key. When ``None``, the globally
            configured API key is used.
        :returns: the response data deserialized to a :class:`dict`.
        """

        # Sanitize the request parameters.
        if params:
            sanitize_param_str = lambda x: x.encode('utf-8') \
                if isinstance(x, unicode) else x
            params = {
                sanitize_param_str(k): sanitize_param_str(params[k])
                for k in params
            }

        # Set up the headers.
        headers = {
            'User-Agent': 'millpy/%s' % (__version__, ),
        }

        # Perform the request.
        is_get = (method.upper() == 'GET')
        actual_url = url or cls.get_url_for_resource(id)

        response = requests.request(method,
                                    actual_url,
                                    auth=(key or api_key, ''),
                                    params = params if is_get else None,
                                    data = None if is_get else params,
                                    headers = headers,
                                    verify = False)

        # Verify the response code.
        if response.status_code < 200 or \
                response.status_code >= 300:
            if response.status_code == 401:
                raise AuthorizationError(
                    'authorization failed using %s' % (
                        'alternative API key' if key else 'global API key'
                    )
                )
            if response.status_code == 403:
                if response.headers['Content-Type'] == 'application/json':
                    try:
                        error_json = response.json()
                        raise UnexpectedResponseError(
                            'Error doing %s request on %s%s: %r' % (
                                method,
                                actual_url,
                                ' with %r' % (params) if params else '',
                                error_json
                            ),
                            error_json=error_json
                        )
                    except (TypeError, ValueError):
                        pass
                raise TransactionError('unexpected response with status code '
                                       '403: %r' % (response.text))
            if response.status_code == 404:
                raise ResourceNotFoundError(
                    'resource located at %s not found' % (url) if url else
                    'resource with ID %s not found' % (id) if id else
                    'resource not found on %s%s' % (
                        actual_url,
                        ' with %r' % (params) if params else ''
                    )
                )
            if response.status_code >= 500:
                raise ServiceUnavailableError(
                    'Paymill appears to be unavailable returning an HTTP '
                    'status code of %d' % (response.status_code)
                )

            if response.status_code == 412 and \
                    response.headers['Content-Type'] == 'application/json':
                error_json = response.json()
                if 'error' in error_json:
                    raise UnexpectedResponseError(
                        'Error doing %s request on %s%s: %r' % (
                            method,
                            actual_url,
                            ' with %r' % (params) if params else '',
                            error_json
                        ),
                        error_json=error_json
                    )

            raise UnexpectedResponseError('unexpected HTTP status code: '
                                          '%d' % (response.status_code))

        # Verify the content MIME type.
        content_type = response.headers.get('Content-Type', '')
        if content_type != 'application/json':
            raise UnexpectedResponseError('unexpected response content '
                                          'type: %s' % (content_type))

        # Return the JSON response data.
        return (response.json(), key or api_key, )

    @classmethod
    def get_url_for_resource(cls, id=None, resource_name=None):
        """Get the URL for a resource.

        Attempts to identify the resource name from the model. If no such
        resource name is defined, this method defaults to using a lower case
        class name as the resource name.

        :param id: Resource ID. Default ``None``.
        :param resource_name:
            Resource name. If no resource name is supplied, it is retrieved
            from the ``__resource_name__`` class property.
        """

        return '%s%s%s' % (PAYMILL_BASE_URL,
                           urllib.quote_plus(resource_name or
                                             getattr(cls, '__resource_name__',
                                                     None)),
                           '/%s' % (id) if id else '')

    def __getattr__(self, attr):
        try:
            return self._properties[attr]
        except KeyError:
            raise AttributeError('%s object has no attribute '
                                 '%r' % (type(self).__name__, attr))

    def __setattr__(self, k, v):
        if not k in self._properties or v != self._properties[k]:
            self._properties[k] = v
            if not k in self._changed:
                self._changed.append(k)

    @classmethod
    def _create(cls, api_key=None, **properties):
        """Create a resource.

        :param cls: Class.
        :param api_key:
            Optional alternative API key. When ``None``, the globally
            configured API key is used.
        :param \*\*properties: Properties.
        """

        response, api_key = cls.request('POST',
                                        cls.compose_properties(properties),
                                        key=api_key)
        return cls.deserialize(response[u'data'], api_key)

    def _update(self, updates, api_key=None):
        """Update the resource.

        :param updates: Sanitized updates parameters.
        :param api_key:
            Optional alternative API key. When ``None``, the globally
            configured API key is used.
        """

        if not self.id:
            raise ResourceNotFoundError('%s has no unique'
                                        'ID' % (self.__class__.__name__))

        response, api_key = self.request('PUT',
                                         updates,
                                         id=self.id,
                                         key=api_key or self._api_key)
        self.update_from_json(response[u'data'], api_key)

    def __repr__(self):
        return '<%s %s at %#x>' % (self.__class__.__name__,
                                   'ID %s' % (self.id) if id else '(deleted)',
                                   id(self))


class CreatableResource(ApiResource):
    """Abstract creatable API resource.

    Represents an API resource that can be created using a POST request to the
    endpoint of the specific resource.
    """

    @classmethod
    def create(cls, api_key=None, **kwargs):
        """Create a resource.

        :param cls: Class.
        :param api_key:
            Optional alternative API key. When ``None``, the globally
            configured API key is used.
        :param \*\*kwargs: Properties.
        """

        return cls._create(api_key, **kwargs)


class DetailableResource(ApiResource):
    """Abstract detailable API resource.

    Represents an API resource that can be requested by a unique ID as part
    of the URL.
    """

    @classmethod
    def get(cls, id, api_key=None):
        """Get a resource.

        :param cls: Class.
        :param id: Unique resource ID.
        :param api_key:
            Optional alternative API key. When ``None``, the globally
            configured API key is used.
        """

        # Perform the request.
        response, api_key = cls.request('GET', id=id, key=api_key)
        return cls.deserialize(response[u'data'], api_key)


class DeletableResource(ApiResource):
    """Abstract deletable API resource.

    Represents an API resource that can be deleted by a unique ID as part
    of the URL.
    """

    @classmethod
    def delete_by_id(cls, id, api_key=None):
        """Delete a resource represented by the given ID.

        :param id: Unique resource ID.
        :param api_key:
            Optional alternative API key. When ``None``, the globally
            configured API key is used.
        """

        # Perform the request.
        response, api_key = cls.request('DELETE', id=id, key=api_key)

    def delete(self, api_key=None):
        """Delete a resource.

        :param api_key:
            Optional alternative API key. When ``None``, the globally
            configured API key is used.
        """

        if not self.id:
            raise ResourceNotFoundError('resource has no ID')

        # Perform the request.
        response, api_key = self.request('DELETE',
                                         id=self.id,
                                         key=api_key or self._api_key)

        # Clear the resource.
        self.__dict__['id'] = None
        self.__dict__['_properties'] = {}
        self.__dict__['_changed'] = []


class UpdatableResource(ApiResource):
    """Abstract updatable API resource.

    Represents an API resource that can be update by a unique ID as part
    of the URL.
    """

    def save(self, api_key=None):
        """Save changes to a resource.

        :param api_key:
            Optional alternative API key. When ``None``, the globally
            configured API key is used.
        """

        # Check if any properties have changed.
        if len(self._changed) == 0:
            return

        # Compose the properties and perform the update.
        properties = self.compose_properties(
            {k: self._properties[k] for k in self._changed}
        )
        self._update(updates=properties, api_key=api_key)


class MappableResource(ApiResource):
    """Abstract mappable API resource.

    An API resource that can be parsed and composed using only explicit
    remappings contained in the ``__resource_parse_map__`` and
    ``__resource_compose_map__``. Any value not contained in those two
    :class:`dict`s will be pass through directly.

    The default resource parse mapping contains a mapping of the generuc
    ``created_at`` and ``updated_at`` properties.
    """

    __resource_parse_map__ = {
        'created_at': parse_datetime,
        'updated_at': parse_datetime,
    }

    __resource_compose_map__ = {}

    def parse_data(self, properties):
        return {
            k: self.__resource_parse_map__[k](v)
            if k in self.__resource_parse_map__ else v
            for k, v in properties.items()
        }

    @classmethod
    def compose_properties(cls, properties):
        return {
            k: cls.__resource_compose_map__[k](v)
            if k in cls.__resource_compose_map__ else v
            for k, v in properties.items()
        }


class ListableResource(ApiResource):
    """Abstract listable API resource.

    An API resource that can be list.
    """

    @classmethod
    def list(cls,
             created_at=None,
             order_by=None,
             order=None,
             api_key=None,
             **properties):
        """List.
        """

        # Sanitize parameters.
        params = properties

        if created_at:
            if isinstance(created_at, (list, tuple, )):
                params['created_at'] = \
                    '%s-%s' % (compose_datetime(created_at[0]),
                               compose_datetime(created_at[1]))
            else:
                params['created_at'] = compose_datetime(created_at)
        if order_by:
            if order not in [ORDER_ASC, ORDER_DESC, None]:
                raise ValueError('invalid order: %s' % (order))
            params['order'] = '%s_%s' % (order_by, order) if order else \
                order_by
        elif order:
            raise ValueError('list cannot be ordered without an order_by '
                             'parameter')

        # Request.
        response, api_key = cls.request(params=params,
                                        key=api_key)
        return [cls.deserialize(r, api_key) for r in response['data']]


class Client(CreatableResource,
             DetailableResource,
             DeletableResource,
             UpdatableResource,
             MappableResource,
             ListableResource):
    """Client.
    """

    __resource_name__ = 'clients'

    __resource_parse_map__ = {
        'created_at': parse_datetime,
        'updated_at': parse_datetime,
        'payment': lambda payments: [
            x if isinstance(x, (str, unicode, )) else
            CreditCardPayment.deserialize(x) if x['type'] == 'creditcard' else
            DebitPayment.deserialize(x) for x in payments if x is not None
        ],
    }


class Offer(CreatableResource,
            DetailableResource,
            DeletableResource,
            UpdatableResource,
            MappableResource,
            ListableResource):
    """Offer.

    An offer is a recurring plan which a user can subscribe to. You can create
    different offers with different plan attributes e.g. a monthly or a yearly
    based paid offer/plan.
    """

    INTERVAL_WEEK = 'week'
    INTERVAL_MONTH = 'month'
    INTERVAL_YEAR = 'year'

    __resource_name__ = 'offers'

    __resource_parse_map__ = {
        'created_at': parse_datetime,
        'updated_at': parse_datetime,
        'amount': lambda x: int(x),
    }


class Payment(MappableResource):
    """Generic payment.
    """

    __resource_name__ = 'payments'
    __resource_parse_map__ = {
        'created_at': parse_datetime,
        'updated_at': parse_datetime,
        'expire_month': parse_int_if_not_none,
        'expire_year': parse_int_if_not_none,
    }

    @classmethod
    def list(cls,
             created_at=None,
             order_by=None,
             order=None,
             api_key=None,
             **properties):
        """List.
        """

        # Sanitize parameters.
        params = properties

        if created_at:
            if isinstance(created_at, (list, tuple, )):
                params['created_at'] = \
                    '%s-%s' % (compose_datetime(created_at[0]),
                               compose_datetime(created_at[1]))
            else:
                params['created_at'] = compose_datetime(created_at)
        if order_by:
            if order not in [ORDER_ASC, ORDER_DESC, None]:
                raise ValueError('invalid order: %s' % (order))
            params['order'] = '%s_%s' % (order_by, order) if order else \
                order_by
        elif order:
            raise ValueError('list cannot be ordered without an order_by '
                             'parameter')

        # Request.
        response, api_key = cls.request(params=params,
                                        key=api_key)
        return [CreditCardPayment.deserialize(r, api_key)
                if r['type'] == 'creditcard' else
                DebitPayment.deserialize(r, api_key) for r in response['data']]


class CreditCardPayment(Payment,
                        DetailableResource,
                        DeletableResource):
    """Credit card payment.
    """

    @classmethod
    def create(cls, token, client=None, api_key=None):
        """Create a credit card payment.

        :param token: Unique credit card token.
        :param client:
            Optional client to add the payment to. If a :class:`Client`
            instance is passed, the unique ID of the instance will be used to
            identify the client, otherwise the unique ID is expected as a
            string. Default ``None``.
        :param api_key:
            Optional alternative API key. When ``None``, the globally
            configured API key is used.
        """

        if client is not None:
            if isinstance(client, Client):
                client = client.id
            if not isinstance(client, (str, unicode, )):
                raise ValueError('invalid unique client ID: %r' % (client))

        return cls._create(type='creditcard',
                           token=token,
                           client=client,
                           api_key=api_key)


class DebitPayment(Payment,
                   DetailableResource,
                   DeletableResource):
    """Debit payment.
    """

    @classmethod
    def create(cls, token, client=None, api_key=None):
        """Create a debit payment.

        :param token: Unique debit payment token.
        :param client:
            Optional client to add the payment to. If a :class:`Client`
            instance is passed, the unique ID of the instance will be used to
            identify the client, otherwise the unique ID is expected as a
            string. Default ``None``.
        :param api_key:
            Optional alternative API key. When ``None``, the globally
            configured API key is used.
        """

        if client is not None:
            if isinstance(client, Client):
                client = client.id
            if not isinstance(client, (str, unicode, )):
                raise ValueError('invalid unique client ID: %r' % (client))

        return cls._create(type='debit',
                           token=token,
                           client=client,
                           api_key=api_key)


class Subscription(MappableResource,
                   DetailableResource,
                   ListableResource):
    """Subscription.

    Subscriptions allow you to charge recurring payments on a client's credit
    card/to a client's direct debit. A subscription connects a client to the
    offers-object. A client can have several subscriptions to different
    offers, but only one subscription to the same offer.
    """

    __resource_name__ = 'subscriptions'

    __resource_parse_map__ = {
        'created_at': parse_datetime,
        'updated_at': parse_datetime,
        'trial_start': parse_datetime_if_not_none,
        'canceled_at': parse_datetime_if_not_none,
        'trial_end': parse_datetime_if_not_none,
        'offer': lambda x: Offer.deserialize(x),
        'client': lambda x: Client.deserialize(x),
        'payment': lambda x: CreditCardPayment.deserialize(x) if
        x['type'] == 'creditcard' else DebitPayment.deserialize(x),
        'cancel_at_period_end': lambda x: bool(x) if
        isinstance(x, (bool, int, long)) else (x.lower() in ['true', '1', ]),
    }

    @classmethod
    def create(cls,
               client,
               offer,
               payment,
               api_key=None):
        """Create a subscription.

        :param client:
            Client to subscribe. If a :class:`Client` instance is passed, the
            unique ID of the instance will be used to identify the client,
            otherwise the unique ID is expected as a string.
        :param offer:
            Offer to subscribe the client to. If a :class:`Offer` instance is
            passed, the unique ID of the instance will be used to identify the
            offer, otherwise the unique ID is expected as a string.
        :param payment:
            Payment to charge. If a :class:`Payment` instance is passed, the
            unique ID of the instance will be used to identify the payment,
            otherwise the unique ID is expected as a string.
        :param api_key:
            Optional alternative API key. When ``None``, the globally
            configured API key is used.
        """

        if isinstance(client, Client):
            client = client.id
        if not isinstance(client, (str, unicode, )):
            raise ValueError('invalid unique client ID: %r' % (client))

        if isinstance(offer, Offer):
            offer = offer.id
        if not isinstance(offer, (str, unicode, )):
            raise ValueError('invalid unique offer ID: %r' % (offer))

        if isinstance(payment, Payment):
            payment = payment.id
        if not isinstance(payment, (str, unicode, )):
            raise ValueError('invalid unique payment ID: %r' % (payment))

        return cls._create(client=client,
                           offer=offer,
                           payment=payment,
                           api_key=api_key)

    def update_cancel_at_period_end(self, cancel=True, api_key=None):
        """Update the cancellation state of the subscription.

        :param cancel: Whether to cancel the subscription at the period end.
        """

        self._update({'cancel_at_period_end': 'true' if cancel else 'false'},
                     api_key=api_key)

    def cancel(self, api_key=None):
        """Cancel the subscription.

        :param api_key:
            Optional alternative API key. When ``None``, the globally
            configured API key is used.
        """

        if not self.id:
            raise ResourceNotFoundError('subscription has no ID')

        # Perform the request.
        response, api_key = self.request('DELETE',
                                         id=self.id,
                                         key=api_key or self._api_key)
        self.update_from_json(response[u'data'], api_key)


class Transaction(MappableResource,
                  DetailableResource,
                  ListableResource):
    """Transaction.

    A transaction is the charging of a credit card or a direct debit. In this
    case you need a new transaction object with either a valid token, payment,
    client + payment or preauthorization. Every transaction has a unique
    identifier which will be generated by Paymill to identify every
    transaction. You can issue/create, list and display transactions in
    detail. Refunds can be done in an extra entity.
    """

    STATUS_OPEN = 'open'
    STATUS_PENDING = 'pending'
    STATUS_CLOSED = 'closed'
    STATUS_FAILED = 'failed'
    STATUS_PARTIAL_REFUNDED = 'partial_refunded'
    STATUS_REFUNDED = 'refunded'
    STATUS_PREAUTHORIZE = 'preauthorize'

    __resource_name__ = 'transactions'
    __resource_parse_map__ = {
        'created_at': parse_datetime,
        'updated_at': parse_datetime,
        'amount': lambda x: int(x),
        'client': lambda x: Client.deserialize(x) if x is not None else x,
        'payment': lambda x: None if x is None else
        CreditCardPayment.deserialize(x) if x['type'] == 'creditcard' else
        DebitPayment.deserialize(x),
        'refunds': lambda refunds: [Refund.deserialize(r) for r in refunds] if
        isinstance(refunds, list) else [],
        'expire_month': parse_int_if_not_none,
        'expire_year': parse_int_if_not_none,
    }

    @classmethod
    def create(cls,
               amount,
               currency,
               description=None,
               client=None,
               payment=None,
               token=None,
               api_key=None):
        """Create a subscription.

        :param amount:
            Amount in integral 1/100th currency units to charge.
        :param currency:
            `ISO 4217 <http://en.wikipedia.org/wiki/ISO_4217>_` formatted
            currency code.
        :param description:
            An optional, short description of the transaction.
        :param client:
            Client to transact. If a :class:`Client` instance is passed, the
            unique ID of the instance will be used to identify the client,
            otherwise the unique ID is expected as a string. Optional.
        :param token:
            Payment token to charge.
        :param payment:
            Payment to charge. If a :class:`Payment` instance is
            passed, the unique ID of the instance will be used to identify the
            payment, otherwise the unique ID is expected as a string.
        :param api_key:
            Optional alternative API key. When ``None``, the globally
            configured API key is used.
        """

        kwargs = {
            'amount': amount,
            'currency': currency,
            'description': description,
            'api_key': api_key
        }

        # Sanitize input.
        if token is not None:
            if not isinstance(token, (str, unicode, )):
                raise ValueError('invalid token: %r' % (token))

        if payment is not None:
            if isinstance(payment, Payment):
                payment = payment.id
            if not isinstance(payment, (str, unicode, )):
                raise ValueError('invalid unique payment ID: %r' % (payment))

        if client is not None:
            if isinstance(client, Client):
                client = client.id
            if not isinstance(client, (str, unicode, )):
                raise ValueError('invalid unique client ID: %r' % (client))

        # Make sure that we have a valid payment method.
        if token:
            if payment or client:
                raise ValueError('payment or client must not be passed when '
                                 'creating a transaction using a token')
            kwargs['token'] = token
        elif payment:
            kwargs['payment'] = payment
            if client:
                kwargs['client'] = client
        else:
            raise ValueError('at least one payment identification must be '
                             'passed when creating a transaction')

        return cls._create(**kwargs)

    def refund(self, amount, description=None, api_key=None):
        """Refund an amount of the transaction.

        :param amount: Amount in integral 1/100th currency units to refund.
        :param description: An optional, short description of the refund.
        :param api_key:
            Optional alternative API key. When ``None``, the globally
            configured API key is used.
        :returns: a :class:`Refund` instance representing the refund.
        """

        url = self.get_url_for_resource(self.id, 'refunds')

        try:
            response, api_key = self.request(
                'POST', {
                    'amount': amount,
                    'description': description,
                }, url=url, key=api_key
            )
        except UnexpectedResponseError as exception:
            if exception.error_json and \
                    exception.error_json.get('exception') == \
                    'refund_amount_to_high':
                raise RefundedAmountTooHighError()
            raise

        update_response, api_key = self.request('GET', id=self.id, key=api_key)
        self.update_from_json(update_response['data'])

        return Refund.deserialize(response['data'])


class Refund(MappableResource, DetailableResource):
    """Refund.
    """

    STATUS_OPEN = 'open'
    STATUS_PENDING = 'pending'
    STATUS_REFUNDED = 'refunded'

    __resource_name__ = 'refunds'

    __resource_parse_map__ = {
        'created_at': parse_datetime,
        'updated_at': parse_datetime,
        'amount': lambda x: int(x),
        'transaction': lambda x: None if x is None else
        Transaction.deserialize(x),
    }


class Preauthorization(MappableResource, DetailableResource):
    """Preauthorization.

    If you'd like to reserve some money from the client's creditcard but you'd
    also like to execute the transaction itself a bit later, then use
    preauthorizations.
    """

    __resource_name__ = 'preauthorizations'

    __resource_parse_map__ = {
        'created_at': parse_datetime,
        'updated_at': parse_datetime,
        'client': lambda x: Client.deserialize(x) if x is not None else x,
        'payment': lambda x: None if x is None else
        CreditCardPayment.deserialize(x) if x['type'] == 'creditcard'
        else DebitPayment.deserialize(x),
    }

    @classmethod
    def create(cls,
               amount,
               currency,
               payment=None,
               token=None,
               client=None,
               api_key=None):
        """Create a subscription.

        Either a payment or a token must be passed. If a token is passed, the
        payment is ignored. The payment must currently be a credit card
        payment.

        :param amount:
            Amount in integral 1/100th currency units to charge.
        :param currency:
            `ISO 4217 <http://en.wikipedia.org/wiki/ISO_4217>_` formatted
            currency code.
        :param payment:
            Payment to charge. If a :class:`CreditCardPayment` instance is
            passed, the unique ID of the instance will be used to identify the
            payment, otherwise the unique ID is expected as a string.
        :param api_key:
            Optional alternative API key. When ``None``, the globally
            configured API key is used.
        """

        kwargs = {
            'amount': amount,
            'currency': currency,
            'api_key': api_key
        }

        if token is not None:
            if not isinstance(token, (str, unicode, )):
                raise ValueError('invalid token: %r' % (token))
            kwargs['token'] = token
        elif payment is None:
            raise ValueError('either a token or a payment must be passed to '
                             'the creation of a preauthorization')
        else:
            if isinstance(payment, Payment):
                payment = payment.id
            if not isinstance(payment, (str, unicode, )):
                raise ValueError('invalid unique payment ID: %r' % (payment))
            kwargs['payment'] = payment

        return cls._create(**kwargs)
