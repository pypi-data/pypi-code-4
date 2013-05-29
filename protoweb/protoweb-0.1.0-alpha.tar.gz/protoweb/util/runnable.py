# -*- coding: utf-8 -*-
# Copyright 2013 Richard Kuesters.  See LICENSE file for details

from protoweb.server import ProtoWebServer, ProcessorHandler
from protoweb.processors import (Processor, LessProcessor,
                                 CycloneTemplateProcessor)

from protoweb.util import get_options


def run():
    parser = get_options()
    (options, args) = parser.parse_args()

    # order of execution must be respected
    if options.use_less:
        ProcessorHandler.add_processor(LessProcessor)

    if not options.no_templates:
        ProcessorHandler.add_processor(CycloneTemplateProcessor)

    ProcessorHandler.add_processor(Processor)

    server = ProtoWebServer(options)
    server.run()


__all__ = ['run']
