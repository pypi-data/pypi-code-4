import unittest
from stub import stub

# class to add call expecting functions
class CallExpecterMixin:
	def clear_call_expecters(self):
		for call_expecter in getattr(self, 'call_expecters', []):
			call_expecter.remove()
		self.call_expecters = []

	def expect_call(self, _callable, calls_expected=1, exact_calls=False):
		"""Decorates a callable so that the current
		test case can verify that the callable was called. The callable
		is replaced in-place and is called by the decorator so that
		the return value should be the same as the un-decorated
		callable.

		Use self.assertExpectedCallsOccurred() to check that all
		calls occurred as expected.

		By default this decorator expects callables to be called once,
		use the `calls_expected` parameter to change this.

		By default, if the callable is called more than the expected number
		of times, the expectation is considered met; otherwise, set the
		`exact_calls` parameter to `True` to cause the expectation to fail
		if the number of calls does not match exactly.
		"""
		if not hasattr(self, 'call_expecters'):
			self.call_expecters = []
		self.call_expecters.append(CallExpecter(_callable, calls_expected, exact_calls))

	def assertExpectedCallsOccurred(self):
		self.assertCalls()

	def assertCalls(self):
		for e in getattr(self, 'call_expecters', []):
			e.__check__()
		self.clear_call_expecters()


class CallExpecter:
	def __init__(self, _callable, calls_expected=1, exact_calls=False):
		self._callable = _callable
		self.calls = 0
		self.calls_expected = calls_expected
		self.exact_calls = exact_calls

		def call_counter(*args, **kwargs):
			self.calls += 1

			return self._callable.unstubbed(*args, **kwargs)

		self._callable = stub(_callable, call_counter)

	def remove(self):
		self._callable.unstub()

	def __call__(self, *args, **kwargs):
		return self._callable(*args, **kwargs)

	def __check__(self):
		name = self._callable.__name__
		source = self._callable.im_self if hasattr(self._callable, 'im_self') else self._callable.__module__

		err_msg = '%s.%s called %s times, expected %s ' % (source, name, self.calls, self.calls_expected)

		if self.exact_calls:
			assert self.calls_expected == self.calls, err_msg
		else:
			assert self.calls_expected <= self.calls, err_msg
