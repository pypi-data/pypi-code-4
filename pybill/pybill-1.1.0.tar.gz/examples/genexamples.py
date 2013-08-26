#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyBill program generating the examples

Generates the PDF rendering for the example XML files. XML input files and
PDF output files are saved in a subdirectory.
"""

from optparse import OptionParser
import logging
import os.path as osp
from os import listdir

from pybill.lib.controller import PyBillController


logging.basicConfig(level=logging.DEBUG)


EXAMPLES_DIR = osp.abspath(osp.dirname(__file__))
CONFIGS_DIR = "configs"
INPUTS_DIR = "inputs"
RESULTS_DIR = "results"


def run(config_file=None) :
    """
    Function generating the examples. XML input files and PDF output files
    are saved in a subdirectory.

    :param config_file: Filename of a config file that will override config
                        references specified in the examples files.
    """
    logging.info("*** Generating examples in `%s` subdirectory"
                 % RESULTS_DIR)
    controller = PyBillController()
    # Hacking config register to read the config files in example config
    # subdirectory.
    controller.config_register.__class__.USER_CONFIG_DIR \
                                          = osp.join(EXAMPLES_DIR, CONFIGS_DIR)
    # Gets the example XML files to process.
    input_files = [osp.join(EXAMPLES_DIR, INPUTS_DIR, f)
                   for f in listdir(osp.join(EXAMPLES_DIR, INPUTS_DIR))
                   if osp.splitext(f)[1] == ".xml"]
    logging.info("    - Found %d example files in `%s` subdirectory"
                 % (len(input_files), INPUTS_DIR))
    if config_file is not None:
        logging.info("    - Overriding specified configurations with  %s config"
                     " file" % config_file)
    # Reads the accounting entities from the XML files.
    logging.info("    - Reading example files")
    read_entities = controller.build_entities_from_files(input_files,
                                                      cfg_filename=config_file)
    # For each accounting entity, changes the company logo filename in the
    # config object (puts an absolute path) and builds the pdf result filename.
    entities = []
    for accdoc, filename in read_entities:
        accdoc.cfg_data.company_logo = osp.join(EXAMPLES_DIR, CONFIGS_DIR,
                                                accdoc.cfg_data.company_logo)
        pdf_filename = "%s%s%s" % (osp.join(EXAMPLES_DIR, RESULTS_DIR,
                                            osp.split(filename)[1]),
                                   osp.extsep,
                                   "pdf")
        entities.append((accdoc, pdf_filename))
    # Generating PDF for the entities.
    logging.info("    - Generating PDF from example files")
    controller.write_pdf_to_files(entities)
    logging.info("    - Generated %d PDF files in `%s` subdirectory"
                 % (len(entities), RESULTS_DIR))
    logging.info("*** End of generation")


if __name__ == '__main__' :
    desc = ("Generates the PDFs of the examples of accounting documents with "
            "PyBill tool.")
    parser = OptionParser(description=desc)
    parser.add_option("-c", "--config",
                      action="store", type="string", dest="config_file",
                      default=None, metavar="CONFIG",
                      help=("override configs specified in examples documents "
                            "with CONFIG file"))
    (options, args) = parser.parse_args()
    run(options.config_file)
