#!/usr/bin/python
# -*- coding: utf-8 -*-

import radish

import os
import sys
import time
import optparse


def main():
    parser = optparse.OptionParser(
        description="radish is a smart 'Behavior Driven Developement'-Tool written in python",
        epilog="(C) Copyright 2012 by Timo Furrer <tuxtimo@gmail.com>"
    )
    parser.add_option(
        "-b", "--basedir",
        dest="basedir",
        default=os.path.join(os.getcwd(), "radish"),
        help="The basedir is used to locate the steps.py and terrain.py"
    )
    parser.add_option(
        "-a", "--abort-fail",
        dest="abort_fail",
        action="store_true",
        help="If one feature file fails this option will stop the execution"
    )
    parser.add_option(
        "-m", "--marker",
        dest="marker",
        default=int(time.time()),
        help="A specific marker for the step loggings"
    )
    parser.add_option(
        "-d", "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Executes a dry run to validate steps"
    )
    parser.add_option(
        "-x", "--xunit-file",
        dest="xunit_file",
        default=None,
        help="Location where to write to JUnit xml report file"
    )
    parser.add_option(
        "--split-xunit",
        dest="split_xunit",
        action="store_true",
        help="If you have specified the -x option this option will split the xunit xml file and create one file per feature file; the -x argument specifies the location"
    )
    parser.add_option(
        "-p", "--profile",
        dest="profile",
        default=None,
        help="Define profile"
    )
    parser.add_option(
        "-t", "--with-traceback",
        dest="with_traceback",
        action="store_true",
        help="Print traceback if a step fails"
    )
    parser.add_option(
        "--no-colors",
        dest="no_colors",
        action="store_true",
        help="Do not print in colors"
    )
    parser.add_option(
        "--no-line-jump",
        dest="no_line_jump",
        action="store_true",
        help="Do not jump up lines to rewrite in another color"
    )
    parser.add_option(
        "--no-duration",
        dest="no_duration",
        action="store_true",
        help="Do not print duration after execution"
    )
    parser.add_option(
        "--no-numbers",
        dest="no_numbers",
        action="store_true",
        help="Do not print numbers before feature, scenario and step sentences"
    )
    parser.add_option(
        "--no-indentation",
        dest="no_indentation",
        action="store_true",
        help="Do not print any indentation before sentences"
    )
    parser.add_option(
        "--no-skipped-steps",
        dest="no_skipped_steps",
        action="store_true",
        help="Do not print skipped steps"
    )
    parser.add_option(
        "--with-section-names",
        dest="with_section_names",
        action="store_true",
        help="print section name before feature and scenario sentences"
    )
    parser.add_option(
        "--show-metrics",
        dest="show_metrics",
        action="store_true",
        help="Show metrics of given feature files"
    )

    options, args = parser.parse_args()

    exitCode = 0
    try:
        # initialize config object
        cf = radish.Config()
        cf.no_colors = options.no_colors
        cf.no_line_jump = options.no_line_jump
        cf.SetBasedir(radish.FileSystemHelper.expand(options.basedir))
        cf.feature_files = args
        cf.abort_fail = options.abort_fail
        cf.marker = options.marker
        cf.dry_run = options.dry_run
        cf.xunit_file = options.xunit_file
        cf.split_xunit = options.split_xunit
        cf.profile = options.profile
        cf.no_numbers = options.no_numbers
        cf.no_indentation = options.no_indentation
        cf.no_duration = options.no_duration
        cf.no_skipped_steps = options.no_skipped_steps
        cf.with_section_names = options.with_section_names
        cf.with_traceback = options.with_traceback
        cf.show_metrics = options.show_metrics

        # parse feature files
        fp = radish.FeatureParser()
        fp.parse()

        # load terrain and steps
        loader = radish.Loader(fp.get_features())
        loader.load()

        if cf.show_metrics:  # just get metrics of feature files
            ur = radish.UtilRegistry()
            if ur.has_util("show_metrics"):
                metrics = radish.Metrics(fp.get_features())
                try:
                    return ur.call_util("show_metrics", fp.get_features(), metrics.calculate())
                except KeyboardInterrupt:
                    pass
            else:
                raise radish.NoMetricUtilFoundError()
        else:  # normal run
            # run the features
            runner = radish.Runner(fp.get_features())
            endResult = runner.run()

            # report writer
            if cf.xunit_file:
                xunit = radish.XunitWriter(endResult)
                xunit.generate()

            exitCode = 0 if endResult.have_all_passed() else 1
    except radish.RadishError, e:
        sys.stderr.write("%s %s\n" % (radish.colorful.bold_red("radish error:"), e))
        exitCode = 2

    sys.exit(exitCode)

if __name__ == "__main__":
    main()
