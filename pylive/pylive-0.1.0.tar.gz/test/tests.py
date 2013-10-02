""" Unit tests for PyLive """

import unittest
import random
import live
import math
import time

class Tests(unittest.TestCase):
	def testSetTempo(self):
		""" set and query tempo """
		set = live.Set()
		tempo = random.randint(50, 150)
		set.tempo = tempo
		self.assertEqual(tempo, set.tempo)

	def testSetTime(self):
		""" set and query arrangement time """
		set = live.Set()
		t = random.randint(0, 16)
		set.set_time(t)
		time.sleep(0.2)
		t_new = set.get_time()
		self.assertEqual(t, t_new)


if __name__ == "__main__":
	unittest.main()
