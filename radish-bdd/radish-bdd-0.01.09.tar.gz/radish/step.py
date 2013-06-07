# -*- coding: utf-8 -*-

import traceback
import inspect
import sys
import datetime
import re

from lxml import etree

from radish.config import Config
from radish.utilregistry import UtilRegistry
from radish.exceptions import ValidationError


class Step(object):
    CHARS_PER_LINE = 100

    def __init__(self, id, scenario, sentence, filename, line_no):
        self._id = id
        self._scenario = scenario
        self._sentence = sentence
        self._filename = filename
        self._line_no = line_no
        self._function = None
        self._metric_indicators = None
        self._match = None
        self._passed = None
        self._fail_reason = None
        self._starttime = None
        self._endtime = None
        self._validation_error = False

    def get_id(self):
        return self._id

    def get_scenario(self):
        return self._scenario

    def get_line_no(self):
        return self._line_no

    def get_sentence(self):
        return self._sentence

    def get_sentence_splitted(self):
        ur = UtilRegistry()
        if ur.has_util("split_sentence"):
            try:
                return ur.call_util("split_sentence", self)
            except KeyboardInterrupt:
                pass
        splitted = [self._sentence[i:i + Step.CHARS_PER_LINE] for i in range(0, len(self._sentence), Step.CHARS_PER_LINE)]
        if Config().no_indentation:
            return len(splitted), "\n".join(splitted)
        return len(splitted), ("\n" + self.get_sentence_indentation()).join(splitted)

    def get_filename(self):
        return self._filename

    def get_indentation(self):
        return "  " + " " * (len(str(Config().highest_feature_id)) + len(str(Config().highest_scenario_id))) + "    "

    def get_sentence_indentation(self):
        return self.get_indentation() + " " * len(str(Config().highest_step_id)) + "  "

    def is_dry_run(self):
        return Config().dry_run

    def get_function(self):
        return self._function

    def set_function(self, function):
        self._function = function

    def get_metric_indicators(self):
        return self._metric_indicators

    def set_metric_indicators(self, metric_indicators):
        self._metric_indicators = metric_indicators

    def get_match(self):
        return self._match

    def set_match(self, match):
        self._match = match

    def has_passed(self):
        return self._passed

    def get_duration(self):
        if self._passed is True or self._passed is False:
            td = self._endtime - self._starttime
            return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 1e6) / 1e6
        return 0

    def get_fail_reason(self):
        return self._fail_reason

    class FailReason(object):
        def __init__(self, e):
            self._exception = e
            self._reason = unicode(str(e), "utf-8")
            self._traceback = traceback.format_exc(e)
            self._name = e.__class__.__name__

        def get_reason(self):
            return self._reason

        def get_traceback(self):
            return self._traceback

        def get_name(self):
            return self._name

    def run(self):
        kw = self._match.groupdict()
        try:
            self._starttime = datetime.datetime.now()
            if kw:
                self._function(self, **kw)
            else:
                self._function(self, *self._match.groups())
            self._passed = not self._validation_error
        except KeyboardInterrupt:
            raise
        except Exception, e:
            self._passed = False
            self._fail_reason = Step.FailReason(e)
            if self.is_dry_run():
                caller = inspect.trace()[-1]
                sys.stderr.write("%s:%d: error: %s\n" % (caller[1], caller[2], self._fail_reason.get_reason().encode("utf-8")))
        self._endtime = datetime.datetime.now()
        return self._passed

    def ValidationError(self, msg):
        self._validation_error = True
        if self.is_dry_run():
            sys.stderr.write("%s:%d: error: %s\n" % (self._filename, self._line_no, msg))
        else:
            raise ValidationError(msg)

    def get_report_as_xunit_tag(self):
        testcase = etree.Element(
            "testcase",
            classname="%s/%s" % (self._scenario.get_feature().get_sentence().replace("/", "\/"), self._scenario.get_sentence().replace("/", "\/")),
            name=self._sentence,
            time=str(self.get_duration())
        )
        if self._passed is False:
            failure = etree.Element(
                "failure",
                type=self._fail_reason.get_name(),
                message=self._strip_ansi_text(self._fail_reason.get_reason())
            )
            failure.text = etree.CDATA(self._strip_ansi_text(self._fail_reason.get_traceback()))
            testcase.append(failure)
        return testcase

    # FIXME: register this methods somewhere as util
    def _strip_ansi_text(self, text):
        pattern = re.compile("(\\033\[\d+(?:;\d+)*m)")
        return pattern.sub("", text)
