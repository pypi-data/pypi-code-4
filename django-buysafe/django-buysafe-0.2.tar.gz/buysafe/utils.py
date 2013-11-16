import importlib
from django.conf import settings
from django.http import HttpResponse
from django.db.models.loading import get_model
from django.shortcuts import render
from buysafe.models import PaymentMethod
from buysafe.forms import BuySafeReceiveForm, WebATMReceiveForm


PAYMENT_RECEIVE_FORMS = {
    PaymentMethod.TYPE_BUYSAFE: BuySafeReceiveForm,
    PaymentMethod.TYPE_WEBATM: WebATMReceiveForm
}


def strip_non_number(text):
    result = ''
    for char in text:
        if char.isdigit():
            result += char
    return result


def default_order_info_handler(request, context, **kwargs):
    order_id = kwargs['order_id']
    Order = get_model('shop', 'Order')
    order = Order.objects.get(id=int(order_id))
    return {
        'price': order.total,
        'order_info': unicode(order),
        'order_id': order.id,
        'name': order.billing_name(),
        'phone': strip_non_number(order.billing_detail_phone),
        'email': order.billing_detail_email
    }


def make_response_handler(response_type, content=None):
    if content is not None:
        def f(**kwargs):
            return response_type(content)
    else:
        def f(**kwargs):
            return response_type()
    f._is_response_handler = True
    return f


def call_handler(name, default_handler, **kwargs):
    """
    Call the handler with `name` set in settings.py with provided keyword
    arguments, and fallback to `default_handler` if the name is not set. If
    `default_handler` is none and the name is not set, nothing happends and
    None will be returned.
    """
    try:
        handler_name = getattr(settings, name)
    except AttributeError:
        if default_handler is not None:
            result = default_handler(**kwargs)
        else:
            result = None
    else:
        components = handler_name.split('.')
        module_name, function_name = '.'.join(components[:-1]), components[-1]
        module = importlib.import_module(module_name)
        result = getattr(module, function_name)(**kwargs)
    return result


def call_handler_and_render(name, default_handler, **kwargs):
    result = call_handler(name, default_handler, **kwargs)
    if result is None \
            and getattr(default_handler, '_is_response_handler', False):
        return default_handler(**kwargs)
    if isinstance(result, HttpResponse):
        return result
    return render(kwargs['request'], kwargs['template'], kwargs['context'])


def get_payment_form(payment_type, querydict):
    methods = PaymentMethod.enabled.filter(payment_type=payment_type)
    form = None
    form_type = PAYMENT_RECEIVE_FORMS[payment_type]
    for method in methods:
        password = method.password
        form = form_type(password, querydict)
        if form.is_valid():
            break
        else:
            form = None
    return form
