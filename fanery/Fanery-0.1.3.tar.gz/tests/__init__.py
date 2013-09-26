"""
Fanery is a Python framework that offers:

    - minimalist pythonic design.
    - strong security.
    - easy of use.
    - scalable fundation.
    - multi-protocol facility.
    - handy profiling support.

Fanery philosofy:

    - Secure by default (yes I love OpenBSD).
    - Free/Open Source Software is the Way.
    - UI should never be created server-side.
    - functional style programming should be
      the preferred way to build applications.

Required dependencies:

    - pycrypto.
    - webob.

Optional dependencies:

    - memory-profiler.
    - line-profiler.
    - profilehooks.
    - pprofiler.
    - linesman.
    - rfoo.
    - lmdb.

Getting started:

    Creating secure services:

        from fanery import service

        @service()
        def safe_call(*args, **argd):
            '''safe_call service.'''
            return dict(args = args, argd = argd)

    Exposed services are pure Python functions,
    don't have to care about client nature:

        - Is it a browser? a raw socket consumer? etc.

    By default call parameters (*args and **argd) are parsed safely
    to python objects by fanery.parse_term(). This behaviour can be
    disabled by setting auto_parse to False:

        @service(auto_parse = False)
        def safe_call(...)

    Exposing hello service through WSGI:

        from fanery import wsgi_server

        # bind by default to localhost:9000
        wsgi_server().start()

Fanery @service decorator explained:

    The @service decorator wraps a function in such
    a way that by default can be consumed only if:

        - The caller own a valid session (is autenticated).
        - The remote call is made through SSL/TLS secured channel.
        - The remote call is encrypted as follow:
            - provide unique session ID and valid HMAC call signature.
            - encrypt the call with OpenSSL compatible AES encryption
              using the server generated cryptographic session token
              which is unique for each single call.

    Such strong security requirements are enforced by the @service
    decorator to avoid and protect applications from attacks like:

        - Cross Site Request Forgery (CSRF).
        - Session Hijacking.
        - Session poisoning.
        - Unwanted redirection.
        - Eyesdrop even in the presence of SSL/TLS weakness.
        - Intercept/resend call stream.


    Aditionally for the sake of remote call safety and application
    scalability fanery:

        - Default login() implementation never send user passwords.
        - Do not rely on session ID secrecy for security, in other
          words, security will not be compromised if session ID is
          disclosed.
        - Bind session to remote call execution stack; session data
          does not rely on thread local facility but fanery.get_state()
          behave like it was.

    When services are exposed via WSGI fanery also take care of
    enforcing safety by:

        - Never use cookies or browser local storage.
        - Never rely on ugly/obfuscated url.

Fanery @service decorator by example:

    from fanery import service, is_number

    @service('sum'):
    def sum_values(*num):
        '''
        sum_values function is exposed as "sum".

        Clients can call it in many ways:

            - with any defined output format:

                sum.json    (default)
                sum.txt     (use %s)
                sum.raw     (use %r)

            - with any prefix:
                prefix/sum.json
                multy/path/prefix/sum.txt

            - with arguments in urlpath:

                sum/n1/n2/n3.raw

            - with GET/POST request arguments:

                GET sum.json?num=1&num=2&num=-4

                POST prefix/sum.txt
                num=1&num=2&num=-4
        '''
        return sum(n for n in num if is_number(n))
"""
