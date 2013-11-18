# -*- coding: utf-8 -*-

import sys
import traceback

from radish.config import Config
from radish.colorful import colorful
from radish.hookregistry import HookRegistry
from radish.endresult import EndResult


class Runner(object):
    def __init__(self, features):
        self._features = features

    def run(self):
        abort = False
        interrupted = False

        hr = HookRegistry()
        e = hr.call_hook("before", "all")
        if e is not None:
            self._print_traceback(e)
            abort = True

        if not abort:
            for f in self._features:
                e = hr.call_hook("before", "feature", f)
                if e is not None:
                    self._print_traceback(e)
                    return self._create_endresult()

                for s in f.get_scenarios():
                    e = hr.call_hook("before", "scenario", s)
                    if e is not None:
                        self._print_traceback(e)
                        return self._create_endresult()
                    skip_remaining_steps = False

                    for step in s.get_steps():
                        e = hr.call_hook("before", "step", step)
                        if e is not None:
                            self._print_traceback(e)
                            return self._create_endresult()

                        if not skip_remaining_steps and not interrupted:
                            try:
                                passed = step.run()
                                if not passed and not Config().dry_run:
                                    skip_remaining_steps = True
                                    if Config().abort_fail:
                                        abort = True
                            except KeyboardInterrupt:
                                interrupted = True
                                sys.stdout.write("\r")

                        e = hr.call_hook("after", "step", step)
                        if e is not None:
                            self._print_traceback(e)
                            return self._create_endresult()
                    e = hr.call_hook("after", "scenario", s)
                    if e is not None:
                        self._print_traceback(e)
                        return self._create_endresult()
                    if abort:  # if -a is set
                        break
                e = hr.call_hook("after", "feature", f)
                if e is not None:
                    self._print_traceback(e)
                    return self._create_endresult()
                if abort:  # if -a is set
                    break
        return self._create_endresult()

    def _print_traceback(self, fail_reason):
        print(colorful.bold_red(fail_reason.get_name()) + colorful.red(" exception caught from external hook at ") + colorful.bold_red(fail_reason.get_filename()) + colorful.red(":") + colorful.bold_red(fail_reason.get_line_no()))
        if Config().with_traceback:
            for l in fail_reason.get_traceback().splitlines():
                colorful.out.red("  " + l)
        else:
            print("  " + colorful.red(fail_reason.get_name() + ": ") + colorful.bold_red(fail_reason.get_reason()))
        sys.stdout.write("\n")

    def _create_endresult(self):
        endResult = EndResult(self._features)
        e = HookRegistry().call_hook("after", "all", endResult)
        if e is not None:
            self._print_traceback(e)
        return endResult
