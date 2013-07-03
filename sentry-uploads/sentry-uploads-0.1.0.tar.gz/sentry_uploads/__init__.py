try:
    VERSION = __import__('pkg_resources').get_distribution('sentry_uploads').version
except Exception as e:
    VERSION = 'unknown'
