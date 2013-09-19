# coding=utf-8
import StringIO
import copy
from datetime import datetime
import os
from django.conf import settings
from django.http import HttpResponse, Http404
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
from reportlab.pdfbase import ttfonts, pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code39, code128
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.lib.units import mm
from pyPdf import PdfFileReader, PdfFileWriter
import slumber
from slumber.exceptions import HttpClientError


def pdf(request, order_id):

    # Если не передан transaction_id - ошибка, не найдено
    if not request.GET.get('transaction_id', None):
            raise Http404

    # Получаем набор билетов
    api = slumber.API(settings.VTIXY_HOST + "/", auth=(settings.VTIXY_LOGIN, settings.VTIXY_PASSWORD))
    try:
        order = api.orders(order_id).get()
    except HttpClientError as e:
        if e.response.status_code == 404:
            raise Http404
        else:
            return HttpResponse(content=e.message, status=500)

    # Если заказ не продан - не найден
    if not order['sold']:
        raise Http404

    # Если transaction_id не совпадают - не найден
    transaction_parts = order['transaction_id'].split('.')
    if request.GET['transaction_id'] != transaction_parts[0]:
        raise Http404

    tickets = order['tickets']

    # Читаем шаблон билета
    template = PdfFileReader(file(settings.VTIXY_TEMPLATE, 'rb'))
    template_page = template.getPage(0)

    # Создаем выходной файл
    output_pdf = PdfFileWriter()

    # Создаём страницы с билетами
    string_io = StringIO.StringIO()
    p = canvas.Canvas(string_io)

    # Подгружаем шрифт (для русских букв)
    fontUbuntuL = ttfonts.TTFont('Ubuntu-L', os.path.join(os.path.dirname(__file__), 'fonts/Ubuntu-L.ttf'))
    fontUbuntuM = ttfonts.TTFont('Ubuntu-M', os.path.join(os.path.dirname(__file__), 'fonts/Ubuntu-M.ttf'))
    fontUbuntuLI = ttfonts.TTFont('Ubuntu-LI', os.path.join(os.path.dirname(__file__), 'fonts/Ubuntu-LI.ttf'))
    fontUbuntuMI = ttfonts.TTFont('Ubuntu-MI', os.path.join(os.path.dirname(__file__), 'fonts/Ubuntu-MI.ttf'))
    pdfmetrics.registerFont(fontUbuntuL)
    pdfmetrics.registerFont(fontUbuntuM)
    pdfmetrics.registerFont(fontUbuntuLI)
    pdfmetrics.registerFont(fontUbuntuMI)

    for ticket in tickets:

        for item in settings.VTIXY_TEMPLATE_LAYOUT:

            # Меняем стиль шрифта, если задан
            if not item.get('style', None):
                style = "n"
            else:
                style = item['style']

            if not item.get('size', None):
                size = 12
            else:
                size = item['size']

            if style == "n":
                p.setFont("Ubuntu-L", size)
            if style == "b":
                p.setFont("Ubuntu-M", size)
            if style == "ni":
                p.setFont("Ubuntu-LI", size)
            if style == "bi":
                p.setFont("Ubuntu-MI", size)

            if item['name'] == "venue":
                p.drawString(item['x'], item['y'], ticket['venue'])

            if item['name'] == "show":
                p.drawString(item['x'], item['y'], ticket['show'])

            if item['name'] == "event":
                parsed_date = datetime.strptime(ticket['event'], "%Y-%m-%dT%H:%M:%S")
                p.drawString(item['x'], item['y'], parsed_date.strftime("%d.%m.%Y %H:%M"))

            if item['name'] == "order":
                p.drawString(item['x'], item['y'], u"Заказ: " + unicode(order['id']))

            if item['name'] == "barcode39":
                barcode = code39.Standard39(str(ticket['barcode']),
                                            barWidth=item['barWidth']*mm, barHeight=item['barHeight']*mm)
                barcode.drawOn(p, item['x'], item['y'])

            if item['name'] == "barcode128":
                barcode = code128.Code128(str(ticket['barcode']),
                                          barWidth=item['barWidth']*mm, barHeight=item['barHeight']*mm)
                barcode.drawOn(p, item['x'], item['y'])

            if item['name'] == "barcode_string":
                p.drawString(item['x'], item['y'],  str(ticket['barcode']))

            if item['name'] == "place":
                p.drawString(item['x'], item['y'],  u"Место: " + ticket['place'])

            if item['name'] == "price":
                p.drawString(item['x'], item['y'], u"Цена: " + str(ticket['price']) + u" руб.")

        p.showPage()

    p.save()

    # Читаем созданный файл с билетами
    string_io.seek(0)
    tickets_pdf = PdfFileReader(string_io)

    # Ко всем билетам применяем шаблон
    for page in tickets_pdf.pages:
        template_page_clone = copy.copy(template_page)
        template_page_clone.mergePage(page)
        output_pdf.addPage(template_page_clone)

    # Пишем содержимое выходного файла в буфер
    output_pdf.write(string_io)

    # Создаём ответ pdf из буфера
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="tickets' + str(order_id) + '.pdf"'
    response.write(string_io.getvalue())

    return response


def mobile(request, order_id):

    # Если не передан transaction_id - ошибка, не найдено
    if not request.GET.get('transaction_id', None):
            raise Http404

    # Получаем набор билетов
    api = slumber.API(settings.VTIXY_HOST + "/", auth=(settings.VTIXY_LOGIN, settings.VTIXY_PASSWORD))
    try:
        order = api.orders(order_id).get()
    except HttpClientError as e:
        if e.response.status_code == 404:
            raise Http404
        else:
            return HttpResponse(content=e.message, status=500)

    # Если заказ не продан - не найден
    if not order['sold']:
        raise Http404

    # Если transaction_id не совпадают - не найден
    transaction_parts = order['transaction_id'].split('.')
    if request.GET['transaction_id'] != transaction_parts[0]:
        raise Http404

    tickets = order['tickets']

     # Создаём ответ
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="tickets' + str(order_id) + '_mob.pdf"'

    # Создаём страницы с билетами
    p = canvas.Canvas(response)

    # Подгружаем шрифт (для русских букв)
    fontUbuntu = ttfonts.TTFont('Ubuntu', os.path.join(os.path.dirname(__file__), 'fonts/Ubuntu-R.ttf'))
    pdfmetrics.registerFont(fontUbuntu)

    for ticket in tickets:

        qrw = QrCodeWidget(str(ticket['barcode']))
        b = qrw.getBounds()
        w = b[2]-b[0]
        h = b[3]-b[1]
        d = Drawing(400, 400, transform=[400./w, 0, 0, 400./h, 0, 0])
        d.add(qrw)
        renderPDF.draw(d, p, 80, 400)

        p.setFont("Ubuntu", 12)
        p.drawString(130, 400, u"Заказ: " + str(order['id']))

        p.drawString(130, 385, u"Билет: " + ticket['barcode'])

        p.drawString(130, 370, ticket['venue'])

        parsed_date = datetime.strptime(ticket['event'], "%Y-%m-%dT%H:%M:%S")
        p.drawString(130, 355, '"' + ticket['show'] + u'" в ' + parsed_date.strftime("%d.%m.%Y %H:%M"))

        p.drawString(130, 340, ticket['place'])

        p.showPage()

    p.save()

    return response