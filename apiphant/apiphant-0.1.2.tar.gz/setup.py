# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='apiphant',
    version='0.1.2',
    description='Simple Python Web API framework, based on Gevent, JSON, CRUD.',
    long_description='''
Features:

* Based on `gevent.wsgi <http://www.gevent.org/servers.html>`_, optimized for tens of thousands of concurrent users.

* Simple! Try it::

    mkdir -p myproduct/api/v0
    touch {myproduct,myproduct/api,myproduct/api/v0}/__init__.py

    cat <<END >myproduct/api/v0/echo.py
    # from myproduct.api import anything
    def read(request):
        response = request.copy()
        response.ok = True
        return response
    END

    sudo apt-get install --yes gcc libevent-dev python-dev
    sudo pip install apiphant
    apiphant myproduct 127.0.0.1:8001

    # POST http://{host}:{port}/api/{version}/{t/a/r/g/e/t}/{action}
    curl --data-binary '{"hello": "world"}' --request POST http://127.0.0.1:8001/api/v0/echo/read
    {"hello": "world", "ok": true}

* Automated functional tests in Python::

    apiphant myproduct 127.0.0.1:8888

    cat <<END >test.py
    from apiphant.test import test
    test('echo', 'read', {"hello": "world"}, 200, {"hello": "world", "ok": True})
    END

    python test.py
    POST http://127.0.0.1:8888/api/v0/echo/read {"hello": "world"} --> 200 {'ok': True, 'hello': 'world'}

* Please see how this shell script
  `test.sh <https://github.com/denis-ryzhkov/apiphant/blob/master/tests/myproduct/api/test.sh>`_
  can help to run Python tests in
  `test.py <https://github.com/denis-ryzhkov/apiphant/blob/master/tests/myproduct/api/test.py>`_.

* Optional full-stack deploy! Supervisor, Nginx, Logrotate, Apt, Pip, etc.

    * Copy `myproduct template <https://github.com/denis-ryzhkov/apiphant/blob/master/tests>`_.
    * Replace ``myproduct`` with your product name in all configs and scripts.
    * Run root ``deploy.sh`` and enjoy the show.
    * This deploy framework is going:
        * To get Virtualenv bootstraper.
        * To be extracted to a separate opensource repo.

* Validate request fields and raise errors::

    from apiphant.validation import ApiError, field, Invalid

    def read(request):
        id = field(request, 'id', is_required=True, valid_type=int)
        # More options: default_value, valid_value, valid_length, max_length.

        item = get_item(id)
        if not item:
            raise Invalid('id')
            # that is a shortcut for:
            raise ApiError(400, 'id is Invalid')

* ``version`` value ``v0`` used in the example
  `means <http://semver.org/>`_ API is not public yet, and maybe never will,
  so is expected to be changed without notification.

* ``action`` is one of `CRUD <http://en.wikipedia.org/wiki/Create,_read,_update_and_delete>`_:
  ``create``, ``read``, ``update``, ``delete``.

* Reasons why `CRUD <http://en.wikipedia.org/wiki/Create,_read,_update_and_delete>`_
  is implemented without use of HTTP methods
  that are recommended by `REST <http://en.wikipedia.org/wiki/Representational_state_transfer>`_:

    * Best match for generally partial «Update» action is `PATCH <http://tools.ietf.org/html/rfc5789>`_ method,
      but it is not supported by our `gevent.wsgi <http://www.gevent.org/servers.html>`_ webserver and several clients.
    * Much more standard ``PUT`` method means «Replace»,
      that is not how «Update» should work in general case.
      Imagine SQL ``UPDATE`` working as «Replace».
    * Some cases allow only ``GET`` and ``POST``,
      e.g. cross-origin requests in some browsers,
      while at least ``DELETE`` method is required for full set of actions.
    * So ``POST`` is selected as «a uniform method», suitable for all actions:
      «The actual function performed by the POST method
      is determined by the server» - `HTTP/1.1 <http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html>`_.

* `{"json": "object"} <http://json.org/>`_ is used for both request and response,
  to speak one language easily with any client.

    * No `X-Custom-HTTP: Headers <http://www.google.com/search?q=custom+http+headers>`_.
    * No `?url=encoded%20query%20string <http://en.wikipedia.org/wiki/Query_string#URL_encoding>`_.
    * No need to check the type of root JSON value,
      it is always ``object`` with self-describing names inside,
      not just bare value like ``42``.

* However, URL still contains several request parameters, because:

    * Different targets may be routed by load balancers
      to different backend servers using simple URL location routing.
    * ``version``, ``target`` and ``action`` are always required,
      so may be positional parameters,
      improving readability and saving resources in a natural way.

''',
    url='https://github.com/denis-ryzhkov/apiphant',
    author='Denis Ryzhkov',
    author_email='denisr@denisr.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=['apiphant'],
    scripts=['scripts/apiphant'],
    install_requires=[
        'adict',
        'gevent',
        'requests>=1.1.0', # Because response.json we use became backward-incompatible in response>=1.*: changed from a property to a method.
    ],
)
