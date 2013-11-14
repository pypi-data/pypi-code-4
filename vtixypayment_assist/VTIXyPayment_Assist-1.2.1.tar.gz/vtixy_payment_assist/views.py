# coding=utf-8
import hashlib
import logging
from smtplib import SMTPDataError
from time import sleep
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
import requests
import slumber
from slumber.exceptions import HttpClientError

logger = logging.getLogger(__name__)


@csrf_exempt
def confirm(request):
    logger.info("POST Confirmation request %s" % request.POST)
    # Проверяем подлинность данных
    check_string = "".join([request.POST['merchant_id'], request.POST['ordernumber'], request.POST['amount'],
                            request.POST['currency'], request.POST['orderstate']])
    check_string_salt = str(hashlib.md5(settings.VTIXY_ASSIST_SALT).hexdigest()
                            + hashlib.md5(check_string).hexdigest()).upper()
    if str(hashlib.md5(check_string_salt).hexdigest()).upper() != request.POST['checkvalue']:
        # Ошибка шифрования (9) и ошибка расшифровки ключом (6)
        # uppercase(md5(uppercase(md5(SALT) + md5(Х)))),
        logger.info("CRC Error")
        return render_to_response('error.xml', {"firstcode": 9, "secondcode": 6}, mimetype='application/xml')

    # Если пришёл тестовый платёж, а режим запрещён - вернём ошибку
    if request.POST['testmode'] == '1' and not settings.VTIXY_ASSIST_TEST_MODE:
        logger.info("Test payment not allowed!")
        # Подозрение на мошеничество (18) Параметр TestMode (212)
        return render_to_response('error.xml', {"firstcode": 18, "secondcode": 212}, mimetype='application/xml')

    # Проверяем orderstate. Допускаем только 'Delayed', 'Approved', 'PartialApproved', 'PartialDelayed'
    if request.POST['orderstate'] not in ('Delayed', 'Approved', 'PartialApproved', 'PartialDelayed'):
        logger.info("orderstate is not valid!")
        # Возвращаем ок
        return render_to_response('ok.xml',
                                  {"billnumber": request.POST['billnumber'], "packetdate": request.POST['packetdate']},
                                  mimetype='application/xml')

    # Получаем заказ из базы
    api = slumber.API(settings.VTIXY_HOST + "/", auth=(settings.VTIXY_LOGIN, settings.VTIXY_PASSWORD))
    try:
        order = api.orders(request.POST['ordernumber']).get()
    except HttpClientError as e:
        if e.response.status_code == 404:
            # Отсутствует объект (10) заказ (201)
            logger.info("No such order '%s'" % request.POST['ordernumber'])
            return render_to_response('error.xml', {"firstcode": 10, "secondcode": 201}, mimetype='application/xml')
        else:
            # Подождать 3 сек и попробовать ещё раз
            logger.info("PATCH order '%s' failed. Retry after 2 sec..." % request.POST['ordernumber'])
            sleep(3)
            try:
                order = api.orders(request.POST['ordernumber']).get()
            except HttpClientError as e:
                if e.response.status_code == 404:
                    # Отсутствует объект (10) заказ (201)
                    logger.info("No such order '%s'" % request.POST['ordernumber'])
                    return render_to_response('error.xml', {"firstcode": 10, "secondcode": 201}, mimetype='application/xml')
                else:
                    # Внутренняя (2) непредвиденная (1) ошибка
                    logger.info("HttpClientError %s" % e.message)
                    return render_to_response('error.xml', {"firstcode": 2, "secondcode": 1}, mimetype='application/xml')

    # Если уже оплачен - возвращаем ok
    if order['sold']:
        logger.info("Warn: order %s already payed" % request.POST['ordernumber'])
        return render_to_response('ok.xml',
                                  {"billnumber": request.POST['billnumber'], "packetdate": request.POST['packetdate']},
                                  mimetype='application/xml')

    # Если различаются суммы - возвращаем error
    if float(order['price']) != float(request.POST['amount']):
        # Неверное значение параметра (5) amount (108)
        logger.info("Error in amount. Expected '%s', got '%s'" % (str(order['price']), request.POST['amount']))
        return render_to_response('error.xml', {"firstcode": 5, "secondcode": 108}, mimetype='application/xml')

    # Проводим продажу заказа в базе
    try:
        api.orders(request.POST['ordernumber']).patch({"sold": True, "transaction_id": request.POST['billnumber']})
    except HttpClientError as e:
        # Внутренняя (2) непредвиденная (1) ошибка
        logger.info("HttpClientError %s" % e.message)
        return render_to_response('error.xml', {"firstcode": 2, "secondcode": 1}, mimetype='application/xml')

    # Подтверждаем операцию в ASSIST
    post_vars = {"Billnumber": request.POST['billnumber'], "Merchant_ID": request.POST['merchant_id'],
                 "Login": settings.VTIXY_ASSIST_LOGIN, "Password": settings.VTIXY_ASSIST_PASSWORD}
    resp = requests.post(settings.VTIXY_ASSIST_CONFIRM_URL, data=post_vars)

    # Если подтверждение неудчно - возвращаем ошибку
    if resp.status_code != 200:
        # Ошибка (1) операции подтверждения (307)
        logger.info("Payment confirmation error %s" % resp.text)
        return render_to_response('error.xml', {"firstcode": 1, "secondcode": 307}, mimetype='application/xml')

    # Отправляем письмо клиенту
    plaintext = get_template("mail_ticket_to_client.txt")
    html = get_template("mail_ticket_to_client.html")
    mail_context = Context({
        "name": request.POST['firstname'] + " " + request.POST['lastname'],
        "link": settings.VTIXY_MAIL_TICKETS_URL % (request.POST['ordernumber'],
                                                   request.POST['billnumber'].split(".")[0], ),
        "order": request.POST['ordernumber'],
        "price": request.POST['orderamount'],
        "currency": request.POST['ordercurrency'],
    })
    text_content = plaintext.render(mail_context)
    html_content = html.render(mail_context)
    msg = EmailMultiAlternatives(settings.VTIXY_MAIL_SUBJECT_PREFIX + request.POST['ordernumber'],
                                 text_content,
                                 settings.VTIXY_MAIL_FROM_NAME + "<" + settings.VTIXY_MAIL_FROM_EMAIL + ">",
                                 [request.POST['email'], ])
    msg.attach_alternative(html_content, "text/html")
    try:
        msg.send()
    except SMTPDataError as e:
        logger.info("Couldn't send email. SMTPDataError %s" % e.message)


    logger.info("Confirmation ok")
    return render_to_response('ok.xml',
                              {"billnumber": request.POST['billnumber'], "packetdate": request.POST['packetdate']},
                              mimetype='application/xml')


@csrf_exempt
def check(request, order_id):
    # Возвращает NEW, CONFIRMED, PENDED, TIMEOUT, CANCELED, DECLINED или UNKNOWN
    #

    #Отправляем запрос в ASSIST
    post_vars = {"Ordernumber": order_id, "Merchant_ID": settings.VTIXY_ASSIST_MERCHANT_ID,
                 "Login": settings.VTIXY_ASSIST_LOGIN, "Password": settings.VTIXY_ASSIST_PASSWORD,
                 "Format": 1, "Startday": 1}   # Format CSV (1)
    resp = requests.post(settings.VTIXY_ASSIST_CHECK_URL, data=post_vars)

    # Если произошла какая-то ошибка - её и возвращаем
    if resp.status_code != 200:
        return HttpResponse(status=500)

    # Парсим строку
    resp_csv = resp.content.splitlines()[0]
    resp_array = resp_csv.split(";")

    # Если вернул ошибку, то обрбатываем параметры и возвращаем 404
    if resp_array[0] == 'error':
        return HttpResponse('{"order_id" : "' + order_id + '", "state": "NOT FOUND"}', content_type='application/json',
                            status=404)
    else:
        resp_csv_vals = resp.content.splitlines()[1]
        resp_csv_vals_array = resp_csv_vals.split(";")
        resp_dict = dict(zip(resp_array, resp_csv_vals_array))

        return_var = "UNKNOWN"
        if resp_dict['orderstate'] == 'Approved':
            return_var = "CONFIRMED"
        if resp_dict['orderstate'] == 'Delayed':
            return_var = "PENDED"
        if resp_dict['orderstate'] == 'Timeout':
            return_var = "TIMEOUT"
        if resp_dict['orderstate'] == 'In Process':
            return_var = "NEW"
        if resp_dict['orderstate'] == 'Canceled':
            return_var = "CANCELED"
        if resp_dict['orderstate'] == 'Declined':
            return_var = "DECLINED"

    return HttpResponse('{"order_id" : "' + order_id + '", "state": "' + return_var + '"}',
                        content_type='application/json')