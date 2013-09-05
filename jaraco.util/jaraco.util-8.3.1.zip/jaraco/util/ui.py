from __future__ import (print_function, absolute_import, unicode_literals,
	division)

import time
import sys
import itertools
import abc

import six

class Menu(object):
	"""
	A simple command-line based menu
	"""
	def __init__(self, choices=None, formatter=str):
		self.choices = choices or list()
		self.formatter = formatter

	def get_choice(self, prompt="> "):
		n = len(self.choices)
		number_width = len(str(n)) + 1
		menu_fmt = '{number:{number_width}}) {choice}'
		formatted_choices = map(self.formatter, self.choices)
		for number, choice in zip(itertools.count(1), formatted_choices):
			print(menu_fmt.format(**vars()))
		print()
		try:
			answer = int(six.moves.input(prompt))
			result = self.choices[answer - 1]
		except ValueError:
			print('invalid selection')
			result = None
		except IndexError:
			print('invalid selection')
			result = None
		except KeyboardInterrupt:
			result = None
		return result


six.add_metaclass(abc.ABCMeta)
class AbstractProgressBar(object):
	def __init__(self, unit='', size=70):
		"""
		Size is the nominal size in characters
		"""
		self.unit = unit
		self.size = size

	def report(self, amt):
		sys.stdout.write('\r%s' % self.get_bar(amt))
		sys.stdout.flush()

	@abc.abstractmethod
	def get_bar(self, amt):
		"Return the string to be printed. Should be size >= self.size"

	def summary(self, str):
		return ' (' + self.unit_str(str) + ')'

	def unit_str(self, str):
		if self.unit:
			str += ' ' + self.unit
		return str

	def finish(self):
		print()

	def __enter__(self):
		self.report(0)
		return self

	def __exit__(self, exc, exc_val, tb):
		if exc is None:
			self.finish()
		else:
			print()


class SimpleProgressBar(AbstractProgressBar):

	_PROG_DISPGLYPH = itertools.cycle(['|', '/', '-', '\\'])

	def get_bar(self, amt):
		bar = next(self._PROG_DISPGLYPH)
		template = ' [{bar:^{bar_len}}]'
		summary = self.summary('{amt}')
		template += summary
		empty = template.format(
			bar='',
			bar_len=0,
			amt=amt,
		)
		bar_len = self.size - len(empty)
		return template.format(**vars())

	@classmethod
	def demo(cls):
		bar3 = cls(unit='cubes', size=30)
		with bar3:
			for x in six.moves.range(1, 759):
				bar3.report(x)
				time.sleep(0.01)

class TargetProgressBar(AbstractProgressBar):
	def __init__(self, total=None, unit='', size=70):
		"""
		Size is the nominal size in characters
		"""
		self.total = total
		super(TargetProgressBar, self).__init__(unit, size)

	def get_bar(self, amt):
		template = ' [{bar:<{bar_len}}]'
		completed = amt / self.total
		percent = int(completed * 100)
		percent_str = ' {percent:3}%'
		template += percent_str
		summary = self.summary('{amt}/{total}')
		template += summary
		empty = template.format(
			total=self.total,
			bar='',
			bar_len=0,
			**vars()
		)
		bar_len = self.size - len(empty)
		bar = '=' * int(completed * bar_len)
		return template.format(total=self.total, **vars())

	@classmethod
	def demo(cls):
		bar1 = cls(100, 'blocks')
		with bar1:
			for x in six.moves.range(1, 101):
				bar1.report(x)
				time.sleep(0.05)

		bar2 = cls(758, size=50)
		with bar2:
			for x in six.moves.range(1, 759):
				bar2.report(x)
				time.sleep(0.01)

	def finish(self):
		self.report(self.total)
		super(TargetProgressBar, self).finish()
