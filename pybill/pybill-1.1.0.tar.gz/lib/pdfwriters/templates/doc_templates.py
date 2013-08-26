# -*- coding: utf-8 -*-
"""
``pybill.lib.pdfwriters.templates.doc_templates`` contains the definition of
the document template classes used in the PDF generation with ReportLab
`platypus`.

These classes are derived from platypus standard classes but are specific to
PyBill software. The document template is used to create new PDF
documents for the PyBill accounting documents. It adds some behaviour to its
base class in the flow content management, specifically the ability to compute
the carry forward from a :class:`~pybill.lib.pdfwriters.utils.TotalizableTable`
inserted in the flow content.

.. autoclass:: AccDocDocumentTemplate
   :members:
   :undoc-members:
   :show-inheritance:
"""
__docformat__ = "restructuredtext en"

from reportlab.platypus import BaseDocTemplate

from pybill.lib.pdfwriters.utils import TotalizableTable
from pybill.lib.pdfwriters.templates.page_templates import (AccDocPageTemplate,
                                                       AccDocFirstPageTemplate)


class AccDocDocumentTemplate(BaseDocTemplate):
    """
    The accounting document template is a class explaining how to create an
    accouting PDF document.

    It uses the
    :class:`~pybill.lib.pdfwriters.templates.page_templates.AccDocPageTemplate`
    and the
    :class:`~pybill.lib.pdfwriters.templates.page_templates.AccDocFirstPageTemplate`
    page templates and can compute the carry forward that has to be brought
    forward from one page to another.

    The computation of the carry forward is only possible if the main table
    of the document is a :class:`~pybill.lib.pdfwriters.utils.TotalizableTable`
    and if, in this table, the total of each row is put in a
    :class:`~pybill.lib.pdfwriters.utils.NumberParagraph`.
    
    The carry forward will not appear if a
    :class:`~pybill.lib.pdfwriters.utils.TotalizableTable` is not used.

    .. attribute:: carry_forward

       Attribute containing the carry forward that has to be brought forward
       from a finished page to the next page.

       type: :class:`float`

    .. attribute:: _carry_forward_computed

       Attribute containing a flag set to ``True`` if the carry forward has once
       been computed.

       type: :class:`bool`
    
    .. attribute:: display_carry_forward

       Attribute containing a flag set to ``True`` if the carry forward has to
       be displayed at end of the page (and the beginning of the next page).
                                 
       type: :class:`bool`
    
    .. attribute:: all_flowables_handled

       Attribute containing a flag set to ``True`` if all the flowables have
       been handled.

       The carry forward must not be displayed on the last page. The only way I
       found to know if is the last page, is to watch the build progress and set
       a flag when I see the last flowable has been handled. Anyway, this works
       properly because the last flowable of the document is in a
       :class:`~reportlab.platypus.KeepTogether` and is never splitted over
       pages.
        
       type: :class:`bool`

    .. attribute:: _estim_num_of_flowables

       Attribute containing the estimated number of flowables to handle (see
       :attr:`all_flowables_handled` for more details).
       
       type: :class:`int`

    .. automethod:: __init__
    """
    def __init__(self, filename, acc_doc):
        """
        Initializes an ``AccDocDocumentTemplate`` object.

        This method initializes the correct page templates to be used when
        generating the document, sets the PDF document metadata, and initializes
        the attributes.
        
        :parameter filename: name of the PDF output file
        :type filename: unicode

        :parameter acc_doc: Accounting entity containing the actual document
                            to be rendered in PDF.
        :type acc_doc:
            :class:`~pybill.lib.entities.accounting_docs.abstract.GenericAccountingDoc`
        """
        # Initializes the document template with the correct page templates.
        accdoc_templates = [AccDocFirstPageTemplate(acc_doc,
                                                    template_id="First"),
                            AccDocPageTemplate(acc_doc,
                                               template_id="Next")]
        BaseDocTemplate.__init__(self, filename,
                                 pageTemplates=accdoc_templates,
                                 allowSplitting=1)
        # Sets the PDF metadata (initialized by base class).
        self.title = u" ".join(acc_doc.doc_ref.split())
        self.author = acc_doc.cfg_data.company_address.name.strip()
        # Specific attributes.
        self.carry_forward = 0.0
        self._carry_forward_computed = False
        self.display_carry_forward = False
        self.all_flowables_handled = False
        self._estim_num_of_flowables = 0
        # Registers the progress function that will set the
        # ``all_flowables_handled`` flag.
        self._onProgress = self.watch_flowable_handling

    def handle_pageBegin(self):
        """
        Overrides base method to add a change of page template after the
        first page and to unset the :attr:`display_carry_forward` flag.
        """
        self._handle_pageBegin()
        if self.page == 1:
            self._handle_nextPageTemplate("Next")
        self.display_carry_forward = False

    def handle_pageEnd(self):
        """
        Overrides base method to set the :attr:`display_carry_forward` flag
        when we are ending a page (that is not the last page) and when the
        main table has already been displayed (or is being displayed).
        """
        if not self.all_flowables_handled:
            # If the carry forward hasn't been computed (``TotalizableTable``
            # not yet displayed on the pages), don't display it.
            self.display_carry_forward = self._carry_forward_computed
        self._handle_pageEnd()

    def afterFlowable(self, flow):
        """
        Overrides base method to compute the carry forward if the flowable
        is a :class:`~pybill.lib.pdfwriters.utils.TotalizableTable`.

        The only :class:`~pybill.lib.pdfwriters.utils.TotalizableTable` in the
        flowables list is the main table that will be used to compute the
        carry forward.
        
        :parameter flow: Flowable that has just been drawn on the page.
        :type flow: :class:`reportlab.platypus.Flowable`
        """
        if isinstance(flow, TotalizableTable):
            self._carry_forward_computed = True
            self.carry_forward += flow.compute_total()

    def watch_flowable_handling(self, ev_type, value):
        """
        Progress function that is called by the document template as it builds
        the PDF document.

        This function has been registered by the :meth`__init__` method in the
        hook called during document process (cf. :attr:`_onProgress` attribute
        of the base class). It sets the :attr:`all_flowables_handled` flag.

        :parameter ev_type: Type of the event. Possible types are:
        
                            - ``PASS``: number of the pass starting
                              now. Numerous passes are done when working with
                              multi-build for indexing flowables.
                              
                            - ``STARTED``: starting build.
                            
                            - ``SIZE_EST``: estimated number of flowables to be
                              handled (some flowables may be added when one
                              flowable is splitted over pages).
                              
                            - ``PROGRESS``: number of the flowable that has just
                              been handled (if a flowable is splitted over
                              pages, its number will appear various times in
                              PROGRESS).
                                      
                            - ``PAGE``: number of the page that has just been
                              finished.
                                  
                            - ``FINISHED``: ending build.
        :type ev_type: :class:`str`

        :parameter value: Number related to the event.
        :type value: :class:`int`
        """
        if ev_type == "SIZE_EST":
            self._estim_num_of_flowables = value
        # The last flowable in an accounting document (the total table) is in a
        # ``KeepTogether``, thus we know it will never be splitted over two
        # pages. Therefore when we see the last flowable in `PROGRESS` we know
        # there is no more flowable to handle (clever isn't it).
        if ev_type == "PROGRESS":
            self.all_flowables_handled = (self._estim_num_of_flowables == value)
