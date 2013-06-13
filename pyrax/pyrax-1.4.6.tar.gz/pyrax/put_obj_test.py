#!/usr/bin/env python
"""Provoke store_object to fail."""
from contextlib import closing
from datetime import datetime
from functools import wraps
from StringIO import StringIO
from tempfile import NamedTemporaryFile
import pyrax
##pyrax.set_setting("identity_type", "rackspace")      # Comment this out when running on 1.3.9.

# Print a breadcrumb every this many calls to store_object.
BREADCRUMB = 60 * 5

# The container and object to which we store, and the source string.
CONTAINER = "jdr_pyrax_test"
OBJECT = "foobar_%d"
SOURCE = "XXX " * 500

# CloudFiles errors that are retryable.
RETRYABLE_CLOUD_ERRORS = (pyrax.exceptions.DNSCallTimedOut,
                          pyrax.exceptions.NetworkCountExceeded,
                          pyrax.exceptions.NetworkInUse,
                          pyrax.exceptions.ClientException)

# Our Rackspace API credentials
CF_DS_ACCT = "INSERT NAME HERE"
CF_DS_API = "INSERT API KEY HERE"
CF_DS_SERVICENET = True                            # Set to True when running on celery node.

# Our cloud object
conn = None

class Retry(object):
    """A simple retry class / decorator."""

    BACKOFF_EXPONENTIAL = staticmethod(lambda delay, count: delay + count ** 2)
    NO_SWALLOW = staticmethod(lambda exc: False)
    EMPTY_HANDLER = staticmethod(lambda exc: None)

    def __init__(self, tries=4, delay=1, **kwargs):
        """Initializer.

        :keyword tries: Number of tries
        :type tries: int
        :keyword delay: Initial delay between retries, in seconds
        :type delay: int
        :keyword backoff_fn: A function to calculate the time to backoff upon an exception. This must
                             take two arguments, initial_delay and a 1-based iteration_number, and
                             return the number of seconds to backoff as an int or float. Defaults to
                             an exponential backoff
        :type  backoff_fn: callable
        :keyword exceptions: The exceptions that are retryable.
        :type  exceptions: tuple of Exception, or Exception
        :keyword exception_handler: Extra handling code.
        :type exception_handler: A callable
        :keyword swallow_fn: Should unhandled exception be swallowed?
        :type  swallow_fn: A callable that returns a bool
        :keyword default_ret: Return value if there is a swallowed exception

        """

        self.tries = tries
        self.initial_delay = delay

        self.backoff_fn = kwargs.get('backoff_fn', self.BACKOFF_EXPONENTIAL)

        self.exceptions = kwargs.get('exceptions', tuple())
        self.exception_handler = kwargs.get('exception_handler', self.EMPTY_HANDLER)

        self.swallow_fn = kwargs.get('swallow_fn', self.NO_SWALLOW)
        self.default_ret = kwargs.get('default_ret', None)

    def __call__(self, operation):
        """Call with retries."""

        @wraps(operation)
        def op_with_retries(*args, **kwargs):
            """Wrapped function."""
            from time import sleep

            for iteration in range(self.tries):
                try:
                    # Execute the desired operation
                    return operation(*args, **kwargs)
                except self.exceptions as exc:
                    # Process the caller's specified exceptions. If we are out of retries, pass the
                    # exception up the call stack. Otherwise, call the exception handler and
                    # iterate.
                    if iteration + 1 >= self.tries:
                        raise
                    self.exception_handler(exc)
                except Exception as exc:
                    # A non-retryable exception. Return the default return value if we're supposed
                    # to swallow it, otherwise pass the exception up the call stack.
                    if self.swallow_fn(exc):
                        return self.default_ret
                    else:
                        raise

                # The operation had a retryable exception. Sleep and then try again.
                sleep(float(self.backoff_fn(self.initial_delay, iteration + 1)))

        return op_with_retries



@Retry(exceptions=RETRYABLE_CLOUD_ERRORS)
def put_object_string(container_name, object_name, value, content_type="application/octet-stream"):

    # Ensure the container exists
    conn.create_container(container_name)

    # Make the checksum.
    with closing(StringIO()) as value_object:
        value_object.write(value)
        value_object.seek(0)
        checksum = pyrax.utils.get_checksum(value_object)

    # Store the object.
    conn.store_object(container_name,
                      object_name,
                      value,
                      content_type=content_type,
                      etag=checksum)

counter = 0

while True:
    # Load a cloud object, if we don't already have one.
    if not pyrax.identity or not pyrax.identity.authenticated or \
            pyrax.identity.expires <= datetime.now() or not conn:
#         pyrax.set_credentials(CF_DS_ACCT, CF_DS_API)
        pyrax.keyring_auth()
        conn = pyrax.connect_to_cloudfiles(region="ORD", public=True)   #not CF_DS_SERVICENET)

    # Print a breadcrumb
    if counter % BREADCRUMB == 0:
        print "[%s] %d" % (datetime.now(), counter)
    counter += 1

    # Store one object.
    object_name = OBJECT % counter

    localcopy = NamedTemporaryFile()
    localcopy.write(SOURCE)
    localcopy.seek(0)

    put_object_string(CONTAINER, object_name, localcopy.read())

    localcopy.close()
