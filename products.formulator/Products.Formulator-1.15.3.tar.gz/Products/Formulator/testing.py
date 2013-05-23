# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt


from infrae.wsgi.testing import BrowserLayer, TestRequest
import Products.Formulator


class FormulatorLayer(BrowserLayer):
    default_products = BrowserLayer.default_products + [
        'Formulator']
    default_users = {
        'manager': ['Manager'],
        }


FunctionalLayer = FormulatorLayer(
    Products.Formulator, zcml_file='configure.zcml')

__all__ = ['FunctionalLayer', 'TestRequest']
