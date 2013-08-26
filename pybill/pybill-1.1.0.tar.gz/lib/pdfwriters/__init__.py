# -*- coding: utf-8 -*-
"""
``pybill.lib.pdfwriters``  package contains the classes and functions used to
produce PDF documents from the PyBill accounting documents.

This package uses :mod:`reportlab` library to build the PDF documents,
specifically the :mod:`~reportlab.platypus` library (see ReportLab documentation
for details).

From this package, the only public class that should be used outside of this
package is the :class:`~pybill.lib.pdfwriters.writers.PDFWriter` class. This
class can transform any PyBill accounting document into a PDF document. It is
imported and available in the namespace of this package.

Moreover, in this package, we define several `reportlab` paragraph styles that
will be used during the PDF generation.

.. data:: style_normal_left

   Object containing the style for a paragraph aligned on the left.

   type: :class:`reportlab.lib.styles.ParagraphStyle`

.. data:: style_normal_just

   Object containing the style for a paragraph justified on the left and the
   right.

   type: :class:`reportlab.lib.styles.ParagraphStyle`

.. data:: style_normal_right

   Object containing the style for a paragraph aligned on the right.

   type: :class:`reportlab.lib.styles.ParagraphStyle`

.. data:: style_normal_center

   Object containing the style for a centered paragraph.

   type: :class:`reportlab.lib.styles.ParagraphStyle`

.. data:: style_little_left

   Object containing the style for a paragraph aligned on the left but with a
   little font size.

   type: :class:`reportlab.lib.styles.ParagraphStyle`

.. data:: style_little_right

   Object containing the style for a paragraph aligned on the right but with a
   little font size.

   type: :class:`reportlab.lib.styles.ParagraphStyle`

.. data:: style_little_center

   Object containing the style for a centered paragraph but with a little font
   size.

   type: :class:`reportlab.lib.styles.ParagraphStyle`

.. data:: style_little_indent_left

   Object containing the style for a paragraph aligned on the left with a little
   font size and with a positive identation on the first line.

   type: :class:`reportlab.lib.styles.ParagraphStyle`

.. data:: style_footer

   Object containing the style for a paragraph of the footer (centered with 
   quite a little font size).

   type: :class:`reportlab.lib.styles.ParagraphStyle`

.. data:: style_title

   Object containing the style for a paragraph of the title (left aligned with a
   bigger font size).

   type: :class:`reportlab.lib.styles.ParagraphStyle`
"""
__docformat__ = "restructuredtext en"

from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import  TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY 


# Defining paragraph styles used in PDF generation

style_normal_left = ParagraphStyle("normal_left")
style_normal_left.fontSize = 11
style_normal_left.firstLineIndent = -1*cm
style_normal_left.leftIndent = 1*cm

style_normal_just = ParagraphStyle("normal_just")
style_normal_just.fontSize = 11
style_normal_just.firstLineIndent = -1*cm
style_normal_just.leftIndent = 1*cm
style_normal_just.alignment = TA_JUSTIFY

style_normal_right = ParagraphStyle("normal_right")
style_normal_right.fontSize = 11
style_normal_right.alignment = TA_RIGHT

style_normal_center = ParagraphStyle("normal_center")
style_normal_center.fontSize = 11
style_normal_center.alignment = TA_CENTER

style_little_left = ParagraphStyle("little_left")
style_little_left.fontSize = 9
style_little_left.firstLineIndent = -1*cm
style_little_left.leftIndent = 1*cm

style_little_right = ParagraphStyle("little_right")
style_little_right.fontSize = 9
style_little_right.alignment = TA_RIGHT

style_little_center = ParagraphStyle("little_center")
style_little_center.fontSize = 9
style_little_center.alignment = TA_CENTER

style_little_indent_left = ParagraphStyle("little_indent_left")
style_little_indent_left.fontSize = 9
style_little_indent_left.firstLineIndent = 0.5*cm

style_footer = ParagraphStyle("footer")
style_footer.fontSize = 10
style_footer.alignment = TA_CENTER

style_title = ParagraphStyle("title")
style_title.fontSize = 14
style_title.fontName = "Helvetica"
style_title.firstLineIndent = -1*cm
style_title.leftIndent = 1*cm


# Imports the class that must be used from the outside to write PDF bills
from pybill.lib.pdfwriters.writers import PDFWriter
