from fanery.filelib import splitext, fullpath, joinpath, isdir, isfile
from fanery.terms import (
    hict, parse_term, get_timestamp, is_string,
    to_simple, to_json, to_str, pickle,
)
from fanery.librand import randuuid

from inspect import currentframe
from functools import wraps
import sys, cgitb, logging

class service(object):

    production = True
    profile = False

    class UnknownFormatter(AssertionError):
        pass

    class SslRequired(AssertionError):
        pass

    class UnsafeCall(AssertionError):
        pass

    class NotFound(AssertionError):
        pass

    def __init__(self):
        self.registry = hict()
        self.batch_jobs = dict()

    def __call__(self, path = None, safe = True, ssl = True, cache = False,
                 static = False, force_download = False, auto_parse = True,
                 log_exc = False, one_time_pad = True, check_outfmt = False,
                 **out):
        '''Register a new service.

        path           - urlpath prefix
        safe           - boolean that enforce service consumption via safe_call
        ssl            - boolean that enforce service consumption over ssl
        cache          - boolean that set/unset response header settings for
                         client side caching. NOTE: no server side caching
        static         - boolean that tell if results are filesystem elements
        force_download - boolean that tell if results are attachments
        auto_parse     - boolean that say if call *args/**kwargs must be parsed
                         terms parsing is performed by fanery.terms.parse_term
        one_time_pad   - boolean that say if crypto token must be unique, which
                         means that a new token is generated on every safe call
        log_exc        - boolean that say if exception must be logged
        check_outfmt   - boolean that say if result formatter must be defined
        **out          - result formatters where key represents mime extension
                         and value is the corresponding callable
                       : default formatters if check_outfmt is not True
                            txt, raw ==> fanery.terms.to_str
                            json     ==> fanery.terms.to_json
                            bin      ==> fanery.terms.pickle

        Example: define a service exposed as /gen_report that accept
                 authenticated safe call over ssl only for users with
                 "board-member" role and return pdf/ods formatted reports.

            from fanery import service, authorize

            def report_pdf(data):
                transform data into pdf file
                return pdf file object or pdf file path

            def report_ods(data):
                transform data into ods file
                return ods file object or ods file path

            @authorize('board-member')
            @service(static = True, ods = report_ods, pdf = report_pdf)
            def gen_report(*args, **argd):
                organize report data based on call parameters
                return data
        '''
        from fanery.profiler import profile

        def decorator(func):

            @wraps(func)
            def wrapper(*args, **argd):
                state = self.state
                if self.production:
                    if ssl is True and state.ssl is not True:
                        raise service.SslRequired(wrapper.service)
                    elif safe is True and state.safe is not True:
                        raise service.UnsafeCall(wrapper.service)

                if auto_parse is True:
                    args = parse_term(args)
                    argd = parse_term(argd)

                try:
                    if self.profile:
                        print '>>> profiling: %s:%s\n' % (func.__module__, func.__name__)
                        return profile(func)(*args, **argd)
                    else:
                        return func(*args, **argd)
                except Exception, e:
                    if log_exc is True or not isinstance(e, AssertionError):
                        logging.error(cgitb.text(sys.exc_info()))
                    raise

            if check_outfmt is not True:
                out.setdefault('json', to_json)
                out.setdefault('raw', to_str)
                out.setdefault('txt', to_str)
                out.setdefault('bin', pickle)

            wrapper.service = hict(
                ssl = ssl,
                safe = safe,
                cache = cache,
                static = static,
                force_download = force_download,
                one_time_pad = one_time_pad,
                log_exc = log_exc,
                auto_parse = auto_parse,
                route = (path or func.__name__).strip('/'),
                output = dict((k, v) for k, v in out.items() if callable(v)),
                check_outfmt = check_outfmt,
            )

            reg = self.registry
            for part in wrapper.service.route.split('/'):
                reg = reg[part]
            else:
                reg[None] = wrapper

            return wrapper

        return decorator

    def lookup(self, urlpath):
        '''Find a registered service by urlpath.'''
        path, ext = splitext(urlpath.strip('/'))
        registry = reg = self.registry

        parts = path.split('/')
        for idx, part in enumerate(parts):
            if part not in reg:
                if reg is registry:
                    continue # skip context prefix
                else:
                    args = parts[idx:]
                    break
            else:
                reg = reg[part]
        else:
            args = parts if reg is registry else list()
            reg = reg.get('', reg)

        func = reg.get(None, None)
        if not callable(func):
            raise self.NotFound()

        service = func.service
        if ext:
            output = service.output.get(ext[1:], None)
            if args and service.static is True:
                args[-1] = args[-1] + ext
        else:
            output = None

        return func, args, ext, output

    def _consume(self, urlpath, *args, **argd):
        '''Consume a registered service by urlpath.'''
        func, urlpath_args, ext, output = self.lookup(urlpath)
        if func.service.check_outfmt is True and not (ext and output):
            raise service.UnknownFormatter(ext)
        ret = func(*(urlpath_args or args), **argd)
        return func.service, ext, output, output(ret) if output else ret

    def consume(self, urlpath, *args, **argd):
        '''Consume a registered service by urlpath.'''
        return self._consume(urlpath, *args, **argd)[-1]

    @property
    def state(self, _key_ = '_fnry_state_'):
        '''Like thread local session, just without thread.'''
        current = currentframe()
        if _key_ in current.f_locals:
            return current.f_locals[_key_]

        frame = caller = current.f_back
        while frame:
            if _key_ in frame.f_locals:
                state = frame.f_locals[_key_]
                break
            frame = frame.f_back
        else:
            state = hict(domain = 'localhost', ssl = False,
                         safe = False, user = None, data = hict())

        return caller.f_locals.setdefault(_key_,
                current.f_locals.setdefault(_key_, state))

    def static(self, path, root, **extra):
        '''Register a new service that allow to retrieve static contents.

        path - urlpath prefix
        root - folder confinement (kind of chroot).

        Example:

            static('/public', '/var/www/public/', safe = False, ssl = False)
                -> no ssl and no authentication required

            static('/reports', '/var/www/reports/', safe = False)
                -> no authentication required but ssl required

            static('/private', '/var/www/private/')
                -> both ssl and authentication required (safe_call over ssl)
        '''
        root = joinpath(fullpath(root), '').rstrip('/')
        assert isdir(root), 'No such directory "%s"' % root

        index = extra.pop('index', 'index.html')
        extra.setdefault('safe', False)
        extra.setdefault('ssl', False)

        @self(path, static = True, auto_parse = False, **extra)
        def static(*args, **argd):
            dompath = fullpath(joinpath(root, self.state.domain, *args))
            if dompath.startswith(root):
                if isdir(dompath):
                    return joinpath(dompath, index)
                elif isfile(dompath):
                    return dompath
            urlpath = fullpath(joinpath(root, *args))
            if urlpath.startswith(root):
                if isdir(urlpath):
                    return joinpath(urlpath, index)
                elif isfile(urlpath):
                    return urlpath
            raise self.NotFound()

    def batch_job(self, job_id):
        job = self.batch_jobs.get(job_id, None)
        if job and not job.process.is_alive():
            del self.batch_jobs[job_id]
        return job

    def _job(self, func, queue, args, argd):
        from fanery import service
        service.state.queue = queue
        return func(*args, **argd)

    def _watcher(self, job, timeout, cleanup):
        try:
            job.start()
            job.join(timeout)
            if job.is_alive():
                job.terminate()
        finally:
            if callable(cleanup):
                cleanup()

    def batch(self, timeout = None, queue = None, cleanup = None):
        '''Make decorated function run as batch process (not thread).

        Running batch process can be queried for working status at any time:

        @service.batch(timeout = 5)
        def batch_job(*args, **argd):
            # this will only perform half of it's work
            from time import sleep
            # queue by default is a synchronized multiprocessing.Manager.list
            queue = service.state.queue
            for i in range(1,11):
                sleep(1)
                queue.append(10.0/i)

        @service()
        def start_batch_job(*args, **argd):
            # remote client call this and get batch job id
            do something
            job = batch_job() # non-blocking
            do something
            return job.id

        @service()
        def job_progress(job_id):
            # later remote client can query batch job progress by id
            job = service.batch_job(job_id)
            assert job, 'not-found'
            return dict(alive = job.process.is_alive(),
                        progress = job.queue[-1] if len(job.queue) else 0)
        '''
        from multiprocessing import Process, Manager
        from threading import Thread

        def decorator(f):

            @wraps(f)
            def wrapper(*args, **argd):
                job_id, q = randuuid(), queue or Manager().list()
                job = self.batch_jobs[job_id] = self.state.jobs[job_id]
                p = Process(target = self._job, args = (f, q, args, argd))
                Thread(target = self._watcher, args = (p, timeout, cleanup)).start()
                return job.update(id = job_id, process = p, queue = q).id

            return wrapper

        return decorator

    def test(self, setUp = None, tearDown = None):
        self.production = False

        def decorator(func):

            @wraps(func)
            def wrapper(*args, **argd):
                state = self.state
                if callable(setUp):
                    setUp()
                if callable(tearDown):
                    try:
                        func(*args, **argd)
                    finally:
                        tearDown()
                else:
                    func(*args, **argd)

            return wrapper

        return decorator
