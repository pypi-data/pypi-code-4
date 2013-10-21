"""ARS is a physically-accurate open-source simulation suite for research and
development of mobile manipulators and, in general, any multi-body system.

"""
# based on: ``django.__init__`` @ commit 5b644a5
# see its license in docs/Django BSD-LICENSE.txt

# for a "real" release, replace 'alpha' with 'final'
VERSION = (0, 5, 0, 'alpha', 2)  # i.e. 0.5a2


def get_version(*args, **kwargs):
	# Only import if it's actually called.
	from .utils.version import get_version
	return get_version(*args, **kwargs)
