# -*- coding: utf-8 -*-
"""
``pybill.lib.config.entities`` module defines the class used to encapsulate the
configuration data.

.. autoclass:: ConfigData
   :members:
   :undoc-members:
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"

from pybill.lib.entities.addresses import OrganisationAddress


class ConfigData:
    """
    Class holding the configuration data.

    This configuration data is used to write the accounting documents in a PDF
    format. It mainly contains the company address and the localised words for
    the accounting documents.

    .. attribute:: reference

        Attribute defining the reference of the configuration that is used to
        store it in the configuration register. This reference is unique among
        configurations and matches the name of the XML file where the
        configuration is stored. It is also used to link the accounting XML
        documents with this configuration through the PyBill processing
        instruction.

       type:class:`unicode`

    .. attribute:: name

       Attribute defining the name of the configuration. The name can be used
       when displaying a list of the various configurations and is more explicit
       that the reference.

       type: :class:`unicode`

    .. attribute:: company_logo

       Attribute defining the name of the file containing the company logo (an
       image).  This logo will be displayed on every PDF document.

       type: :class:`str`

    .. attribute:: company_address

       Attribute containing the specific object that describes the company
       address.

       type: :class:`~pybill.lib.entities.addresses.OrganisationAddress`

    .. attribute:: footer_lines

       Attribute containing the list of the lines to be written in the footer
       of all the PDF documents.

       type: list of :class:`unicode`

    .. attribute:: bank_data_lines

       Attribute containing the list of the lines that describe the bank
       data. This information will be written on the PDF documents that require
       a payment from the client (bill, etc.)

       type: list of :class:`unicode`

    .. attribute:: agreement_intro_lines

       Attribute containing the list of the agreement lines to be written on
       the pro-forma PDF document (e.g. u"sign here").

       type: list of :class:`unicode`

    .. attribute:: number_separators

       Attribute containing a dictionnary describing the characters used to
       format the numbers in the PDF output. There are three separators
       corresponding to the three keys of the dictionary:

       - ``u"sign"`` contains the character separating the sign and the
         non-signed part of the number,

       - ``u"thousands"`` contains the character separating the thousands and
         the hundreds, the millions and the hundreds of thounsands, and so on,

       - ``u"digits"`` contains the character separating the integer part of the
         number and the digits.

       An example of ``number_separators`` dictionnary is ``{u"sign": u"",
       u"thousands": u" ", \ u"digits": u"."}```

       type: dictionary of :class:`unicode` indexed with :class:`unicode` keys

    .. attribute:: local_phrases

       Attribute containing a dictionary whose keys are the keywords used in
       PyBill and whose values are the localized phrases corresponding to these
       keywords (e.g. u"bill": u"Facture").
                         
       type: dictionary of :class:`unicode` indexed with :class:`unicode` keys

    .. automethod:: __init__
    """
    def __init__(self):
        """
        Intializes a new object.

        This object is empty and will be filled when reading an XML
        configuration file (cf.
        :class:`~pybill.lib.entities.config.xmlreaders.ConfigXMLReader`\ ).
        """
        self.reference = None
        self.name = u""
        self.company_logo = u""    
        self.company_address = OrganisationAddress()
        self.footer_lines = []
        self.bank_data_lines = []
        self.agreement_intro_lines = []
        self.number_separators = {}
        self.local_phrases = {}

    def get_local_phrase(self, keyword):
        """
        Gets the local phrase corresponding to the keyword ``keyword``.

        If the keyword is not defined in the configuration data, returns the
        keyword itself between two ``#`` characters (and doesn't raise any
        exception).

        :parameter keyword: keyword that must be localized. Can be for example
                            u"bill").
        :type keyword: :class:`unicode`

        :returns: The localized phrase associated to the given keyword in the
                  configuration data.
        :rtype: :class:`unicode`
        """
        if self.local_phrases.has_key(keyword):
            return self.local_phrases[keyword]
        else:
            return u"## %s ##" % keyword
