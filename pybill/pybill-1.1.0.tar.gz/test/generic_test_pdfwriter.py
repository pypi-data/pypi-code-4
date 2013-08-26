# -*- coding: utf-8 -*-

from StringIO import StringIO
import reportlab 

from pybill.lib.entities.addresses import PersonAddress, OrganisationAddress
from pybill.lib.entities.accounting_docs import AccItem
from pybill.lib.config.entities import ConfigData

# When set to True, PDF results are written on the disk in a subdirectory of
# data directory. This is the way to check manually the PDF produced by the
# tests.
WRITE_RESULTS_ON_DISK = False

REFERENCE_DIR = ("reference_pdfs/reportlab_%s"
                 % reportlab.Version.replace(".", "_"))


class PDFWriterGenericTest :
    """
    Abstract class containing various useful methods for testing the PDF
    generation for an accounting document and factorizing some common tests.

    We should not define test methods on this object as it doesn't inherit from
    ``TestCase``... but it is so much simpler to do this and Python is a nice
    dynamic language that doesn't complain about this.

    :ivar writer: PDFWriter object that will be built by the ``setUp``
                  method before each test and that will be used to transform
                  the accounting document in PDF.
    :type writer: `pybill.lib.pdfwriters.PDFWriter`
    
    :ivar acc_doc: Accounting document that will be built by the ``setUp``
                   method before each test and that will be transformed in
                   PDF in each test.
    :type acc_doc: `pybill.lib.entities.accounting_docs.GenericAccountingDoc`

    :ivar entity_name: Name of the accounting entity that is tested. This name
                       is used to generate the filenames of the PDF (output PDF
                       and reference PDF). It will be defined in the child
                       classes by the ``setUp`` method, run before each test.
                       Can be "bill", "claimform", "debit", "downpayment",
                       or "proforma".
    :type entity_name: str
    """
    def __init__(self) :
        self.writer = None
        self.acc_doc = None
        self.entity_name = ""
        if self.__class__ is PDFWriterGenericTest :
            raise NotImplementedError()

    def _mask_pdf_variable_parts(self, pdf_str):
        """
        This method deletes the variable parts in a PDF string. Hence, in a PDF
        some keyword contain the date of creation, the checksum, etc. In order
        to compare a PDF with a PDF that was previously manually validated, it
        is interesting to delete these parts.

        Currently, this method deletes:

        - the literal strings after ``CreationDate`` and ``ModDate`` keywords,

        - the hexadecimal string after ``CheckSum`` keyword,

        - the trailer of the PDF document (that contains an unique identifier
          for the document).

        Please note that this method doesn't modify the initial PDF string but
        returns a modified copy of this string.

        :parameter pdf_str: Unicode string containing the whole PDF document.
                            This string is copied and some parts of the PDF
                            document are masked.
        :type pdf_str: unicode

        :returns: Unicode string containing an extract of the initial PDF
                  document where some parts were deleted. This string is a copy
                  of the initial string. This string doesn't contain a valid
                  PDF document.
        :rtype: unicode
        """
        masked_str = pdf_str[:]
        # Masks creation date, modification date and checksum.
        for keyword, start_tag, end_tag in [("CreationDate", "(", ")"),
                                            ("ModDate", "(", ")"),
                                            ("CheckSum", "<", ">")]:
            while (True):
                try:
                    kw_start = masked_str.index("/%s" %keyword)
                except ValueError:
                    break
                # Just to make sure we don't go too far in case of problem.
                dict_end = masked_str.find(">>", kw_start)
                val_start = min(masked_str.index(start_tag, kw_start),
                                dict_end)
                val_end = min(masked_str.index(end_tag, val_start),
                              dict_end)
                masked_str = masked_str[:kw_start] + masked_str[val_end+1:]
        # Masks document trailer.
        start = masked_str.rfind("trailer") + 7
        end = masked_str.find("startxref", start)
        masked_str = masked_str[:start] + "\n" + masked_str[end:]
        return masked_str
    
    def _run_pdf_test(self, pdf_filename):
        """
        Runs the common part of a PDF test: builds the PDF with ``self.writer``
        from ``self.acc_doc``. If ``WRITE_RESULTS_ON_DISK`` constant is set to
        ``True``, the resulting PDF will be written in a subdirectory of the
        data directory.

        The resulting PDF is compared with a reference PDF that has been
        manually validated. Please note that this comparison is really basic:
        two document might be different but have the same rendering in a PDF
        viewer. Here, we just check that the two documents are strictly
        identical. However, as PDF document have some variable parts (date of
        creation, etc.), we mask these parts before the actual comparison.

        Please be aware that the PDF documents are stored in strings (that are
        copied for doing the masking). Therefore, it is unwise to test large
        PDF documents.

        :parameter pdf_filename: Name of the PDF files: the output PDF that
                                 would be written in ``output_pdfs`` data
                                 subdirectory if ``WRITE_RESULTS_ON_DISK``
                                 constant is set, and the reference PDF that
                                 is read from ``reference_pdfs`` data
                                 subdirectory.
        :type pdf_filename: str
        """
        # Uses the reportlab `platypus` ``BaseDocTemplate`` sympathy to pass
        # it a string stream instead of a filename.
        output_pdf = StringIO()
        self.writer.write(self.acc_doc, output_pdf)
        output_pdf.flush()
        # Writes the resulting PDF on the disk if wanted.
        if WRITE_RESULTS_ON_DISK:
            output_file = open(self.datapath("output_pdfs/%s" % pdf_filename),
                               'w')
            output_file.write(output_pdf.getvalue())
            output_file.close()
        # Tries to load the reference PDF.
        try:
            ref_pdf = open(self.datapath("%s/%s"
                                         % (REFERENCE_DIR, pdf_filename)),
                           'r').read()
        except IOError:
            ref_pdf = ""
        # Masks the variable parts in the PDFs and compares them
        out = self._mask_pdf_variable_parts(output_pdf.getvalue())
        ref = self._mask_pdf_variable_parts(ref_pdf)
        self.assertEqual(out, ref)

    def _fill_acc_doc_metadata(self, acc_doc) :
        """
        Fills the metadata for ``acc_doc`` accounting document.

        :parameter acc_doc: Accounting document whose common metadata fields
                            will be filled. This object is modified by this
                            method.
        :type acc_doc:
            `pybill.lib.entities.accounting_docs.GenericAccountingDoc`
        """
        acc_doc.doc_ref = u"document reference"
        acc_doc.place = u"place"
        acc_doc.date = u"date"
        acc_doc.other_infos = {u"keyword1": u"value1",
                               u"keyword2": u"value2"}

    def _build_person_address(self, code) :
        """
        Builds an ``PersonAddress`` and fills it with data.

        :parameter code: String prefix that will be added in all the fields
                         of the address and that eases the future checks.
        :type code: unicode

        :returns: A ``PersonAddress`` filled with data.
        :rtype: `pybill.lib.entities.addresses.PersonAddress`
        """
        addr = PersonAddress()
        addr.honorific = u"%s_hon" % code
        addr.firstname = u"%s_firstname" % code
        addr.other_name = u"%s_oth" % code
        addr.surname = u"%s_surname" % code
        addr.lineage = u"%s_lin" % code
        addr.streets.append(u"%s_street_1" % code)
        addr.streets.append(u"%s_street_2" % code)
        addr.post_box = u"%s_pb" % code
        addr.post_code = u"%s_pcode" % code
        addr.city = u"%s_city" % code
        addr.state = u"%s_state" % code
        addr.country = u"%s_country" % code
        addr.phone = u"%s_phone" % code
        addr.fax = u"%s_fax" % code
        addr.email = u"%s_email" % code
        addr.web = u"%s_web" % code
        # affiliation
        addr.organisation = self._build_organisation_address(u"%s_affil" \
                                                             % code)
        return addr

    def _build_organisation_address(self, code) :
        """
        Builds an ``OrganisationAddress`` and fills it with data.

        :parameter code: String prefix that will be added in all the fields
                         of the address and that eases the future checks.
        :type code: unicode

        :returns: An ``OrganisationAddress`` filled with data.
        :rtype: `pybill.lib.entities.addresses.OrganisationAddress`
        """
        addr = OrganisationAddress()
        addr.name = u"%s_name" % code
        addr.job_titles.append(u"%s_job_title_1" % code)
        addr.job_titles.append(u"%s_job_title_2" % code)
        addr.divisions.append(u"%s_division_1" % code)
        addr.divisions.append(u"%s_division_2" % code)
        addr.streets.append(u"%s_street_1" % code)
        addr.streets.append(u"%s_street_2" % code)
        addr.post_box = u"%s_pb" % code
        addr.post_code = u"%s_pcode" % code
        addr.city = u"%s_city" % code
        addr.state = u"%s_state" % code
        addr.country = u"%s_country" % code
        addr.phone = u"%s_phone" % code
        addr.fax = u"%s_fax" % code
        addr.email = u"%s_email" % code
        addr.web = u"%s_web" % code
        return addr

    def _build_acc_items_list(self, length) :
        """
        Builds an accounting items list of length ``length``, filled with
        different ``AccItem`` objects.

        :parameter length: Length of the list of accounting items to be built.
        :type length: int
        
        :returns: A list of ``AccItem`` objects whose length is ``length``.
        :rtype: list
        """
        acclist = []
        for i in range(length):
            it = AccItem()
            it.quantity = float(i+1)
            it.title = u"Element %d" % (i+1)
            it.details.append(u"detailed description %d.1" % (i+1))
            it.details.append(u"detailed description %d.2" % (i+1))
            it.unit_price = float(10*(i+1.007453))
            it.vat_rate = 19.6
            it.holdback_rate = None
            it.holdback_on_vat = False
            acclist.append(it)
        return acclist

    def _build_config_data(self) :
        """
        Builds and fills a ``ConfigData`` object.

        :returns: A ``ConfigData`` object filled with relevant information.
        :rtype: `pybill.lib.config.entities.ConfigData`
        """
        cfg = ConfigData()
        cfg.company_address = self._build_organisation_address(u"cp")
        cfg.footer_lines.append(u"footer: line 1")
        cfg.footer_lines.append(u"footer: line 2")
        cfg.bank_data_lines.append(u"bank data: line 1")
        cfg.bank_data_lines.append(u"bank data: line 2")
        cfg.agreement_intro_lines.append(u"agreement introduction: line 1")
        cfg.agreement_intro_lines.append(u"agreement introduction: line 2")
        cfg.number_separators = {u"sign"     : u" ",
                                 u"thousands": u",",
                                 u"digits"   : u"·"}
        cfg.local_phrases = {u'colon'              : u":",
                             u'phone-kw'           : u"Phone",
                             u'fax-kw'             : u"Fax",
                             u'web-kw'             : u"Web",
                             u'email-kw'           : u"Email",
                             u'doc-ref-kw'         : u"Our ref",
                             u'receiver-kw'        : u"Attn",
                             u'sender-kw'          : u"Followed by",
                             u'on-date'            : u"on",
                             u'bill'               : u"Bill",
                             u'claim-form'         : u"Claim Form",
                             u'downpayment'        : u"Downpayment",
                             u'pro-forma'          : u"Purchase Order",
                             u'debit'              : u"Debit",
                             u'number'             : u"# ",
                             u'dated'              : u"dated",
                             u'valid-until'        : u"valid until",
                             u'intro-detail'       : u"All amounts in Euros",
                             u'quantity'           : u"Qty",
                             u'description'        : u"Description",
                             u'vat-rate'           : u"VAT rate",
                             u'unit-price'         : u"Unit Price",
                             u'tf-unit-price'      : u"TF Unit Price",
                             u'price'              : u"Price",
                             u'tf-price'           : u"TF Price",
                             u'it-price'           : u"IT Price",
                             u'holdback-on'        : u"Holdback on",
                             u'ita-est'            : u"i.e.",
                             u'total'              : u"Total",
                             u'tf-total'           : u"TF Total",
                             u'vat-amount'         : u"VAT",
                             u'it-total'           : u"IT Total",
                             u'including'          : u"including",
                             u'holdback'           : u"Holdback",
                             u'on-tf'              : u"on TF amounts",
                             u'on-vat'             : u"on VAT amounts",
                             u'debit-total'        : u"Total of debit",
                             u'charged-downpayment': u"Downpayment",
                             u'charged-on'         : u"charged on",
                             u'issued-debit'       : u"Debit",
                             u'issued-on'          : u"issued on",
                             u'to-be-paid'         : u"To be paid (EUR)",
                             u'payment-terms'      : u"Payment Terms",
                             u'to-bring-forward'   : u"To bring forward",
                             u'carry-forward'      : u"Carry forward",
                             u'your-ref-kw'        : u"Your ref",
                             u'purch-ref-kw'       : u"Purchase #",
                             u'supplier-ref-kw'    : u"Supplier #",
                            }

        return cfg

    def test_write_one_item(self):
        """
        Tests the PDFWriter writes correctly an accounting document with only
        one item.
        """
        self.acc_doc.acc_items = self._build_acc_items_list(1)
        self.acc_doc.acc_items[0].details = []
        self._run_pdf_test("%s_one_item.pdf" % self.entity_name),

    def test_write_one_item_with_details(self):
        """
        Tests the PDFWriter writes correctly an accounting document with only
        one item with details.
        """
        self.acc_doc.acc_items = self._build_acc_items_list(1)
        self.acc_doc.acc_items[0].details[0] = u"detailed description 1.1" * 7
        self._run_pdf_test("%s_one_item_with_details.pdf" % self.entity_name)

    def test_write_three_items(self):
        """
        Tests the PDFWriter writes correctly an accounting document with three
        items.
        """
        self.acc_doc.acc_items = self._build_acc_items_list(3)
        self._run_pdf_test("%s_three_items.pdf" % self.entity_name)

    def test_write_three_items_with_no_sender(self):
        """
        Tests the PDFWriter writes correctly an accounting document with three
        items and no sender data.
        """
        self.acc_doc.acc_items = self._build_acc_items_list(3)
        self.acc_doc.sender = None
        self._run_pdf_test("%s_three_items_no_sender.pdf" % self.entity_name)

    def test_write_three_items_with_person_receiver(self):
        """
        Tests the PDFWriter writes correctly an accounting document with three
        items and a receiver that is a person (no organisation data).
        """
        self.acc_doc.acc_items = self._build_acc_items_list(3)
        self.acc_doc.receiver.organisation = None
        self._run_pdf_test("%s_three_items_person_receiver.pdf" 
                           % self.entity_name)

    def test_write_three_items_with_organisation_receiver(self):
        """
        Tests the PDFWriter writes correctly an accounting document with three
        items and a receiver that is an organisation (no person name).
        """
        self.acc_doc.acc_items = self._build_acc_items_list(3)
        self.acc_doc.receiver.honorific = u""
        self.acc_doc.receiver.firstname = u""
        self.acc_doc.receiver.other_name = u""
        self.acc_doc.receiver.surname = u""
        self.acc_doc.receiver.lineage = u""
        self._run_pdf_test("%s_three_items_organisation_receiver.pdf" 
                           % self.entity_name)

    def test_write_three_items_with_various_qty_digits(self):
        """
        Tests the PDFWriter writes correctly an accounting document with three
        items and different specifications of quantity digits.
        """
        self.acc_doc.acc_items = self._build_acc_items_list(3)
        for i in range(3):
            self.acc_doc.acc_items[i].quantity = 1.545
            self.acc_doc.acc_items[i].quantity_digits = i
        self._run_pdf_test("%s_three_items_with_various_qty_digits.pdf"
                           % self.entity_name)

    def test_write_three_items_with_various_price_digits(self):
        """
        Tests the PDFWriter writes correctly an accounting document with three
        items and different specifications of unit price digits.
        """
        self.acc_doc.acc_items = self._build_acc_items_list(3)
        for i in range(3):
            self.acc_doc.acc_items[i].unit_price_digits = i+2
        self._run_pdf_test("%s_three_items_with_various_price_digits.pdf"
                           % self.entity_name)

    def test_write_three_items_with_various_vat_rates(self):
        """
        Tests the PDFWriter writes correctly an accounting document with three
        items that have various VAT rates.
        """
        self.acc_doc.acc_items = self._build_acc_items_list(3)
        self.acc_doc.acc_items[1].vat_rate = 33.0
        self._run_pdf_test("%s_three_items_with_various_vat_rates.pdf"
                           % self.entity_name)

    def test_write_three_items_with_various_vat_rates_and_one_nul(self):
        """
        Tests the PDFWriter writes correctly an accounting document with three
        items that have various VAT rates, one of this rate is zero.
        """
        self.acc_doc.acc_items = self._build_acc_items_list(3)
        self.acc_doc.acc_items[1].vat_rate = 33.0
        self.acc_doc.acc_items[2].vat_rate = 0.0
        self._run_pdf_test("%s_three_items_with_various_vat_rates_and_one"
                           "_nul.pdf" % self.entity_name)

    def test_write_three_items_with_various_vat_rates_one_not_defined(self):
        """
        Tests the PDFWriter writes correctly an accounting document with three
        items that have various VAT rates, one of this rate is not defined.
        """
        self.acc_doc.acc_items = self._build_acc_items_list(3)
        self.acc_doc.acc_items[1].vat_rate = 33.0
        self.acc_doc.acc_items[2].vat_rate = None
        self._run_pdf_test("%s_three_items_with_various_vat_rates_one_not"
                           "_defined.pdf" % self.entity_name)

    def test_write_three_items_with_no_vat_rate(self):
        """
        Tests the PDFWriter writes correctly an accounting document with three
        items that have no VAT rate.
        """
        self.acc_doc.acc_items = self._build_acc_items_list(3)
        for i in range(3):
            self.acc_doc.acc_items[i].vat_rate = None
        self._run_pdf_test("%s_three_items_with_no_vat_rate.pdf"
                           % self.entity_name)

    def test_write_three_items_and_one_holdback(self):
        """
        Tests the PDFWriter writes correctly an accounting document with three
        items and one holdback.
        """
        self.acc_doc.acc_items = self._build_acc_items_list(3)
        self.acc_doc.acc_items[1].holdback_rate = 5.0
        self._run_pdf_test("%s_three_items_and_one_holdback.pdf"
                           % self.entity_name)

    def test_write_three_items_no_vat_and_one_holdback(self):
        """
        Tests the PDFWriter writes correctly an accounting document with three
        items and one holdback.
        """
        self.acc_doc.acc_items = self._build_acc_items_list(3)
        for i in range(3):
            self.acc_doc.acc_items[i].vat_rate = None
        self.acc_doc.acc_items[1].holdback_rate = 5.0
        self.acc_doc.acc_items[1].holdback_on_vat = True
        self._run_pdf_test("%s_three_items_no_vat_and_one_holdback.pdf"
                           % self.entity_name)

    def test_write_three_items_and_holdbacks(self):
        """
        Tests the PDFWriter writes correctly an accounting document with three
        items and one holdback.
        """
        self.acc_doc.acc_items = self._build_acc_items_list(3)
        for i in range(3):
            self.acc_doc.acc_items[i].holdback_rate = 5.0*(i+1)
            self.acc_doc.acc_items[i].holdback_on_vat = True
        self.acc_doc.acc_items[0].holdback_on_vat = False
        self.acc_doc.acc_items[2].vat_rate = None
        self._run_pdf_test("%s_three_items_and_holdbacks.pdf"
                           % self.entity_name)

    def test_write_three_items_and_remarks(self):
        """
        Tests the PDFWriter writes correctly an accounting document with three
        items and some preliminary remarks.
        """
        self.acc_doc.acc_items = self._build_acc_items_list(3)
        self.acc_doc.remarks.append("Remark 1 "*15)
        self.acc_doc.remarks.append("Remark 2 ")        
        self._run_pdf_test("%s_three_items_and_remarks.pdf" % self.entity_name)


    def test_write_various_items_total_on_page_2(self):
        """
        Tests the PDFWriter writes correctly an accounting document with
        various items and a total that can't be displayed on page 1 (so it's
        on page 2).
        """
        self.acc_doc.acc_items = self._build_acc_items_list(6)
        self._run_pdf_test("%s_various_items_total_on_page_2.pdf"
                           % self.entity_name)

    def test_write_various_items_on_two_pages(self):
        """
        Tests the PDFWriter writes correctly an accounting document with
        various items displayed on two pages (too much items for one single
        page).
        """
        self.acc_doc.acc_items = self._build_acc_items_list(10)
        self._run_pdf_test("%s_various_items_on_two_pages.pdf"
                           % self.entity_name)

    def test_write_one_item_and_logo(self):
        """
        Tests the PDFWriter writes correctly an accounting document with only
        one item and a logo for the company.
        """
        self.acc_doc.acc_items = self._build_acc_items_list(1)
        self.acc_doc.cfg_data.company_logo = unicode(self.datapath("mpe.png"))
        self._run_pdf_test("%s_one_item_and_logo.pdf" % self.entity_name)
