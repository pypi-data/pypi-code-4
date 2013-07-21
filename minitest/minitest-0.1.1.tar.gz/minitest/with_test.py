import sys
import traceback
from datetime import datetime
import pprint

import inject_methods
from variables import *

__all__ = ['test', 'test_case', 'get_test_self']

class TestSelf(object):
    pass

def get_test_self():
    return TestSelf()

class TestFailure(object):
    def __init__(self, actual, expected, file_info):
        self.actual = actual
        self.expected = expected
        self.file_info = file_info

class TestCase(object):
    def __init__(self, msg=None):
        self.msg = msg
        self.test_methods = []
        self.assertion_count = 0
        self.failures = []

    def __enter__(self):
        self.start_time = datetime.now()
        print "Running tests:\n"
        set_current_test_case(self)
        return self

    def __exit__(self, e_type, value, tb):
        self.end_time = datetime.now()
        if e_type != None:
            # print e_type
            # print value
            # print tb
            print traceback.format_exc()
        set_current_test_case(None)
        self.print_report()
        return self

    def add_test_method(self, test_method):
        self.test_methods.append(test_method)
        return self

    def add_assertion(self):
        self.assertion_count += 1

    def add_failure(self, actual=None, expected=None, file_info=None):
        self.failures.append(TestFailure(actual, expected, file_info))

    def print_report(self):
        pass_seconds = (self.end_time - self.start_time).total_seconds()
        print "\n"
        print "Finished tests in %fs.\n" % pass_seconds
        [self.print_failure(index, failure) for index, failure in enumerate(self.failures)]
        # map(self.print_failure, enumerate(self.failures))
        print "%d tests, %d assertions, %d failures, %d errors." %\
          (len(self.test_methods), self.assertion_count, len(self.failures), 0)
        return True
        
    def print_failure(self, index, failure):
        print "%d) Failure:" % (index+1)
        print "The line No is [%s]:" % failure.file_info
        print "--- expected"
        print "+++ actual"
        print "-[%s]" % pprint.pformat(failure.expected)
        print "#[%s]" % pprint.pformat(failure.actual)
        print
        return True


# Run options: --seed 38103

# # Running tests:

# F.

# Finished tests in 0.044339s, 45.1070 tests/s, 45.1070 assertions/s.

#   1) Failure:
# test_0001_can work!(OrderDecisionTableBuilder) [/Users/Colin/work/ruby/dsl/advanced_decision_table/order_decision_table_builder.rb:79]:
# --- expected
# +++ actual
# @@ -1 +1 @@
# -[#<struct Consequence description="Fee">, #<struct Consequence description="Alert Re p">]
# +[#<struct Consequence description="Fee">, #<struct Consequence description="Alert Rep">]

# 2 tests, 2 assertions, 1 failures, 0 errors, 0 skips
# [Finished in 0.3s with exit code 1]

# # Running tests:

# ..

# Finished tests in 0.002570s, 778.2101 tests/s, 3501.9455 assertions/s.

# 2 tests, 9 assertions, 0 failures, 0 errors, 0 skips
# [Finished in 0.3s]


class TestMethod(object):
    def __init__(self, msg=None):
        self.msg = msg
        self.failed_flag = False

    def __enter__(self):
        # print "test enter"
        set_current_test_method(self)
        get_current_test_case().add_test_method(self)
        return self

    def __exit__(self, e_type, value, tb):
        if e_type != None:
            # print e_type
            # print value
            # print tb
            print traceback.format_exc()
        # print "method exit"
        if self.failed_flag:
            sys.stdout.write('F')
        else:
            sys.stdout.write('.')
        sys.stdout.flush()
        set_current_test_method(None)
        return self

    def set_failed(self):
        self.failed_flag = True
        return self.failed_flag

def test_case(msg):
    return TestCase(msg)

def test(msg):
    return TestMethod(msg)



if __name__ == '__main__':
    import operator
    with test_case("new test case"):


        with test("test must_equal"):
            'jc'.must_equal('jc')

        with test("test must_true"):
            True.must_true()
            False.must_true()


        with test("test must_equal_with_func"):
            (1).must_equal_with_func(1, operator.eq)
            (1).must_equal_with_func(2, operator.eq)

        def div_zero():
            1/0
            
        with test("test must_raise"):
            (lambda : div_zero()).must_raise(ZeroDivisionError)



