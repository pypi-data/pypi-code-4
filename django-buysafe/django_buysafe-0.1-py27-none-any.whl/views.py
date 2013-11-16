# -*- coding: utf8

from django.http import HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render
from buysafe.models import PaymentMethod
from buysafe.forms import SunTechReceiveForm, BuySafeSendForm, WebATMSendForm
from buysafe.utils import (
    call_handler, call_handler_and_render, get_payment_form,
    default_order_info_handler, make_response_handler
)


PAYMENT_SEND_FORMS = {
    PaymentMethod.TYPE_BUYSAFE: BuySafeSendForm,
    PaymentMethod.TYPE_WEBATM: WebATMSendForm
}


def entry(request, order_id, template='buysafe/entry.html'):
    return render(request, template, {'order_id': order_id})


@require_POST
def start(request, template='buysafe/start.html'):
    keyword_args = {}
    for k in request.POST:
        keyword_args[k] = request.POST[k]

    context = {}

    info = call_handler(
        'BUYSAFE_FORM_VALUES_GENERATOR',
        default_order_info_handler,
        request=request, context=context, **keyword_args
    )

    forms = []
    payment_methods = PaymentMethod.enabled.all()
    for method in payment_methods:
        form_model = PAYMENT_SEND_FORMS[method.payment_type]
        info['store_name'] = method.store_id
        form = form_model(
            store_password=method.password, initial=info
        )
        form.fill_checksum()
        form.submit_button_title = method.name
        forms.append(form)

    context['forms'] = forms
    return call_handler_and_render(
        'BUYSAFE_START_HANDLER', None,
        request=request, template=template, context=context,
        forms=forms, payment_methods=payment_methods
    )


@csrf_exempt
@require_POST
def success(request, payment_type, template='buysafe/success.html'):
    context = {}
    payment_type = int(payment_type)
    form = get_payment_form(payment_type, request.POST)
    if form is None:
        return call_handler_and_render(
            'BUYSAFE_SUCCESS_INVALID_HANDLER',
            make_response_handler(HttpResponseBadRequest),
            request=request, context=context, form=form
        )
    context['data'] = form.cleaned_data
    send_type = form.cleaned_data['send_type']
    if send_type == SunTechReceiveForm.SEND_TYPE.BACKGROUND:
        return call_handler_and_render(
            'BUYSAFE_SUCCESS_BACKGROUND_HANDLER',
            make_response_handler(HttpResponse),
            request=request, context=context, form=form
        )
    return call_handler_and_render(
        'BUYSAFE_SUCCESS_RENDER_HANDLER', None,
        request=request, template=template, context=context, form=form
    )


@csrf_exempt
@require_POST
def fail(request, payment_type, template='buysafe/fail.html'):
    context = {}
    payment_type = int(payment_type)
    form = get_payment_form(payment_type, request.POST)
    if form is None:
        return call_handler_and_render(
            'BUYSAFE_FAIL_INVALID_HANDLER',
            make_response_handler(HttpResponseBadRequest),
            request=request, context=context, form=form
        )
    context['data'] = form.cleaned_data
    send_type = form.cleaned_data['send_type']
    if send_type == SunTechReceiveForm.SEND_TYPE.BACKGROUND:
        return call_handler_and_render(
            'BUYSAFE_FAIL_BACKGROUND_HANDLER',
            make_response_handler(HttpResponse),
            request=request, context=context, form=form
        )
    return call_handler_and_render(
        'BUYSAFE_FAIL_RENDER_HANDLER', None,
        request=request, template=template, context=context, form=form
    )


@csrf_exempt
@require_POST
def check(request, payment_type):
    context = {}
    payment_type = int(payment_type)
    form = get_payment_form(payment_type, request.POST)
    if form is None:
        return call_handler_and_render(
            'BUYSAFE_CHECK_INVALID_HANDLER',
            make_response_handler(HttpResponseBadRequest),
            request=request, context=context, form=form
        )
    send_type = form.cleaned_data['send_type']
    if send_type == SunTechReceiveForm.SEND_TYPE.BACKGROUND:
        return call_handler_and_render(
            'BUYSAFE_CHECK_HANDLER',
            make_response_handler(HttpResponse, '0000'),
            request=request, context=context, form=form
        )
        return HttpResponse('0000')
    return call_handler_and_render(
        'BUYSAFE_CHECK_INVALID_HANDLER',
        make_response_handler(HttpResponseBadRequest),
        request=request, context=context, form=form
    )
