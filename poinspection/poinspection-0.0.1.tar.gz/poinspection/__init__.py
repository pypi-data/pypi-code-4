# Fail gracefully if IPython not installed or if old version.
try: from poinspection import load_ipython_extension, unload_ipython_extension
except (ImportError, SyntaxError): pass
