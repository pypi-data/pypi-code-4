#-*- coding: utf-8 -*-
from __future__ import print_function
import sys
import os
import logging
import re
from types import MethodType

import six

from pyparsing import ParseException

from nose.plugins import Plugin
from nose.plugins.errorclass import ErrorClassPlugin
from nose.selector import TestAddress
from nose.failure import Failure
from nose.util import isclass

from fresher.core import TagMatcher, load_language, load_feature, StepsRunner
from fresher.prettyprint import FresherPrettyPrint
from fresher.stepregistry import StepImplLoader, StepImplRegistry
from fresher.stepregistry import UndefinedStepImpl, StepImplLoadException
from fresher.test.base import FeatureSuite, FresherTestCase, ExceptionWrapper

try:
    # use colorama for cross-platform colored text, if available
    import colorama # pylint: disable=F0401
    colorama.init()
except ImportError:
    colorama = None

log = logging.getLogger('nose.plugins.fresher')

# This line ensures that frames from this file will not be shown in tracebacks
__unittest = 1


class FresherErrorPlugin(ErrorClassPlugin):

    enabled = True

    def options(self, parser, env):
        parser.add_option('--fresher-allow-undefined',
                          action="store_true",
                          default=env.get("NOSE_FRESHER_ALLOW_UNDEFINED") == '1',
                          dest="allow_undefined",
                          help="Allow undefined steps."
                          "[NOSE_FRESHER_ALLOW_UNDEFINED]")

    def configure(self, options, config):
        super(FresherErrorPlugin, self).configure(options, config)
        if options.list_undefined:
            options.allow_undefined = True
        # This bypasses the 'attr = ErrorClass(...)' method of declaring error
        # classes.
        FresherErrorPlugin.errorClasses = \
            ((UndefinedStepImpl,
              ("undefined", "UNDEFINED", not options.allow_undefined)), )



class StepsLoadFailure(Failure):

    def __str__(self):
        return "Could not load steps for %s" % self.address()

class ParseFailure(Failure):

    def __init__(self, parse_exception, tb, filename):
        self.parse_exception = parse_exception
        self.filename = filename
        address = TestAddress(filename).totuple()
        super(ParseFailure, self).__init__(parse_exception.__class__, parse_exception, tb, address)

    def __str__(self):
        return "Could not parse %s" % (self.filename)

class FresherNosePlugin(Plugin):

    name = "fresher"

    # This makes it so that fresher's formatFailure gets called before capture
    # and logcapture - those plugins replace and obscure the true exception value
    score = 1000

    def options(self, parser, env):
        super(FresherNosePlugin, self).options(parser, env)

        parser.add_option('--fresher-tags', action='store',
                          dest='tags',
                          default=env.get('NOSE_FRESHER_TAGS'),
                          help="Run only those scenarios and features which "
                               "match the given tags. Should be a comma-separated "
                               "list. Each tag can be prefixed with a ~ to negate "
                               "[NOSE_FRESHER_TAGS]")
        parser.add_option('--fresher-language',
                          action="store",
                          dest='language',
                          default='en',
                          help='Change the language used when reading the feature files')
        parser.add_option('--fresher-list-undefined',
                          action="store_true",
                          default=env.get('NOSE_FRESHER_LIST_UNDEFINED') == '1',
                          dest="list_undefined",
                          help=("Make a report of all undefined steps that "
                                "fresher encounters when running scenarios. "
                                "(Implies --fresher-allow-undefined.) "
                               "[NOSE_FRESHER_LIST_UNDEFINED]"))

    def configure(self, options, config):
        super(FresherNosePlugin, self).configure(options, config)
        all_tags = options.tags.split(",") if options.tags else []
        self.tagmatcher = TagMatcher(all_tags)
        self.language = load_language(options.language)
        self.impl_loader = StepImplLoader()
        self.topdir = os.getcwd()
        if not self.language:
            print("Error: language '%s' not available" % options.language, file=sys.stderr)
            exit(1)
        if options.list_undefined:
            self.undefined_steps = []
        else:
            self.undefined_steps = None
        self._test_class = None

    def wantDirectory(self, dirname):
        if not os.path.exists(os.path.join(dirname, ".fresherignore")):
            return True
        return None

    def wantFile(self, filename):
        return filename.endswith(".feature") or None

    def _makeTestClass(self, feature, scenario):
        """Chooses the test base class appropriate
        for the given feature.

        This method supports late import of the
        test base class so that userspace code (e.g.
        in the support environment) can configure
        the test framework first (e.g. in the case
        of twisted tests to install a custom
        reactor implementation).

        The current simplistic implementation chooses
        a twisted-enabled test class if twisted is
        present and returns a PyUnit-based test otherwise.

        In the future this can be extended to support
        more flexible (e.g. user-defined) test classes
        on a per-feature basis."""
        if self._test_class is None:
            try:
                from fresher.test.async import TwistedTestCase
                self._test_class = TwistedTestCase
            except ImportError:
                from fresher.test.pyunit import PyunitTestCase
                self._test_class = PyunitTestCase
        name = feature.name.encode('utf8') if not six.PY3 else feature.name
        return type(name, (self._test_class, ),
                    {scenario.name: lambda self: self.runScenario()})


    def loadTestsFromFile(self, filename, indexes=[]):
        log.debug("Loading from file %s" % filename)

        step_registry = StepImplRegistry(TagMatcher)
        try:
            feat = load_feature(filename, self.language)
            path = os.path.dirname(filename)
        except ParseException as e:
            _, _, tb = sys.exc_info()
            yield ParseFailure(e, tb, filename)
            return

        try:
            self.impl_loader.load_steps_impl(step_registry, self.topdir,
                                             path, feat.use_step_defs)
        except StepImplLoadException as e:
            yield StepsLoadFailure(address=TestAddress(filename), *e.exc)
            return

        cnt = 0
        ctx = FeatureSuite()
        for i, sc in enumerate(feat.iter_scenarios()):
            if (not indexes or (i + 1) in indexes):
                if self.tagmatcher.check_match(sc.tags + feat.tags):
                    test_class = self._makeTestClass(feat, sc)
                    yield test_class(StepsRunner(step_registry), step_registry, feat, sc, ctx)
                    cnt += 1

        if not cnt:
            yield False

    def loadTestsFromName(self, name, _=None):
        log.debug("Loading from name %s" % name)

        if not self._is_file_with_indexes(name):
            return # let nose take care of it

        name_without_indexes, indexes = self._split_file_in_indexes(name)
        if not os.path.exists(name_without_indexes):
            return

        if os.path.isfile(name_without_indexes) \
           and name_without_indexes.endswith(".feature"):
            for tc in self.loadTestsFromFile(name_without_indexes, indexes):
                yield tc

    def _is_file_with_indexes(self, name):
        drive, tail = os.path.splitdrive(name)
        if ":" not in tail:
            return False
        else:
            return True

    def _split_file_in_indexes(self, name_with_indexes):
        drive, tail = os.path.splitdrive(name_with_indexes)
        parts = tail.split(":")
        name_without_indexes = drive + parts.pop(0)
        indexes = []
        indexes = set(int(p) for p in parts)
        return (name_without_indexes, indexes)

    def describeTest(self, test):
        if isinstance(test.test, FresherTestCase):
            return test.test.description

    def formatFailure(self, test, err):
        if hasattr(test, 'test') and isinstance(test.test, FresherTestCase):
            ec, ev, tb = err
            if ec is ExceptionWrapper and isinstance(ev, Exception):
                orig_ec, orig_ev, orig_tb = ev.e
                message = "%s\n\n%s" % (str(orig_ev), self._formatSteps(test, ev.step))
                return (orig_ec, Exception(message), orig_tb)
            elif not ec is UndefinedStepImpl and hasattr(test.test, 'last_step'):
                message = "%s\n\n%s" % (str(ev), self._formatSteps(test, test.test.last_step))
                return (ec, Exception(message), tb)
            elif ec is UndefinedStepImpl and hasattr(test.test, 'last_step'):
                # Create a new instance that will not have a traceback.
                # Otherwise, Python 3 insists on printing the traceback.
                return (ec, UndefinedStepImpl(ev.step), None)

        return err

    formatError = formatFailure

    def prepareTestResult(self, result):
        # Patch the result handler with an addError method that saves
        # UndefinedStepImpl exceptions for reporting later.
        if self.undefined_steps is not None:
            plugin = self
            def _addError(self, test, err):
                ec, ev, tb = err
                if isclass(ec) and issubclass(ec, UndefinedStepImpl):
                    plugin.undefined_steps.append((test, ec, ev, tb))
                self._old_addError(test, err)
            result._old_addError = result.addError
            result.addError = MethodType(_addError, result)

    def report(self, stream):
        if self.undefined_steps:
            stream.write("======================================================================\n")
            stream.write("Tests with undefined steps\n")
            stream.write("----------------------------------------------------------------------\n")
            for test, ec, ev, tb in self.undefined_steps:
                stream.write(self._formatSteps(test, ev.step, False) + "\n\n")
            stream.write("You can implement step definitions for the missing steps with these snippets:\n\n")
            uniq_steps = set(s[2].step for s in self.undefined_steps)
            for step in uniq_steps:
                stream.write('@%s(r"^%s$")\n' % (self.language.words(step.step_type)[0],
                                                 step.match))
                stream.write('def %s_%s():\n' % (step.step_type,
                                                 re.sub('[^\w]', '_', step.match).lower()))
                stream.write('    # code here\n\n')

    def _formatSteps(self, test, failed_step, failure=True):
        ret = []
        ret.append(FresherPrettyPrint.feature(test.test.feature))
        ret.append(FresherPrettyPrint.scenario(test.test.scenario))
        found = False
        for step in test.test.scenario.iter_steps():
            if step == failed_step:
                found = True
                if failure:
                    ret.append(FresherPrettyPrint.step_failed(step))
                else:
                    ret.append(FresherPrettyPrint.step_undefined(step))
            elif found:
                ret.append(FresherPrettyPrint.step_notrun(step))
            else:
                ret.append(FresherPrettyPrint.step_passed(step))
        return "\n".join(ret)
