"""
Ax_FuzzyTourney - Basic command-line tournament runner.

This is a basic example of how to run a tournament defined in a 
JSON or YAML file.
It can be run from the command line like:

$ python -m axonchisel.fuzzytourney.util.run example/tourney1.json

You may also wish to run tournaments in other environments and with other 
options by creating your own wrapper to load a tournament, customize the 
runner, and execute it.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2013 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from __future__ import print_function

import sys

import axonchisel.fuzzytourney.config.loader
import axonchisel.fuzzytourney.runner


# ----------------------------------------------------------------------------


class RunUtil(object):
    """Basic bootstrap cmdline tool to load tournament and run it."""
    
    def __init__(self, argv):
        self._argv = argv
        
    def main(self):
        tfname = self._get_tournament_filename()
        tournament = self._load_tournament(tfname)
        self._run_tournament(tournament)

    def _get_verbose_level(self):
        if len(self._argv) > 1:
            vopt = self._argv[1]
            if vopt.startswith("-v"):
                if vopt == "-v2":
                    return 2
                return 1
        return 0

    def _get_tournament_filename(self):
        if len(self._argv) < 2:
            self._print_error("No tournament file specified")
            self._print_usage(sys.stderr)
            sys.exit(1)
        return self._argv[-1]
        
    def _load_tournament(self, tournament_filename):
        with open(tournament_filename, 'rb') as fin:
            if tournament_filename.endswith('.yaml'):
                loader = axonchisel.fuzzytourney.config.loader.Loader_YAML()
            elif tournament_filename.endswith('.json'):
                loader = axonchisel.fuzzytourney.config.loader.Loader_JSON()
            else:
                self._print_error("Unknown tournament file extension in {0}".format(tournament_filename))
                self._print_usage(sys.stderr)
                sys.exit(2)
            loader.set_file(fin)
            loader.set_app_context(self._get_tournament_app_context())
            tournament = loader.load_tournament()
        return tournament

    def _run_tournament(self, tournament):
        runner = axonchisel.fuzzytourney.runner.Runner()
        runner.set_app_context(self._get_tournament_app_context())
        runner.set_status_callback_handler(self._get_run_status_callback())
        runner.run(tournament)

    def _get_tournament_app_context(self):
        return {}

    def _get_run_status_callback(self):
        vlvl = self._get_verbose_level()
        if vlvl == 2:
            return axonchisel.fuzzytourney.runner.RunStatusCallback_BasicDebug()
        elif vlvl == 1:
            return axonchisel.fuzzytourney.runner.RunStatusCallback_Basic()
        else:
            return None
        
    def _print_error(self, msg, *objs):
        print("ERROR:", msg, "...", *objs, file=sys.stderr)

    def _print_usage(self, f):
        print("", file=f)
        print("Ax_FuzzyTourney cmdline runner", file=f)
        print("", file=f)
        print("Run with tournament filename (.json or .yaml)", file=f)
        print("Specify -v or -v2 option first for verbose output", file=f)
        print("", file=f)
        
    

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    runutil = RunUtil(sys.argv)
    runutil.main()
