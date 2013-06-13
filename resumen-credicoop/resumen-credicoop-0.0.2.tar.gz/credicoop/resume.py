# -*- coding: utf-8 -*-

class Resumen(object):

    #fecha = ''
    saldo_anterior = ''
    saldo = ''
    fecha_saldo = ''
    items = []

    def __repr__(self):
        return u"Resumen al {fecha}".format(fecha=self.fecha_saldo)

    def __str__(self):
        return u"Resumen()"

    def to_dict(self):
        resumen_dict = {}
        resumen_dict['saldo_anterior'] = self.saldo_anterior
        resumen_dict['saldo'] = self.saldo
        resumen_dict['fecha_saldo'] = self.fecha_saldo

        detalle= []

        for item in self.items:
            item_dict = {}
            item_dict['fecha'] = item.fecha
            item_dict['comprobante'] = item.comprobante
            item_dict['descripcion'] = item.descripcion
            item_dict['debito'] = item.debito
            item_dict['credito'] = item.credito
            item_dict['saldo'] = item.saldo

            detalle.append(item_dict)

        resumen_dict['detalle'] = detalle

        return resumen_dict


class ResumenDetalle(object):

    fecha = ''
    comprobante = ''
    descripcion = ''
    debito = ''
    credito = ''
    saldo = ''

    def __repr__(self):
        return u"< {descripcion} >".format(descripcion=self.descripcion)

    def __str__(self):
        return "ResumenDetalle()"


