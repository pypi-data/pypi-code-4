# -*- coding: utf-8 -*-
"""
``pybill.commandline.ui`` module define the User Interface for PyBill command
line.

This User Interface consists in a :func:`run` function that defines a parser for
the command line arguments and relies on a PyBill controller for running the
PyBill functions.

This module can be executed and just runs the :func:`run` function defined
below.

In this module, we define a unique PyBill controller that will be used by the
run function.

.. data:: controller

   Unique controller that is used by the :func:`run` function to do the actual
   PyBill work.

   type: :class:`~pybill.lib.controller.PyBillController`

This module also defines the run function that provides the User Interface for
the command line.

.. autofunction:: run
"""
__docformat__ = "restructuredtext en"

from optparse import OptionParser
from traceback import format_exc
from sys import stderr
import os.path as osp
from pybill.lib.controller import PyBillController
from pybill.lib.errors import PyBillException
from pybill.__pkginfo__ import version

"""
Controller that does the actual PyBill work.
"""
controller = PyBillController()


def run():
    """
    Function containing the User Interface for the command line.

    This function hardly relies on a
    :class:`~pybill.lib.controller.PyBillController` object for doing the
    actual work and only reads and passes the correct arguments.

    In order to manage the command line arguments, this function defines and
    uses an :class:`optparse.OptionParser` object.
    """
    # Defines the parser of the command line options
    usage = ("Usage: %prog [options] accounting_files")
    desc = ("Generate a PDF representation of accounting documents (bills, "
            "etc.) The accounting documents are XML documents in a 'PyBill "
            "Document' format. They can represent a bill, a claim form, a "
            "downpayment, a debit, or a pro-forma. PyBill converts them in PDF"
            " and can generate the corresponding accounting entries in "
            "'pycompta' XML format.")
    opt_parser = OptionParser(usage=usage, description=desc,
                              version="PyBill %s" % version)
    opt_parser.add_option("-c", "--config", action="store", type="string",
                          dest="config_file", default=None,
                          metavar="CFGFILE",
                          help=("Name of the config file to be used for "
                                "generating the PDFs of the accounting "
                                "documents. This config file overrides the "
                                "config specified in each accounting "
                                "document."))
    opt_parser.add_option("-k", "--convert", action="store_true",
                          dest="convert_accdocs", default=False,
                          help=("Convert the processed accounting documents "
                                "into the last 'PyBill Document' format and "
                                "save them."))
    opt_parser.add_option("-n", "--no-entries", action="store_false",
                          dest="gen_entries", default=True,
                          help=("Don't generate the accounting entries "
                                "corresponding to the processed accounting "
                                "documents."))
    opt_parser.add_option("-e", "--entries-file", action="store", type="string",
                          dest="entries_file", default="entries.xml",
                          metavar="XMLFILE",
                          help=("Name of the file where the generated "
                                "accounting entries will be saved in 'pycompta'"
                                " format."))
    opt_parser.add_option("--encoding", action="store", type="string",
                          dest="xml_encoding", default="UTF-8",
                          metavar="XML_ENCODING",
                          help=("Encoding used for the XML files outputted by "
                                "this program (e.g. entries file or converted "
                                "pybill document."))
    opt_parser.add_option("--debug", action="store_true",
                          dest="debug", default=False,
                          help=("Print debug information and don't catch "
                                "the exceptions."))
    # Parses the command line options
    (options, acc_files) = opt_parser.parse_args()
    # Actual run
    try:
        acc_docs = controller.build_entities_from_files(acc_files,
                                                        options.config_file)
        if options.convert_accdocs:
            controller.save_entities_to_files(
                [(doc, "%s%sxml" % (filename, osp.extsep))
                 for doc, filename in acc_docs], options.xml_encoding)
        controller.write_pdf_to_files(
            [(doc, "%s%spdf" % (filename, osp.extsep))
             for doc, filename in acc_docs])
        if options.gen_entries:
            controller.export_accounting_entries_to_xml_file(
                [doc for doc, _ in acc_docs], options.entries_file, 
                options.xml_encoding)
    except PyBillException, exc:
        if not options.debug:
            stderr.write("Error while running PyBill:\n")
            stderr.write("%s\n" % exc)
        else:
            raise
    except Exception, exc:
        if not options.debug:
            stderr.write("Unexpected error during execution!\n")
            stderr.write("%s" % format_exc(limit=1))
        else:
            raise


if __name__ == '__main__' :
    run()
