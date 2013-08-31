import contextlib
import os

@contextlib.contextmanager
def ignored(*e):
	try:
		yield
	except e:
		pass

dataDir = os.path.join(os.path.dirname(__file__), "data")
