##
# This file contains an class for pdf_collate
#
# @package     pdf_collate
# @author      Matt Koskela <mattkoskela@gmail.com>
##

"""
Example.py

This file contains an example class with a basic function.
"""

import os
import hashlib
from PyPDF2 import PdfFileReader, PdfFileWriter


class PDF():
    """
    This is the example Math class in pybase
    """

    def __init__(self):
        pass

    def collate_pages(self, source_filename, output_filename=""):

        if not output_filename:
            random_filename = os.getcwd() + "/" + hashlib.md5().hexdigest() + ".pdf"
            output_filename = random_filename

        pdfTest = PdfFileReader(file(source_filename, "rb"))
        output = PdfFileWriter()

        number_of_pages = pdfTest.getNumPages()

        for page_number in range(0, number_of_pages/2):
            output.addPage(pdfTest.getPage(page_number))
            output.addPage(pdfTest.getPage(page_number + number_of_pages/2))

        outputStream = file(output_filename, "wb")
        output.write(outputStream)
        outputStream.close()

        if random_filename:
            os.rename(random_filename, source_filename)
