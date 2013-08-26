# -*- coding: utf-8 -*-

from pybill.lib import ACCURACY, PBD_1_0
from pybill.lib.entities.accounting_docs import AccItem


class AbstractAccDocTest:
    """
    Base class factorizing the common behaviour for the tests of the various
    sort of bills.

    We should not define test methods on this object as it doesn't inherit from
    ``TestCase``... but it is so much simpler to do this and Python is a nice
    dynamic language that doesn't complain about this.

    :ivar acc_doc: Accounting object that will be tested. This object is
                   actually built by the child classes before each test in
                   the ``setUp`` method.
    :type acc_doc: `pybill.lib.entities.accounting_docs.GenericAccountingDoc`
    """
    def __init__(self):
        """
        Just defines the ``acc_doc`` attribute without setting it.
        """
        self.acc_doc = None

    def build_vat_example(self):
        """
        Creates an accounting document containing items with various VAT
        rates.
        """
        item = AccItem()
        item.quantity = 13.0
        item.unit_price = 14.0 
        self.acc_doc.acc_items.append(item)
        item = AccItem()
        item.quantity = 13.0
        item.unit_price = 17.0 
        item.vat_rate = 1.0
        self.acc_doc.acc_items.append(item)
        for i in range(3):
            item = AccItem()
            item.quantity = 5.0
            item.unit_price = 7.0 
            item.vat_rate = 1.0+(20.0-i*10.0)
            self.acc_doc.acc_items.append(item)

    def build_standard_example(self, with_holdbacks=False):
        """
        Creates an accounting document containing several items.

        :parameter with_holdbacks: When set to ``True``, holdbacks are
                                   inserted in the items.
        :type with_holdbacks: bool
        """
        item = AccItem()
        item.quantity = 17.0
        item.unit_price = 13.0
        if with_holdbacks:
            item.holdback_rate = 5.0
            item.holdback_on_vat = True
        self.acc_doc.acc_items.append(item)
        for i in range(3):
            item = AccItem()
            item.quantity = 5.0*(i+1)
            item.unit_price = 7.0*(i+1)
            item.vat_rate = 19.6
            if with_holdbacks and i in [1,2]:
                item.holdback_rate = 5.0
            if with_holdbacks and i in [0,1]:
                item.holdback_on_vat = True
            self.acc_doc.acc_items.append(item)

    def build_rounding_example(self):
        """
        Creates an accounting document containing several items. The totals
        of these items are rounded to ``ACCURACY`` digits.
        """
        for i in range(4):
            item = AccItem()
            item.quantity = 5.009
            item.unit_price = 7.0
            item.vat_rate = 19.6
            item.holdback_rate = 5.0
            item.holdback_on_vat = True
            self.acc_doc.acc_items.append(item)

    def test_empty_object(self):
        """
        Tests an empty object contains nothing and has totals of 0.0
        """
        self.assertEqual(self.acc_doc.cfg_data, None)
        self.assertEqual(self.acc_doc.account_numbers, {})
        self.assertEqual(self.acc_doc.origin_format, PBD_1_0)
        self.assertEqual(self.acc_doc.acc_items, [])
        self.assertEqual(self.acc_doc.get_all_vat_rates(), set())
        self.assertEqual(self.acc_doc.get_vat_amount_for_rate(19.6),
                          round(0.0, ACCURACY))
        self.assertEqual(self.acc_doc.get_price_total(),
                          round(0.0, ACCURACY))
        self.assertEqual(self.acc_doc.get_holdback_amount(),
                          round(0.0, ACCURACY))
        self.assertEqual(self.acc_doc.get_holdback_vat_amount(),
                          round(0.0, ACCURACY))
        self.assertEqual(self.acc_doc.get_including_taxes_total(),
                          round(0.0, ACCURACY))
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback_free(),
                          round(0.0, ACCURACY))
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback(),
                          round(0.0, ACCURACY))
        self.assertEqual(self.acc_doc.get_to_be_paid_vat(),
                          round(0.0, ACCURACY))
        self.assertEqual(self.acc_doc.get_to_be_paid(),
                          round(0.0, ACCURACY))

    def test_has_vat_rates_with_vat_rates(self):
        """
        Tests the method saying if the document contains VAT rates when VAT
        rates are defined.
        """
        self.build_standard_example()
        self.assertEqual(self.acc_doc.has_vat_rates(), True)

    def test_has_vat_rates_without_vat_rate(self):
        """
        Tests the method saying if the document contains VAT rates when no VAT
        rate is defined.
        """
        self.build_standard_example()
        for item in self.acc_doc.acc_items:
            item.vat_rate = None
        self.assertEqual(self.acc_doc.has_vat_rates(), False)
        
    def test_has_holdbacks_with_holdbacks(self):
        """
        Tests the method saying if the document contains holdbacks when
        holdback rates are defined on some items.
        """
        self.build_standard_example()
        self.acc_doc.acc_items[1].holdback_rate = 5.0
        self.assertEqual(self.acc_doc.has_holdbacks(), True)

    def test_has_holdbacks_without_holdback(self):
        """
        Tests the method saying if the document contains holdbacks when no
        holdback rate is defined.
        """
        self.build_standard_example()
        self.assertEqual(self.acc_doc.has_holdbacks(), False)

    def test_has_vat_holdbacks_with_vat_holdbacks(self):
        """
        Tests the method saying if the document contains vat holdbacks when
        holdback rates are defined on some items and some of these holdbacks
        are applied on VAT.
        """
        self.build_standard_example()
        self.acc_doc.acc_items[0].holdback_rate = 10.0
        self.acc_doc.acc_items[1].holdback_rate = 5.0
        self.acc_doc.acc_items[1].holdback_on_vat = True
        self.assertEqual(self.acc_doc.has_vat_holdbacks(), True)

    def test_has_vat_holdbacks_with_no_vat_holdbacks(self):
        """
        Tests the method saying if the document contains vat holdbacks when
        holdback rates are defined on some items but these holdbacks are not
        applied on VAT.
        """
        self.build_standard_example()
        self.acc_doc.acc_items[0].holdback_rate = 10.0
        self.acc_doc.acc_items[1].holdback_rate = 5.0
        self.acc_doc.acc_items[1].holdback_on_vat = False
        self.acc_doc.acc_items[2].holdback_on_vat = True
        self.assertEqual(self.acc_doc.has_vat_holdbacks(), False)

    def test_has_vat_holdbacks_without_vat_rates(self):
        """
        Tests the method saying if the document contains vat holdbacks when
        no VAT rates are defined.
        """
        self.build_standard_example()
        for item in self.acc_doc.acc_items:
            item.vat_rate = None
        self.acc_doc.acc_items[1].holdback_rate = 5.0
        self.acc_doc.acc_items[1].holdback_on_vat = True
        self.assertEqual(self.acc_doc.has_vat_holdbacks(), False)

    def test_has_vat_holdbacks_without_holdback(self):
        """
        Tests the method saying if the document contains holdbacks when no
        holdback rate is defined.
        """
        self.build_standard_example()
        self.assertEqual(self.acc_doc.has_vat_holdbacks(), False)

    def test_get_all_vat_rates(self):
        """
        Tests the method giving the different VAT rates used in the document.
        """
        self.build_vat_example()        
        self.assertEqual(self.acc_doc.get_all_vat_rates(),
                          set([1.0,11.0,21.0]))

    def test_get_no_vat_rate(self):
        """
        Tests the method giving the different VAT rates used in the document
        when no vat rate is defined.
        """
        self.build_standard_example()
        for item in self.acc_doc.acc_items:
            item.vat_rate = None
        self.assertEqual(self.acc_doc.get_all_vat_rates(), set())

    def test_get_vat_amount_for_rate(self):
        """
        Tests the method giving the VAT amount for a given VAT rate.
        """
        self.build_vat_example()
        self.assertEqual(self.acc_doc.get_vat_amount_for_rate(1.0),
                          round(2.56, ACCURACY))
        self.assertEqual(self.acc_doc.get_vat_amount_for_rate(11.0),
                          round(3.85, ACCURACY))
        self.assertEqual(self.acc_doc.get_vat_amount_for_rate(21.0),
                          round(7.35, ACCURACY))
        self.assertEqual(self.acc_doc.get_vat_amount_for_rate(19.6),
                          round(0.0, ACCURACY))

    def test_get_price_total(self):
        """
        Tests the computation of the tax free total.
        """
        self.build_standard_example()
        self.assertEqual(self.acc_doc.get_price_total(),
                          round(711.0, ACCURACY))

    def test_get_including_taxes_total(self):
        """
        Tests the computation of the including taxes total.
        """
        self.build_standard_example()
        self.assertEqual(self.acc_doc.get_including_taxes_total(),
                          round(807.04, ACCURACY))

    def test_get_holdback_amount(self):
        """
        Tests the computation of the amount of holdbacks.
        """
        self.build_standard_example()
        self.assertEqual(self.acc_doc.get_holdback_amount(),
                          round(0.0, ACCURACY))

    def test_get_holdback_vat_amount(self):
        """
        Tests the computation of the amount of holdbacks on vat.
        """
        self.build_standard_example()
        self.assertEqual(self.acc_doc.get_holdback_vat_amount(),
                          round(0.0, ACCURACY))

    def test_get_total_without_holdback_to_be_paid(self):
        """
        Tests the computation of the total without holdbacks to be paid.
        """
        self.build_standard_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback_free(),
                          round(807.04, ACCURACY))

    def test_get_total_holdback_to_be_paid(self):
        """
        Tests the computation of the total of holdbacks to be paid.
        """
        self.build_standard_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback(),
                          round(0.0, ACCURACY))

    def test_get_total_vat_to_be_paid(self):
        """
        Tests the computation of the total of VAT to be paid.
        """
        self.build_standard_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_vat(),
                          round(96.04, ACCURACY))

    def test_get_total_to_be_paid(self):
        """
        Tests the computation of the total to be paid.
        """
        self.build_standard_example()
        self.assertEqual(self.acc_doc.get_to_be_paid(),
                          round(807.04, ACCURACY))

    def test_get_vat_amount_for_rate_with_holdback(self):
        """
        Tests the method giving the VAT amount for a given VAT rate when
        holdbacks are defined on some items.
        """
        self.build_vat_example()
        for i in range(len(self.acc_doc.acc_items)):
            item = self.acc_doc.acc_items[i]
            if i in [0,1,3]:
                item.holdback_rate = 5.0
            if i in [0,1,2]:
                item.holdback_on_vat = True
        self.assertEqual(self.acc_doc.get_vat_amount_for_rate(1.0),
                          round(2.56, ACCURACY))
        self.assertEqual(self.acc_doc.get_vat_amount_for_rate(11.0),
                          round(3.85, ACCURACY))
        self.assertEqual(self.acc_doc.get_vat_amount_for_rate(21.0),
                          round(7.35, ACCURACY))
        self.assertEqual(self.acc_doc.get_vat_amount_for_rate(19.6),
                          round(0.0, ACCURACY))

    def test_get_price_total_with_holdback(self):
        """
        Tests the computation of the tax free total when holdbacks are defined
        on some items.
        """
        self.build_standard_example(with_holdbacks=True)
        self.assertEqual(self.acc_doc.get_price_total(),
                          round(711.0, ACCURACY))

    def test_get_including_taxes_total_with_holdback(self):
        """
        Tests the computation of the including taxes total when holdbacks are
        defined on some items.
        """
        self.build_standard_example(with_holdbacks=True)
        self.assertEqual(self.acc_doc.get_including_taxes_total(),
                          round(807.04, ACCURACY))

    def test_get_holdback_amount_with_holdback(self):
        """
        Tests the computation of the amount of holdbacks when holdbacks are
        defined on some items.
        """
        self.build_standard_example(with_holdbacks=True)
        self.assertEqual(self.acc_doc.get_holdback_amount(),
                          round(33.80, ACCURACY))

    def test_get_holdback_vat_amount_with_holdback(self):
        """
        Tests the computation of the amount of holdbacks on vat when holdbacks
        are defined on some items.
        """
        self.build_standard_example(with_holdbacks=True)
        self.assertEqual(self.acc_doc.get_holdback_vat_amount(),
                          round(1.372, ACCURACY))

    def test_get_total_without_holdback_to_be_paid_with_holdback(self):
        """
        Tests the computation of the total without holdbacks to be paid when
        holdbacks are defined on some items.
        """
        self.build_standard_example(with_holdbacks=True)
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback_free(),
                          round(771.868, ACCURACY))

    def test_get_total_holdback_to_be_paid_with_holdback(self):
        """
        Tests the computation of the total of holdbacks to be paid when
        holdbacks are defined on some items.
        """
        self.build_standard_example(with_holdbacks=True)
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback(),
                          round(35.172, ACCURACY))

    def test_get_total_vat_to_be_paid_with_holdback(self):
        """
        Tests the computation of the total of VAT to be paid when holdbacks are
        defined on some items.
        """
        self.build_standard_example(with_holdbacks=True)
        self.assertEqual(self.acc_doc.get_to_be_paid_vat(),
                          round(96.04, ACCURACY))

    def test_get_total_to_be_paid_with_holdback(self):
        """
        Tests the computation of the total to be paid when holdbacks are
        defined on some items.
        """
        self.build_standard_example(with_holdbacks=True)
        self.assertEqual(self.acc_doc.get_to_be_paid(),
                          round(807.04, ACCURACY))

    def test_get_vat_amount_for_rate_when_rounding(self):
        """
        Tests the method giving the VAT amount for a given VAT rate when
        rounding to ``ACCURACY`` is done.
        """
        self.build_rounding_example()
        self.assertEqual(self.acc_doc.get_vat_amount_for_rate(19.6),
                          round(27.44, ACCURACY))

    def test_get_price_total_when_rounding(self):
        """
        Tests the computation of the tax free total when rounding to
        ``ACCURACY`` is done.
        """
        self.build_rounding_example()
        self.assertEqual(self.acc_doc.get_price_total(),
                          round(140.00, ACCURACY))

    def test_get_including_taxes_total_when_rounding(self):
        """
        Tests the computation of the including taxes total when rounding to
        ``ACCURACY`` is done.
        """
        self.build_rounding_example()
        self.assertEqual(self.acc_doc.get_including_taxes_total(),
                          round(167.44, ACCURACY))

    def test_get_holdback_amount_when_rounding(self):
        """
        Tests the computation of the amount of holdbacks when rounding to
        ``ACCURACY`` is done.
        """
        self.build_rounding_example()
        self.assertEqual(self.acc_doc.get_holdback_amount(),
                          round(7.0, ACCURACY))

    def test_get_holdback_vat_amount_when_rounding(self):
        """
        Tests the computation of the amount of holdbacks on vat when rounding
        to ``ACCURACY`` is done.
        """
        self.build_rounding_example()
        self.assertEqual(self.acc_doc.get_holdback_vat_amount(),
                          round(1.36, ACCURACY))

    def test_get_total_without_holdback_to_be_paid_when_rounding(self):
        """
        Tests the computation of the total without holdbacks to be paid when
        rounding to ``ACCURACY`` is done.
        """
        self.build_rounding_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback_free(),
                          round(159.08, ACCURACY))

    def test_get_total_holdback_to_be_paid_when_rounding(self):
        """
        Tests the computation of the total of holdbacks to be paid when
        rounding to ``ACCURACY`` is done.
        """
        self.build_rounding_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_holdback(),
                          round(8.36, ACCURACY))

    def test_get_total_vat_to_be_paid_when_rounding(self):
        """
        Tests the computation of the total of VAT to be paid when rounding to
        ``ACCURACY`` is done.
        """
        self.build_rounding_example()
        self.assertEqual(self.acc_doc.get_to_be_paid_vat(),
                          round(27.44, ACCURACY))

    def test_get_total_to_be_paid_when_rounding(self):
        """
        Tests the computation of the total to be paid when rounding to
        ``ACCURACY`` is done.
        """
        self.build_rounding_example()
        self.assertEqual(self.acc_doc.get_to_be_paid(),
                          round(167.44, ACCURACY))
