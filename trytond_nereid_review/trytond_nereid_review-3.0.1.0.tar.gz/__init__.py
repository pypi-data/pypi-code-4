# -*- coding: utf-8 -*-
"""
    __init__

    Nereid Reviews

    :copyright: (c) 2012-2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool
from review import NereidReview


def register():
    Pool.register(
        NereidReview,
        type_="model", module="nereid_review"
    )
