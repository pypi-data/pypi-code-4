__unittest = True


class Expectation(object):
    def __init__(self, actual):
        self.actual = actual

    @classmethod
    def extend(cls, *extensions):
        return type('', tuple(reversed(extensions)) + (cls,), {})

    @staticmethod
    def fail(message='', *args, **kwargs):
        raise AssertionError(message.format(*args, **kwargs))

    def equal(self, expected):
        if self.actual == expected:
            return
        self.fail_binary_op('==', expected)

    def not_equal(self, expected):
        if self.actual != expected:
            return
        self.fail_binary_op('!=', expected)

    def is_(self, expected):
        if self.actual is expected:
            return
        self.fail_binary_op('is', expected)

    def is_not(self, expected):
        if self.actual is not expected:
            return
        self.fail_binary_op('is not', expected)

    def true(self):
        if bool(self.actual):
            return
        self.fail('Expected {} to be true', repr(self.actual))

    def false(self):
        if not self.actual:
            return
        self.fail('Expected {} to be false', repr(self.actual))

    def in_(self, expected):
        if self.actual in expected:
            return
        self.fail_binary_op('in', expected)

    def not_in(self, expected):
        if self.actual not in expected:
            return
        self.fail_binary_op('not in', expected)

    def less(self, expected):
        if self.actual < expected:
            return
        self.fail_binary_op('<', expected)

    def less_equal(self, expected):
        if self.actual <= expected:
            return
        self.fail_binary_op('<=', expected)

    def greater(self, expected):
        if self.actual > expected:
            return
        self.fail_binary_op('>', expected)

    def greater_equal(self, expected):
        if self.actual >= expected:
            return
        self.fail_binary_op('>=', expected)

    def almost_equal(self, expected):
        if round(self.actual - expected, 7) == 0:
            return
        self.fail(
            'Expected {} almost equal to {} (7)',
            repr(self.actual), repr(expected))

    def not_almost_equal(self, expected):
        if round(self.actual - expected, 7) != 0:
            return
        self.fail(
            'Expected {} not almost equal to {} (7)',
            repr(self.actual), repr(expected))

    @classmethod
    def raises(cls, expected):
        class ContextManager(object):
            def __enter__(self):
                pass

            def __exit__(self, exc_type, exc_value, traceback):
                if exc_value is None:
                    cls.fail('Expected code to raise {}', repr(expected))

                if isinstance(exc_value, expected):
                    return True
        return ContextManager()

    def fail_binary_op(self, op, expected):
        self.fail('Expected {} {} {}', repr(self.actual), op, repr(expected))

expect = Expectation
