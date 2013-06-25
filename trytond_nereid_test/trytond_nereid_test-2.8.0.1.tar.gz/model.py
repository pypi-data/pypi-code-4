# This file is part of Tryton & Nereid. The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.model import ModelSQL, fields


class TestModel(ModelSQL):
    """A Tryton model which uses Pagination which could be used for
    testing."""
    __name__ = "nereid.test.test_model"

    name = fields.Char("Name")
