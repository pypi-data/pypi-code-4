# -*- coding: utf-8 -*-
# Copyright 2013 Richard Kuesters.  See LICENSE file for details

from optparse import OptionParser, OptionGroup

import protoweb


def get_options():

    version = "%prog {0}".format(protoweb.__version__)

    desc = """protoweb is a simple command line tool to create rich web \
development environments, with processors and the power of the Cyclone \
framework to handle static and dynamic content."""

    epilog = """Copyright 2013 Richard Kuesters <rkuesters@gmail.com> and \
released under the MIT LICENSE <http://opensource.org/licenses/MIT>. \
Visit us on https://github.com/vltr/protoweb for more information."""

    usage = "%prog [-h]"

    parser = OptionParser(
        description=desc,
        usage=usage,
        version=version,
        epilog=epilog
    )

    parser.add_option(
        "-s",
        "--source",
        dest="sources",
        metavar="SOURCE",
        action="append",
        help="source path to run protoweb, can be more then one, default: %default"
    )

    parser.add_option(
        "-p",
        "--port",
        dest="port",
        metavar="PORT",
        help="the TCP port this server will listen to, default: %default",
        default=9000,
        type="int"
    )

    parser.add_option(
        "-i",
        "--index",
        dest="default_html",
        metavar="INDEX",
        help="the html file in case none is found, default: %default",
        default="index.html"
    )

    parser.add_option(
        "-I",
        "--interface",
        dest="interface",
        metavar="INTERFACE",
        help="the TCP interface you will be running, default: %default",
        default="0.0.0.0"
    )
    parser.add_option(
        "-L",
        "--use-less",
        action="store_true",
        dest="use_less",
        default=False,
        help="use the Less CSS processor for *.less files, default: %default"
    )

    parser.add_option(
        "-n",
        "--no-templates",
        action="store_true",
        dest="no_templates",
        default=False,
        help="disable the usage of Cyclone templates: %default"
    )

    less_group = OptionGroup(parser, "Less options")

    less_group.add_option(
        "-l",
        "--less-flag",
        dest="less_flags",
        metavar="LESS-FLAGS",
        action="append",
        help="less desired compilation flag, can be more then one"
    )

    tpl_group = OptionGroup(parser, "Cyclone template options")

    tpl_group.add_option(
        "-j",
        "--json-path",
        dest="json_path",
        metavar="JSON_PATH",
        help="the JSON path in case of usage of Cyclone templates, default: %default",
        default="."
    )

    parser.add_option_group(less_group)
    parser.add_option_group(tpl_group)

    return parser
