from testsuite.prettyprint.outcomes.reporter import PrettyOutcomesReporter

try:
    import colorama
    colorama.init()
except ImportError:
    pass

__all__ = ['PrettyOutcomesReporter']
