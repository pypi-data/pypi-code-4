# -*- coding: utf-8 -*-

# exercise_generator.py --- Generate exercises
# Copyright (c) 2011, 2012, 2013 Florent Rougon
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 51 Franklin St, Fifth Floor,
# Boston, MA  02110-1301 USA.


import sys, locale, random, operator, logging, collections, functools
from PyQt4 import QtCore
translate = QtCore.QCoreApplication.translate

from . import fch_util
from .conjugations.fr_FR import conj_subjects, conj, used_tenses, \
    instruction as conj_instr


def setup_logging(level=logging.NOTSET, chLevel=None):
    global logger

    if chLevel is None:
        chLevel = level

    logger = logging.getLogger('flo_check_homework.exercise_generator')
    logger.setLevel(level)
    # Create console handler and set its level
    ch = logging.StreamHandler() # Uses sys.stderr by default
    ch.setLevel(chLevel)  # NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
    # Logger name with :%(name)s... many other things available
    formatter = logging.Formatter("%(levelname)s %(message)s")
    # Add formatter to ch
    ch.setFormatter(formatter)
    # Add ch to logger
    logger.addHandler(ch)

setup_logging()


# *Not* useful for l10n, because of known shortcomings of QObject.tr() in PyQt
# app = QtCore.QCoreApplication.instance()


class Seen(set):
    """Class used to store question items.

    This class is used to remember the questions asked during a
    session, in order to avoid asking the same question twice in the
    same session. The elements are supposed to be valid "items" for
    ItemGenerator instances (or related objects), i.e., typically
    tuples (for instance, the operands of a calculus).

    """
    pass

class ItemGenerator(object):
    def __init__(self, register_cleanup_handler, items_key,
                 cursor_key, needswork_key, *, disable_needswork=False,
                 seen=None, qsettings=None):
        self.items_key = items_key
        self.cursor_key = cursor_key
        self.needswork_key = needswork_key
        self.disable_needswork = disable_needswork
        self.qsettings = qsettings or QtCore.QSettings()
        # Flag:  True when the persistent variables have been modified after
        # the last time they were saved by self.qsettings.
        self.dirty = False

        self.init_master_vars()
        self.load_persistent_vars() # Needs self.qsettings
        self.seen = seen if seen is not None else Seen()

        # Qt waits for the timer callback function to terminate before
        # processing QCoreApplication.aboutToQuit (and probably any other
        # event), therefore there is no need for a lock in
        # self.save_persistent_vars*.
        self.qtimer = QtCore.QTimer()
        self.qtimer.timeout.connect(self.save_persistent_vars_if_modified)
        self.qtimer.start(1000)

        # To be run on program exit
        register_cleanup_handler(self.save_persistent_vars_if_modified)

    def loadOrInitSetting(self, *args, **kwargs):
        return fch_util.loadOrInitSetting(self.qsettings, *args, **kwargs)

    def loadOrInitIntSetting(self, *args, **kwargs):
        return fch_util.loadOrInitIntSetting(self.qsettings, *args, **kwargs)

    def init_master_vars(self):
        """Initialize variables that are needed to compute an items list.

        This method may access self.qsettings. The default
        implementation does nothing.

        """
        return

    def compute_items_list(self):
        """Must be implemented by every subclass and return the list."""
        raise NotImplementedError("This method must be overriden by "
                                  "each subclass")

    def initialize_new_items_table(self, items_list):
        """Setup a new items table from 'items_list'.

        This may or may not require shuffling 'items_list'.
        'items_list' may be used and modified in-place, considering
        the current implementation of self.load_persistent_vars().

        """
        self.items = items_list
        random.shuffle(self.items)

        self.dirty = True

    def is_consistent(self, items_list):
        # This tests whether self.items and items_list have the same
        # elements, regardless of the order.
        return frozenset(self.items) == frozenset(items_list)

    def load_persistent_vars(self):
        """Load or initialize self.items, self.cursor and self.needswork.

        Prior initialization should be done by overriding
        self.init_master_vars()."""
        # Unless both self.items and self.cursor are set, self.cursor
        # must be set to 0.
        if not (self.qsettings.contains(self.items_key)
                and self.qsettings.contains(self.cursor_key)):
            self.cursor = 0
        else:
            # The default value would be used in case the value set
            # in the file can't be converted to an integer...
            self.cursor = self.loadOrInitIntSetting(self.cursor_key, 0)

        # Up-to-date list of possible items; it is used to initialize
        # self.items if necessary and check its consistency with
        # other parameters if self.items was loaded from the config file.
        items_list = self.compute_items_list()

        if self.qsettings.contains(self.items_key):
            # No need to compute a new table in this case
            self.items = self.loadOrInitSetting(self.items_key)

            if not self.disable_needswork:
                self.needswork = collections.deque(
                    self.loadOrInitSetting(self.needswork_key, []))

            if not self.is_consistent(items_list):
                logger.info("Items table %s is inconsistent with other "
                "variables, resetting persistent vars", self.items_key)
                self.reset_persistent_vars(items_list)
        else:
            self.reset_persistent_vars(items_list)

        self.dirty = True

    def reset_persistent_vars(self, items_list):
        """Reset self.items, self.cursor and self.needswork."""
        self.initialize_new_items_table(items_list)
        # The new items table may be too small for self.cursor, reset it.
        self.cursor = 0

        # The tables may have changed; needswork may be inconsistent with
        # the new self.items. Therefore, reset it.
        if not self.disable_needswork:
            self.needswork = collections.deque()
        self.dirty = True

    def save_persistent_vars(self, sync=False):
        """Save self.items, self.cursor and self.needswork to self.qsettings."""
        for name in ("items",):
            self.qsettings.setValue(
                getattr(self, "%s_key" % name),
                repr(getattr(self, name)))

        # Now that self.needswork is implemented as a deque, it needs special
        # treatment.
        if not self.disable_needswork:
            self.qsettings.setValue(self.needswork_key,
                                    repr(list(self.needswork)))

        # Simple integer, stored as is
        self.qsettings.setValue(self.cursor_key, self.cursor)
        self.dirty = False

        if sync:
            self.qsettings.sync()

        return True

    @QtCore.pyqtSlot(result=bool)
    def save_persistent_vars_if_modified(self):
        if self.dirty:
            res = self.save_persistent_vars()
        else:
            res = False

        return res

    def canonicalized(self, t):
        """Return the canonicalized form of an item.

        The canonicalized form is the one stored in self.needswork
        and Seen objects and used for membership testing in Seen
        objects.

        For instance, if (x, y) and (y, x) are to be treated equally,
        this method could be defined to return ((min(t), max(t)).

        """
        return t

    def alreadySeen(self, t):
        return (self.canonicalized(t) in self.seen)

    def add_to(self, l, t):
        if not self.canonicalized(t) in l:
            l.append(self.canonicalized(t))
            self.dirty = True

    def add_to_needswork(self, t):
        if not self.disable_needswork:
            self.add_to(self.needswork, t)

    def pop_from_needswork(self):
        """Pop an item from self.needswork for serving to the user.

        Subclasses may want to override this method with one that
        randomly swaps the item components, for instance.

        """
        return self.needswork.popleft()

    def gen_items(self, nb_items):
        return [ self.gen_item() for i in range(nb_items) ]

    def gen_item(self):
        # If all items from self.items have been seen in the current
        # session, reset self.seen, otherwise we'll be looping
        # forever looking for a new item...
        for t in self.items:
            if not self.alreadySeen(t):
                break
        else:
            logger.debug("Clearing self.seen")
            # in-place operation, as the object may be shared by several item
            # generators
            self.seen.clear()

        # First of all, pop the items from self.needswork (if any) unless they
        # have already been seen in the current session.
        if (not self.disable_needswork) and self.needswork \
                and not self.alreadySeen(self.needswork[0]):
            logger.debug("Popping %s from needswork = %s" %
                         (self.needswork[0], list(self.needswork)))
            res = self.pop_from_needswork()
        else:
            # Skip all operations already seen in the current session
            while self.alreadySeen(self.items[self.cursor]):
                self.cursor = (self.cursor + 1) % len(self.items)
                if self.cursor == 0:
                    random.shuffle(self.items)

            res = self.items[self.cursor]

            # Advance cursor to the next position
            self.cursor = (self.cursor + 1) % len(self.items)
            if self.cursor == 0:
                random.shuffle(self.items)

        self.seen.add(self.canonicalized(res))
        self.dirty = True       # Because of self.cursor and self.needswork

        return res

    def __iter__(self):
        while True:
            yield self.gen_item()


# ****************************************************************************
# *                   Base classes for Question generators                   *
# ****************************************************************************

# "Question generator": iterable that yields Question instances (or instances
# of a subclass of Question)

class CommutativeOpGenerator(ItemGenerator):
    """Question generator suitable for commutative binary operators.

    Tailored for multiplication but also suitable for addition or
    other commutative binary operators.

    For each (x, y) couple with x and y in self.tables, self.items
    will contain:
      - (x, y) exactly once if x == y;
      - (x, y) and (y, x) exactly once each otherwise.

    If x != y, (x, y) and (y, x) are treated the same as far as
    self.seen and self.needswork are concerned, which means that:
      - (x, y) and (y, x) won't be both proposed in the same session
        unless the session is so long that all other items have been
        exhausted.
      - if a mistake is made for (x, y), it will be served again in
        priority after the current session, but maybe as (y, x), not
        necessarily as (x, y).

    """
    def __init__(self, register_cleanup_handler,
                 tables_key, items_key, cursor_key, needswork_key,
                 operator, operator_for_print, qDesc, *,
                 disable_needswork=False, seen=None, qsettings=None):
        # Needed for init_master_vars(), called by the parent constructor
        self.tables_key = tables_key

        super().__init__(
            register_cleanup_handler, items_key, cursor_key,
            needswork_key, disable_needswork=disable_needswork,
            seen=seen, qsettings=qsettings)

        self.operator = operator
        self.operator_for_print = operator_for_print
        self.qDesc = qDesc

    def init_master_vars(self):
        # Get/initialize the list of tables to work on (making sure it is set
        # in the config file)
        self.tables = self.loadOrInitSetting(
            self.tables_key, list(range(2, 10)))

    def compute_items_list(self):
        l = []
        for x in self.tables:
            for y in range(2, 10):
                if y in self.tables:
                    l.append((x, y))
                else:
                    l.extend([(x, y), (y, x)])

        return l

    def canonicalized(self, t):
        return (min(t), max(t))

    def pop_from_needswork(self):
        """Pop a tuple from self.needswork for serving to the user.

        Since (x, y) tuples are always stored in self.needswork with
        x < y, this method randomly swaps the tuple components.

        """
        x, y = self.needswork.popleft()
        return random.choice(((x, y), (y, x)))

    def gen_question(self):
        return ArithmeticCalculus(
            self.qDesc, self.gen_item(), self.operator, self.operator_for_print,
            self)

    def __iter__(self):
        while True:
            yield self.gen_question()


def binop_with_spacing(s):
    return "\N{MEDIUM MATHEMATICAL SPACE}" + s + "\N{MEDIUM MATHEMATICAL SPACE}"

class DirectMultTablesGenerator(CommutativeOpGenerator):
    """Question generator for multiplication tables"""
    def __init__(self, register_cleanup_handler,
                 tables_key="DirectMultTables/Tables",
                 items_key="DirectMultTables/Items",
                 cursor_key="DirectMultTables/Cursor",
                 needswork_key="DirectMultTables/NeedsWork",
                 operator=operator.mul,
                 operator_for_print=binop_with_spacing('×'),
                 qDesc="multiplication", *,
                 disable_needswork=False, seen=None, qsettings=None):
        super().__init__(
            register_cleanup_handler, tables_key, items_key, cursor_key,
            needswork_key, operator, operator_for_print, qDesc,
            disable_needswork=disable_needswork, seen=seen, qsettings=qsettings)


class DirectAddTablesGenerator(CommutativeOpGenerator):
    """Question generator for addition tables"""
    def __init__(self, register_cleanup_handler,
                 tables_key="DirectAddTables/Tables",
                 items_key="DirectAddTables/Items",
                 cursor_key="DirectAddTables/Cursor",
                 needswork_key="DirectAddTables/NeedsWork",
                 operator=operator.add,
                 operator_for_print=binop_with_spacing('+'),
                 qDesc="addition", *,
                 disable_needswork=False, seen=None, qsettings=None):
        super().__init__(
            register_cleanup_handler, tables_key, items_key, cursor_key,
            needswork_key, operator, operator_for_print, qDesc,
            disable_needswork=disable_needswork, seen=seen, qsettings=qsettings)


class BasicSubstractionGenerator(ItemGenerator):
    """Question generator for working with basic substractions"""
    def __init__(self, register_cleanup_handler,
                 items_key="BasicSubstraction/Items",
                 cursor_key="BasicSubstraction/Cursor",
                 needswork_key="BasicSubstraction/NeedsWork",
                 operator=operator.sub,
                 operator_for_print=binop_with_spacing('−'),
                 qDesc="substraction", *,
                 disable_needswork=False, seen=None, qsettings=None):
        super().__init__(
            register_cleanup_handler, items_key, cursor_key,
            needswork_key, disable_needswork=disable_needswork, seen=seen,
            qsettings=qsettings)

        self.operator = operator
        self.operator_for_print = operator_for_print
        self.qDesc = qDesc

    def compute_items_list(self):
        l = []
        for x in range(4, 21):
            for y in range(2, x-1):
                l.append((x, y))

        return l

    def gen_question(self):
        return ArithmeticCalculus(
            self.qDesc, self.gen_item(), self.operator, self.operator_for_print,
            self)

    def __iter__(self):
        while True:
            yield self.gen_question()


class RandomAdditionGenerator(object):
    """Random addition generator.

    This generator doesn't store all items in a file and is therefore
    well suited for working with not-very-small numbers.

    """
    def __init__(self, m, M, seen=None):
        self.min = m
        self.max = M
        self.operator = operator.add
        self.operator_for_print = binop_with_spacing('+')
        self.qDesc = "addition"
        self.seen = seen if seen is not None else Seen()

    def gen_item(self):
        for i in range(2):
            for j in range(200):
                a = random.randint(self.min, self.max)
                b = random.randint(self.min, self.max)

                # Don't consider already seen items
                if (a, b) in self.seen:
                    continue

                self.seen.add((a, b))
                return (a, b)

            logger.info(
                "Too many collisions in %s.gen_item(), clearing self.seen"
                % self.__class__.__name__)
            self.seen.clear()

        assert False, "Unable to generate a random addition item, aborting"

    def gen_question(self):
        return ArithmeticCalculus(
            self.qDesc, self.gen_item(), self.operator, self.operator_for_print,
            score=1.5)

    def __iter__(self):
        while True:
            yield self.gen_question()


class RandomSubstractionGenerator(object):
    """Random substraction generator.

    This generator doesn't store all items in a file and is therefore
    well suited for working with not-very-small numbers.

    """
    def __init__(self, m, M, deltamin=2, positive=True, seen=None):
        assert M - m >= deltamin, (M, m, deltamin)

        self.min = m
        self.max = M
        self.deltamin = deltamin
        self.operator = operator.sub
        self.operator_for_print = binop_with_spacing('−')
        self.qDesc = "substraction"
        self.positive = positive
        self.seen = seen if seen is not None else Seen()

    def gen_item(self):
        for i in range(2):
            for j in range(200):
                if self.positive:
                    b = random.randint(self.min + self.deltamin, self.max)
                    a = random.randint(self.min, b - self.deltamin)
                else:
                    a = random.randint(self.min, self.max)
                    b = random.randint(self.min, self.max)

                # Don't consider too easy items nor already seen ones
                if abs(b - a) < self.deltamin or ((b, a) in self.seen):
                    continue

                self.seen.add((b, a))
                return (b, a)

            logger.info(
                "Too many collisions in %s.gen_item(), clearing self.seen"
                % self.__class__.__name__)
            self.seen.clear()

        assert False, "Unable to generate a random substraction item, aborting"

    def gen_question(self):
        return ArithmeticCalculus(
            self.qDesc, self.gen_item(), self.operator, self.operator_for_print,
            score=1.5)

    def __iter__(self):
        while True:
            yield self.gen_question()


class EuclidianDivisionGenerator(ItemGenerator):
    """Question generator for divisions."""
    def __init__(self, register_cleanup_handler,
                 tables_key="EuclidianDivision/DivisorsTables",
                 items_key="EuclidianDivision/DivisorsItems",
                 cursor_key="EuclidianDivision/DivisorsCursor",
                 needswork_key="EuclidianDivision/DivisorsNeedsWork",
                 operator=divmod, *, avoid_zero_remainder=True,
                 disable_needswork=False, seen=None, couplesSeen=None,
                 qsettings=None):
        # Needed for init_master_vars(), called by the parent constructor
        self.tables_key = tables_key

        super().__init__(
            register_cleanup_handler, items_key, cursor_key,
            needswork_key, disable_needswork=disable_needswork, seen=seen,
            qsettings=qsettings)

        self.operator = operator
        self.qDesc = "euclidian division"
        self.couplesSeen = couplesSeen if couplesSeen is not None else Seen()
        self.minDividend = 10**3
        self.maxDividend = 10**5 - 1
        self.avoid_zero_remainder = avoid_zero_remainder

    def init_master_vars(self):
        # Get/initialize the list of divisors to work with (making sure it is
        # set in the config file)
        self.tables = self.loadOrInitSetting(
            self.tables_key, list(range(2, 10)))

    def compute_items_list(self):
        l = self.tables[:]
        random.shuffle(l)

        return l

    def gen_item(self):
        # All divisors will be tried before we give up
        for h in range(2):
            for i in range(len(self.items)):
                divisor = super().gen_item()
                for j in range(200):
                    dividend = random.randint(self.minDividend,
                                              self.maxDividend)

                    if (dividend, divisor) in self.couplesSeen \
                            or (self.avoid_zero_remainder \
                                    and (dividend % divisor) == 0):
                        continue

                    self.couplesSeen.add((dividend, divisor))
                    return (dividend, divisor)

            logger.info(
             "Too many collisions in %s.gen_item(), clearing self.couplesSeen"
                % self.__class__.__name__)
            self.couplesSeen.clear()

        assert False, "Unable to generate a random euclidian division item, " \
            "aborting"

    def gen_question(self):
        return EuclidianDivision(self.qDesc, self.gen_item(), self.operator,
                                 self, score=2)

    def __iter__(self):
        while True:
            yield self.gen_question()


class VerbTenseComboGenerator(ItemGenerator):
    def __init__(self, register_cleanup_handler,
                 instruction_type=None,
                 verbs_key="Conjugation/Verbs",
                 tenses_key="Conjugation/Tenses",
                 items_key="Conjugation/Items",
                 cursor_key="Conjugation/Cursor",
                 needswork_key="Conjugation/NeedsWork", *,
                 disable_needswork=False, seen=None, qsettings=None):
        # Needed for init_master_vars(), called by the parent constructor
        self.verbs_key = verbs_key
        self.tenses_key = tenses_key

        super().__init__(
            register_cleanup_handler, items_key, cursor_key,
            needswork_key, disable_needswork=disable_needswork, seen=seen,
            qsettings=qsettings)

        self.instruction_type = instruction_type

    def compute_items_list(self):
        l = [ (v, t) for v in self.verbs for t in self.tenses ]

        return l

    def init_master_vars(self):
        # Get/initialize the list of verbs to work on (make sure it is set in
        # the config file)
        if self.loadOrInitIntSetting("Conjugation/UseAllDefinedVerbs", 1):
            # Use all verbs defined in conj, regardless of the value assigned
            # to verbs_key in the config file managed by QSettings.
            self.verbs = list(conj.keys())
        else:
            self.verbs = self.loadOrInitSetting(self.verbs_key,
                                                list(conj.keys()))

        # Get/initialize the list of tenses to work on (make sure it is set in
        # the config file)
        if self.loadOrInitIntSetting("Conjugation/UseAllTenses", 0):
            # Use all tenses defined in conj, regardless of the value assigned
            # to tenses_key in the config file managed by QSettings.
            self.tenses = used_tenses
        else:
            self.tenses = self.loadOrInitSetting(
                self.tenses_key, list(used_tenses))

    def gen_item(self):
        while True:
            verb, tense = super().gen_item()

            try:
                t = conj[verb]
                try:
                    c = t[tense]
                    break
                except KeyError:
                    logger.warning("conj table in conjugations module has no "
                                   "entry for verb '%s' in tense '%s'",
                                   verb, tense)
            except KeyError:
                logger.warning("conj table in conjugations module has no entry "
                               "for verb '%s'", verb)

        if self.instruction_type is not None:
            instruction = conj_instr(self.instruction_type, verb, tense)
        else:
            instruction = None

        return (verb, tense, instruction)


class ConjugationsGenerator(object):
    """Question generator for conjugations.

    Every instance is bound to a given verb and tense.
    Generate a Question for every person for this verb in this tense."""
    def __init__(self, verb_tense_generator, verb, tense):
        self.qDesc = "conjugation"
        self.verb = verb
        self.tense = tense
        self.verb_tense_generator = verb_tense_generator

    def gen_question(self, person):
        return Conjugation(self.qDesc, self.verb, self.tense, person,
                           generator=self.verb_tense_generator)

    def __iter__(self):
        for i in range(len(conj_subjects)):
            # The existence of conj[self.verb][self.tense] is ensured by the
            # implementation of gen_item in VerbTenseComboGenerator.
            if conj[self.verb][self.tense][i] is None:
                continue

            yield self.gen_question(i)


# ****************************************************************************
# *                      Question class and subclasses                       *
# ****************************************************************************

class Question(object):
    """Class containing everything needed to display a question, check and
    correct the answer. Must be derived and completed by subclasses.

    """
    def __init__(self, desc):
        # Non-translatable string identifying the kind of work that the
        # Question is about (e.g., "addition"); this is used for autogenerated
        # help.
        self.desc = desc
        self.result_as_strings = ()

    def is_correct_result(self, ans, field=None):
        # Generic method that does a string comparison of every field after
        # stripping whitespace in ans[field]. If, for instance, "005" is as
        # good an answer as "5", this method should be overridden.
        if field is None:
            assert len(ans) == len(self.result_as_strings), \
                (ans, self.result_as_strings)
        elif not isinstance(field, int):
                raise TypeError("invalid type for argument 'field': %s"
                                % repr(field))

        for o in (ans if field is None else (ans,)):
            if not isinstance(o, str):
                raise TypeError("not a string: %s" % repr(o))

        # Strip whitespace in every component of ans before comparing to the
        # corresponding component of self.result_as_strings.
        check_field = lambda x, y: str(x).strip() == y
        if field is None:
            return all(map(check_field, ans, self.result_as_strings))
        else:
            return check_field(ans, self.result_as_strings[field])

    def check(self, ans):
        """Check an answer and remember the associated item if the answer is incorrect.

        This method needs only to differ from is_correct_result() for
        subclasses that remember incorrect answers.

        """
        return self.is_correct_result(ans)

    def format(self):
        raise NotImplementedError()

    def format_question(self):
        raise NotImplementedError()

    def addAutoGeneratedHelp(self, formatInfo):
        langCode = locale.getlocale(locale.LC_MESSAGES)[0]

        if langCode in opHelpFunc:
            formatInfo["help"] = opHelpFunc[langCode](langCode, self.desc)


class QuestionWithNeedsWorkFeedback(Question):
    """Class containing everything needed to display a question, check and
    correct the answer, and report to the appropriate generator in case the
    answer is wrong. Must be derived and completed by subclasses.

    """
    def __init__(self, desc, item, generator=None):
        super().__init__(desc)
        # self.item is what is going to be added to needswork if an answer is
        # incorrect.
        self.item = item
        self.generator = generator

    def check(self, ans):
        if self.is_correct_result(ans):
            return True
        else:
            if self.generator is not None \
                    and not self.generator.disable_needswork:
                self.generator.add_to_needswork(self.item)
                logger.debug("Adding %s to needswork -> %s"
                             % (self.item, list(self.generator.needswork)))
            return False


class Conjugation(QuestionWithNeedsWorkFeedback):
    def __init__(self, desc, verb, tense, person, generator=None, score=1):
        # Only the (verb, tense) couple is remembered in case of an incorrect
        # answer.
        super().__init__(desc, (verb, tense), generator)

        self.verb = verb
        self.tense = tense

        self.person = person

        self.score = score
        self.result = self.result_as_strings = \
            ( str(conj[self.verb][self.tense][self.person]), )

        assert self.result[0].strip() == self.result[0], \
            "%s has leading or trailing whitespace" % repr(self.result[0])

        assert conj[self.verb][self.tense][self.person] is not None, \
            (self.verb, self.tense, self.person)

    def format(self):
        return conj_subjects[self.person]

    def format_question(self, addAutoGenHelp=True):
        # Prompt for a conjugation; {0} will be something like
        # "1st pers. sing.". As the whole instruction text is in French, the
        # string uses French typography and is not marked as translatable.
        formatInfo = { "text": "{0} : ".format(self.format()) }
        if addAutoGenHelp:
            self.addAutoGeneratedHelp(formatInfo)

        return (formatInfo, None)


class ArithmeticCalculus(QuestionWithNeedsWorkFeedback):
    def __init__(self, desc, operands, operator, operator_for_print,
                 generator=None, score=1):
        """Class representing a calculus with integers.

        It is suitable for:
          - associative binary operators
            e.g., the operation 5 + 12 + 8 can be represented with
            self.operands = (5, 12, 8)
          - non-associative operators when only two operands are used
            e.g., the operation 12 - 5 can be represented with
            self.operands = (12, 5).

        This is because the calculus from self.operands is done with
        functools.reduce().

        """
        super().__init__(desc, operands, generator)

        self.operands = operands
        self.operator = operator
        self.operator_for_print = operator_for_print

        self.score = score
        self.result = ( functools.reduce(self.operator, self.operands) ,)
        self.result_as_strings = ( str(self.result[0]) ,)

    def is_correct_result(self, ans, field=None):
        if field is None:
            assert len(ans) == len(self.result) == 1, (ans, self.result)
            an = ans[0]
        elif field == 0:
            an = ans
        else:
            raise ValueError("invalid value for argument 'field': %s"
                             % repr(field))

        if isinstance(an, str):
            try:
                ansi = int(an)
            except ValueError:
                return False
        else:
            raise TypeError("not a string: %s" % repr(an))

        return self.result[0] == ansi

    def format(self):
        return self.operator_for_print.join(map(str, self.operands))

    def format_question(self, addAutoGenHelp=True):
        #: Prompt for a calculus
        formatInfo = { "text": translate("app", "{0} = ").format(
                self.format()) }
        if addAutoGenHelp:
            self.addAutoGeneratedHelp(formatInfo)

        return (formatInfo, None)


class EuclidianDivision(QuestionWithNeedsWorkFeedback):
    def __init__(self, desc, operands, operator, generator=None, score=1):
        """Class representing an euclidian division."""
        # Only the divisor is remembered in case of an incorrect answer.
        super().__init__(desc, operands[1], generator)

        self.operands = operands
        self.operator = operator

        self.score = score
        self.result = self.operator(*operands)
        self.result_as_strings = tuple(map(str, self.result))

    def fieldAsIntOrNone(self, s):
        if isinstance(s, str):
            try:
                res = int(s)
            except ValueError:
                res = None
        else:
            raise TypeError("not a string: %s" % repr(s))

        return res

    def is_correct_result(self, ans, field=None):
        if field is None:
            assert len(ans) == len(self.result) == 2, (ans, self.result)
            ansi = map(self.fieldAsIntOrNone, ans)
            return all(map(operator.eq, ansi, self.result))
        elif field in (0, 1):
            ansi = self.fieldAsIntOrNone(ans)
            return ansi == self.result[field]
        else:
            raise ValueError("invalid value for argument 'field': %s"
                             % repr(field))

    def format(self):
        #: E.D. = Euclidian Division
        return translate("app", "E.D. of {0} by {1}").format(self.operands[0],
                                                             self.operands[1])

    def format_question(self, addAutoGenHelp=True):
        #: {0} will be something like "E.D. of 3263 by 7"
        formatInfo0 = { "text": translate("app", "{0}: quotient = ").format(
                self.format()) }
        if addAutoGenHelp:
            self.addAutoGeneratedHelp(formatInfo0)

        return (formatInfo0, { "text": translate("app",
                                                 "; remainder = ") }, None)


# ****************************************************************************
# *             Adornments, A.K.A automatically generated "help"             *
# ****************************************************************************

fr_FR_genreCode = { "m": 0, "f": 1 }

fr_FR_operations = {
    "addition": ("addition", "f"),
    "substraction": ("soustraction", "f"),
    "multiplication": ("multiplication", "f"),
    "euclidian division": ("division euclidienne", "f"),
    "conjugation": ("conjugaison", "f") }

fr_FR_qualifiersPre1 = ( \
    ("adorable",),
    ("chouette",),
    ("sympatique",),
    ("attendrissant", "attendrissante"),
    ("joli", "jolie"),
    ("gentil", "gentille"),
    ("mignon", "mignonne"),
    ("délicieux", "délicieuse"),
    ("inoffensif", "inoffensive") )

fr_FR_qualifiersPre2 = ( \
    ("petit", "petite"),)

fr_FR_qualifiersPost1 = ( \
    ("sympatique",),
    ("romantique",),
    ("qui vous veut du bien",),
    ("de derrière les fagots",),
    ("simple et authentique",),
    ("qui ne veut de mal à personne",),
    ("plein de tendresse", "pleine de tendresse"),
    ("bien intentionné", "bien intentionnée"),
    ("coquin", "coquine"),
    ("affectueux", "affectueuse"),
    ("mignon à croquer", "mignonne à croquer"),)

def accord(genreCode, t):
    return t[genreCode] if len(t) >= 2 else t[0]

def fr_FR_genOpHelp(langCode, operation):
    gc = fr_FR_genreCode[fr_FR_operations[operation][1]]
    opName = fr_FR_operations[operation][0]
    l = []
    usePost = random.choice((True, False))

    if not usePost:
        l.append(accord(gc, random.choice(fr_FR_qualifiersPre1)))

    if random.choice((True, False)):
        l.append(accord(gc, random.choice(fr_FR_qualifiersPre2)))

    l.append(opName)

    if usePost:
        l.append(accord(gc, random.choice(fr_FR_qualifiersPost1)))

    return ' '.join(map(str, l))

opHelpFunc = { "fr_FR": fr_FR_genOpHelp,
               "fr":    fr_FR_genOpHelp }


def _test():
    logger.setLevel(logging.DEBUG)

    r = iter(RandomAdditionGenerator(10, 14))
    for i in range(30):
        print(next(r).format())

    sys.exit(0)

if __name__ == "__main__": _test()
