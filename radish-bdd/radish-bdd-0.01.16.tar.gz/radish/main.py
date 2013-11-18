#!/usr/bin/python
# -*- coding: utf-8 -*-

import radish

import os
import sys
import time
import shutil

from docopt import docopt


def main():
    """
Usage:
    radish <features>...
           [-b=<basedir> | --basedir=<basedir>]
           [-m=<marker> | --marker=<marker>] [-p=<profile> | --profile=<profile>]
           [-d | --dry-run] [-a | --abort-fail]
           [-t | --with-traceback]
           [-x=<output> | --xunit-file=<output> [--split-xunit]]
           [--no-colors] [--no-line-jump] [--no-overwrite]
           [--no-indentation] [--no-duration] [--no-numbers]
           [--no-skipped-steps] [--with-section-names]
           [--show-metrics]
    radish (-c | --create-basedir)  [-b=<basedir> | --basedir=<basedir>]
    radish (-h | --help)
    radish (-v | --version)

Arguments:
    features                             feature files to run

Options:
    -h --help                            show this screen
    -v --version                         show version

    -c --create-basedir                  create basedir and initial steps and terrain files
    -b=<basedir> --basedir=<basedir>     set base dir from where the step.py and terrain.py will be loaded [default: $PWD/radish]
    -m=<marker> --marker=<marker>        specific marker which you can use to implement some kind of logging delimitiers [default: time.time()]
    -d --dry-run                         execute a dry run to validate steps
    -a --abort-fail                      abort run if one step fails
    -p=<profile> --profile=<profile>     define porfile which you can use in your step implementation
    -t --with-traceback                  print traceback if a step fails

    -x=<output> --xunit-file=<output>    generate xunit file after run at specific location
    --split-xunit                        split the xunit file into multiple files - one file per inputted feature file

    --no-colors                          do not print in colors
    --no-line-jump                       do not jump up lines to rewrite in another color
    --no-overwrite                       do not overwrite step
    --no-duration                        do not print duration after run
    --no-numbers                         do not print numbers before feature, scenario and step sentences
    --no-indentation                     do not print any indentation before sentences
    --no-skipped-steps                   do not print skipped steps
    --with-section-names                 print section name before feature and scenario sentences

    --show-metrics                       show metrics of given feature files after run

(C) Copyright 2013 by Timo Furrer <tuxtimo@gmail.com>"""

    arguments = docopt("radish %s\n%s" % (radish.version.__version__, main.__doc__), version=radish.version.__version__)

    cf = radish.Config()
    cf.no_colors = arguments["--no-colors"]

    if arguments['--create-basedir']:
        datadir = os.path.join(radish.__path__[0], "..")
        basedir = radish.FileSystemHelper.expand(arguments["--basedir"])
        if os.path.exists(basedir):
            print("basedir already exists: %s" % basedir)
        else:
            print "creating %s" % basedir
            os.mkdir(basedir)

        filename = "%s/steps.py" % basedir
        if os.path.exists(filename):
            print("file already exists: %s" % filename)
        else:
            print("creating %s" % filename)
            shutil.copyfile(os.path.join(datadir, "steps.py"), filename)

        filename = "%s/terrain.py" % basedir
        if os.path.exists(filename):
            print("file already exists: %s" % filename)
        else:
            print("creating %s" % filename)
            shutil.copyfile(os.path.join(datadir, "terrain.py"), filename)

        sys.exit(0)

    exitCode = 0
    try:
        # initialize config object
        # FIXME: clean up config and arguments
        cf.no_line_jump = arguments["--no-line-jump"]
        cf.SetBasedir(radish.FileSystemHelper.expand(os.path.join(os.getcwd(), "radish") if arguments["--basedir"] == "$PWD/radish/" else arguments["--basedir"]))
        cf.feature_files = arguments["<features>"]
        cf.abort_fail = arguments["--abort-fail"]
        cf.marker = time.time() if arguments["--marker"] == "time.time()" else arguments["--marker"]
        cf.create_basedir = arguments["--create-basedir"]
        cf.dry_run = arguments["--dry-run"]
        cf.xunit_file = arguments["--xunit-file"]
        cf.split_xunit = arguments["--split-xunit"]
        cf.profile = arguments["--profile"]
        cf.no_numbers = arguments["--no-numbers"]
        cf.no_indentation = arguments["--no-indentation"]
        cf.no_overwrite = arguments["--no-overwrite"]
        cf.no_duration = arguments["--no-duration"]
        cf.no_skipped_steps = arguments["--no-skipped-steps"]
        cf.with_section_names = arguments["--with-section-names"]
        cf.with_traceback = arguments["--with-traceback"]
        cf.show_metrics = arguments["--show-metrics"]

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
        e.show()
        exitCode = 2

    sys.exit(exitCode)
