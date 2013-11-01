import os
from unittest import TestCase
from PyODConverter import DocumentConverter, DocumentConversionException

class DocumentConverterTest(TestCase):

  def setUp(self):
    self.converter = DocumentConverter(listener=('localhost', 2002))

  def test_fail_connect(self):
    with self.assertRaises(DocumentConversionException):
      DocumentConverter(listener=('localhost', 1337))

  def test_not_existing_document(self):
    input = "kittens.docx"
    output = "docs.pdf"
    with self.assertRaises(DocumentConversionException):
      self.converter.convert(input, output)

  def test_convert_docx_to_pdf(self):
    input = "test_data/document.docx"
    output = "test_data/document.pdf"
    result = self.converter.convert(input, output)
    self.assertTrue(os.path.exists("test_data/document.pdf"))

  def test_convert_odt_to_pdf(self):
    input = "test_data/document.odt"
    output = "test_data/document.pdf"
    result = self.converter.convert(input, output)
    self.assertTrue(os.path.exists("test_data/document.pdf"))

  def tearDown(self):
    """
    Cleanup
    """
    if os.path.exists("test_data/document.pdf"):
      os.remove("test_data/document.pdf")
