# -*- coding: utf-8 -*-
"""
``pybill.lib.pdfwriters.utils`` module defines two specific flowable elements
for :mod:`reportlab.platypus` and useful functions.

The flowable elements are the elements that can be inserted in the PDF by the
platypus machinery of Reportlab. These specific elements allow the computation
of a carry-forward for each page.

.. autoclass:: NumberParagraph
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: TotalizableTable
   :members:
   :undoc-members:
   :show-inheritance:

The functions define in this module concern the rendering of texts and numbers,
and the conversion to the specific flowable elements defined above.

.. autofunction:: escape_text

.. autofunction:: format_number

.. autofunction:: turn_Table_in_TotalizableTable
"""
__docformat__ = "restructuredtext en"

from xml.sax.saxutils import escape

from reportlab.platypus import Paragraph
from reportlab.platypus import Table

from pybill.lib import ACCURACY


def escape_text(text, normalize_spaces=False):
    """
    Escapes the text to be written in the PDF document.
    
    This function must be called when the text is in a platypus ``Paragraph``
    as some characters must be escaped (e.g. & and <).
    
    .. warning::

       Do not call this function after the text has been tagged as the
       tags will be escaped (e.g. ``<b>hello</b>`` will be turned in
       ``&lt;b>Hello&lt;/b>``\ ).
    
    :parameter text: Text to be escaped.
    :type text: :class:`unicode`
    
    :parameter normalize_spaces:
        When set to ``True``, the function normalizes the whitespace characters
        (no space at begining and end, only one space between the words).
    :type normalize_spaces: :class:`bool`
    
    :returns: The normalized text.
    :rtype: :class:`unicode`
    """
    if normalize_spaces:
        string = u" ".join(text.split())
    else :
        string = text
    return escape(string)


def format_number(number, digits=ACCURACY, separators=None):
    """
    Formats a number to be written in the PDF document.

    This function uses separators defined in the ``separators`` dictionnary
    (separating characters between the sign and the number, between the
    thousands and between the integer and the digits).
    
    :parameter number: Float number to be formatted.
    :type number: :class:`float`
    
    :parameter digits: Number of digits to be displayed (the float number is
                       rounded if it has more digits). 
    :type digits: :class:`int`

    :parameter separators:

        Dictionary containing the separators used to format a number. There are
        three separators:

        - `sign` that is inserted between the sign and the non-signed number,

        - `thousands` that is inserted between the thousands and the hundreds,
          between the millions and the hundreds of thousands, and so on,

        - `digits` that is inserted between the integer and the digits.

        When not specified, default separators are used.  They are:
        ``{u'sign': u'', u'thousands': u'',\ u'digits': u'.'}``.

    :type separators: dictionary of :class:`unicode` indexed with :class:`unicode` keys
    
    :returns: The float number formatted in a string.
    :rtype: :class:`unicode`
    """
    result = u""
    # Setting default values in the ``separators`` dictionnary.
    if separators is None:
        separators = {}
    separators.setdefault(u'sign', u'')
    separators.setdefault(u'thousands', u'')
    separators.setdefault(u'digits', u'.')
    # If number is None, returns u""
    if number is None:
        return u""
    # Deals with the sign.
    if number < 0:
        number = -number
        result += u"-%s" % separators[u'sign']
    # Deals with the integer part (cuts it three digits by three digits)
    number = round(number, digits)
    if digits > 0:
        num_int = int(number)
        num_dgts = number - num_int
    else:
        num_int = int(number)
        num_dgts = 0.0
    if num_int == 0:
        num_str = u"0"
    else:
        num_str = u""
        while num_int > 0:
            units = num_int % 1000
            num_int /= 1000
            if num_int > 0:
                num_str = u"%s%03d%s" % (separators[u'thousands'],
                                         units, num_str)
            else:
                num_str = u"%d%s" % (units, num_str)
    result += num_str
    # Deals with the digits
    if digits > 0:
        str_mask = u"%%.%df" % digits
        rounded_str = str_mask % num_dgts
        result += u"%s%s" % (separators[u'digits'], rounded_str.split(".")[1])
    # And finally returns the result!
    return result


def turn_Table_in_TotalizableTable(table):
    """
    Builds a PyBill-specific :class:`TotalizableTable` object from a
    platypus standard :class:`~reportlab.platypus.Table` object.

    The two objects have the same internal content.
    
    :parameter table: Platypus table object to be turned in a PyBill-specific
                      :class:`TotalizableTable` object.
    :type table: :class:`reportlab.platypus.Table`
    
    :returns: Pybill-specific ``TotalizableTable`` object identical to the
              Platypus table.
    :rtype: :class:`TotalizableTable`
    """
    tot_table = TotalizableTable(table._cellvalues,
                                  table._colWidths, table._argH,
                                  repeatRows=table.repeatRows,
                                  repeatCols=table.repeatCols,
                                  splitByRow=table.splitByRow)
    # Copies the style instructions
    tot_table._cellStyles = table._cellStyles[:]
    tot_table._linecmds = table._linecmds[:]
    tot_table._bkgrndcmds = table._bkgrndcmds[:]
    tot_table._spanCmds = table._spanCmds[:]
    return tot_table


class NumberParagraph(Paragraph):
    """
    PyBill-specific paragraph that only contains a number.

    The ``NumberParagraph`` objects will be used by PyBill-specific
    :class:`TotalizableTable` class to compute a sum over the rows of the table,
    and be able to compute a carry-forward at the end of each page.

    Basically a ``NumberParagraph`` is identical to a platypus
    :class:`~reportlab.platypus.Paragraph` but contains a float number (see
    ``number`` attribute). This number will be used to compute the sum in a
    ``TotalizableTable``.

    .. attribute:: number

       Attribute containing the number displayed in the paragraph. It is this
       number that will be totalized in the ``TotalizableTable``.

       type: :class:`float`

    .. automethod:: __init__
    """
    def __init__(self, number, text, style,
                 bulletText = None, frags=None, caseSensitive=1):
        """
        Initializes a ``NumberParagraph``.

        Most of the parameters are identical to those of the platypus
        :class:`~reportlab.platypus.Paragraph` initializer (see this base
        class for details on the parameters).
        
        :parameter number: The number contained in the paragraph. This number
                           will be used by the ``TotalizableTable`` to compute
                           the total over its rows.

                           This parameter is specific to the
                           ``NumberParagraph`` class.
        :type number: :class:`float`
        
        :parameter text: The text contained in the paragraph (see ``Paragraph``
                         for a full description of the available markup).
        :type text: :class:`unicode`
        
        :parameter style: The style of the paragraph.
        :type style: :class:`reportlab.lib.styles.ParagraphStyle`
        """
        self.number = number
        Paragraph.__init__(self, text, style, bulletText = bulletText,
                           frags=frags, caseSensitive=caseSensitive)


class TotalizableTable(Table):
    """
    PyBill-specific table that can compute a total over its cells.

    The total is computed by summing all the the :class:`NumberParagraph`
    objects contained in the table cells.
    
    Usually there is only one ``NumberParagraph`` per row and thus the
    ``TotalizableTable`` can compute the sum of an amount over the rows.

    Please note that only the cells of the table that contain a single
    ``NumberParagraph`` object will be taken into account for computing the
    sum.

    .. automethod:: _splitRows
    """
    def __repr__(self):
        """
        Returns a string representation of the object.

        :returns: String representation of the object.
        :rtype: :class:`str`
        """
        return "Totalizable"+Table.__repr__(self)

    def _splitRows(self, availHeight):
        """
        Splits the table into two tables. The first table height is maximal
        but less than availHeight.
        
        :parameter availHeight: Available height in the PDF frame.
        :type availHeight: :class:`float`
        
        :returns: A list of ``TotalizableTable`` objects containing all the
                  rows of the table that have been split into several objects.
                  This list can be empty, have a single element or have
                  several elements.
        :rtype: list of :class:`TotalizableTable`
        """
        # Ask the ``_splitRows`` method of the base class to split the table.
        result = Table._splitRows(self, availHeight)
        # As the result contains ``Table`` instances and not
        # ``TotalizableTable`` instances, turns the result elements into
        # ``TotalizableTable`` objects.
        return [turn_Table_in_TotalizableTable(elt) for elt in result]

    def compute_total(self):
        """
        Computes the sum, over the cells of the table, of all the numbers
        contained in :class:`NumberParagraph` objects.
        
        Usually there is only one ``NumberParagraph`` per row, thus the
        ``compute_total`` method returns the sum over the rows of the table.

        Please note that only the cells of the table that contain a single
        ``NumberParagraph`` object will be taken into account for computing
        the sum.

        :returns: the sum of all the numbers contained in the
                  ``NumberParagraph`` objetcs inside the cells of the table.
        :rtype: :class:`float`
        """
        return sum([cell.number for line in self._cellvalues for cell in line
                    if cell.__class__ is NumberParagraph])
