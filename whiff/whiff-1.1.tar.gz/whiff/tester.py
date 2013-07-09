"""
Test bootstrap module primarily intended for testing WHIFF applications,
but it could be used for other wsgi apps.

At the moment it is not carefully conformant to the WSGI spec when emulating
WSGI.

There are no provisions for "expected exceptions".
"""

# quoted delimiters "}}" "{{" are not handled correctly.

import glob
import traceback
import cStringIO
import sys
import rdjson.jsonParse
import types
import resolver
import time
import os

PAGE_DUMP_FORMAT = """
{{env whiff.content_type: "text/html"/}}

{{comment
    Automatically generated wsgi test case captured from test run.
    You may want to edit this by hand to remove unneeded environment entries.

    SCRIPT_NAME = %(SCRIPT_NAME)s
    PATH_INFO = %(PATH_INFO)s
    QUERY_STRING = %(QUERY_STRING)s
/}}

{{include "%(TESTER_URL)s"}}

{{comment Input parameters /}}

{{data wsgi_environment}}
%(WSGI_ENVIRONMENT)s
{{/data}}

{{text wsgi_input}}%(WSGI_INPUT)s{{/text}}

{{using application_to_test}}%(APPLICATION_TO_TEST)s{{/using}}

{{comment Expected output parameters for comparison. /}}

{{text expect_status}}%(EXPECT_STATUS)s{{/text}}

{{data expect_headers}}
%(EXPECT_HEADERS)s
{{/data}}

{{text expect_output}}%(EXPECT_OUTPUT)s{{/text}}

{{/include}}
"""

class WhiffTestWrapper:
    def __init__(self,
                 application_to_test,
                 wsgi_input=False, # should be a string (converted to a file on invocation), or false for no input
                 wsgi_environment=None, # should include other environment to emulate except for files (dict)
                 expect_status=None, # status to expect on start_response or None for don't care
                 expect_headers=None, # expected headers on start_response or None for don't care
                 expect_output=None, # expected output from __call__ iterable, string or None for don't care
                 source_path=None, # name of file where the test came from
                 #diagnostics_path=None, # path of file for storing diagnostics
                 #observed_test_path=None, # path of file for storing observed behaviour as a test case.
                 ):
        assert wsgi_input is False or type(wsgi_input) in types.StringTypes
        assert wsgi_environment is None or type(wsgi_environment) is types.DictType
        assert expect_status is None or type(expect_status) is types.StringType
        assert expect_headers is None or type(expect_headers) is types.TupleType
        assert source_path is None or type(source_path) is types.StringType
        #pr"WhiffTestWrapper __init__ from source", repr(source_path)
        self.source_path_stream = source_path
        self.source_path = None # must be evaluated at wsgi __call__
        self.application_to_test = application_to_test
        self.wsgi_input = wsgi_input
        if wsgi_environment is None:
            wsgi_environment = {}
        else:
            # make convert to strings where appropriate
            env = {}
            for (k,v) in wsgi_environment.items():
                if type(v) is types.UnicodeType:
                    v = str(v)
                env[str(k)] = v
            wsgi_environment = env
        self.wsgi_environment = wsgi_environment
        
        self.expect_headers = expect_headers
        self.expect_status = expect_status
        self.expect_headers = expect_headers
        self.expect_output = expect_output
        self.received_headers = None
        self.received_output = None
        self.received_status = None
        self.anomalies = []
        self.exc_info = None
        self.external_start_response = None
    def test_failed(self):
        return len(self.anomalies)>0
    def observed_report(self, tester_url="WhiffTester"):
        # observed behaviour dumped as a testing page.
        # unhandled exceptions not reported.
        status = self.received_status
        headers = self.received_headers
        output = self.received_output
        application_text = getattr(self.application_to_test, "text", None)
        input = self.wsgi_input
        if input is None:
            input = ""
        env = clean_env(self.wsgi_environment)
        if status is None:
            return "cannot generate test case: no status"
        if headers is None:
            return "cannot generate test case: no headers"
        if output is None:
            return "cannot generate test case: no output"
        D = {}
        D["TESTER_URL"] = tester_url
        D["WSGI_ENVIRONMENT"] = stream.mystr(rdjson.jsonParse.format(env))
        D["SCRIPT_NAME"] = repr(env.get("SCRIPT_NAME"))
        D["PATH_INFO"] = repr(env.get("PATH_INFO"))
        D["QUERY_STRING"] = repr(env.get("QUERY_STRING"))
        D["WSGI_INPUT"] = input
        D["APPLICATION_TO_TEST"] = application_text
        D["EXPECT_STATUS"] = status
        D["EXPECT_HEADERS"] = stream.mystr(rdjson.jsonParse.format(headers))
        D["EXPECT_OUTPUT"] = stream.mystr(output)
        return PAGE_DUMP_FORMAT % D
    def __call__(self, env, start_response):
        "default interpretation as wsgi -- return an html report"
        #pr"tester __call__ environment"
        self.source_path = self.source_path_stream.get_content(env)
        #for pair in env.items():
            #prpair
        self.test_application()
        start_response('200 OK', [('Content-Type', 'text/html')])
        return self.html_report()
    def test_application(self, external_start_response=None):
        self.capture_application_to_test(external_start_response)
        self.find_anomalies()
    def capture_application_to_test(self, external_start_response):
        env = self.wsgi_environment.copy()
        self.external_start_response = external_start_response
        start_response = self.capture_start_response
        if self.wsgi_input is not None and self.wsgi_input is not False:
            env["wsgi.input"] = cStringIO.StringIO(self.wsgi_input)
        # XXXX other wsgi parameters like the error stream are deferred for now
        result_list = None
        try:
            call_result = self.application_to_test(env, start_response)
            result_list = list(call_result)
            self.received_output = "".join(result_list)
        except:
            print "VERBOSE: GOT EXCEPTION"
            info = sys.exc_info()
            for a in info:
                print a # verbose
            traceback.print_tb(info[-1]) # verbose
            self.exc_info = info
        return result_list
    def capture_start_response(self, status, headers):
        self.received_status = status
        self.received_headers = headers[:]
        sr = self.external_start_response
        if sr is not None:
            sr(status, headers)
    def anomaly(self, *info):
        self.anomalies.append(info)
    def find_anomalies(self):
        # invoke after call
        exc_info = self.exc_info
        if exc_info is not None:
            (type, value, traceback) = exc_info
            self.anomaly("exception occurred", type, value)
        expect_status = self.expect_status
        received_status = self.received_status
        if received_status is None:
            self.anomaly("no status received")
        elif expect_status is not None:
            if expect_status!=received_status:
                self.anomaly("expected and received statuses do not match", expect_status, received_status)
        if self.expect_headers is not None:
            expect_headers = clean_headers(self.expect_headers)
            received_headers = clean_headers(self.received_headers)
            if received_headers is None:
                self.anomaly("no headers received")
            elif expect_headers!=received_headers:
                self.anomaly("received and expected headers do not exactly match")
                missing = False
                for pair in expect_headers:
                    if pair not in received_headers:
                        self.anomaly("expected_header pair not received", pair)
                        missing = True
                for pair in received_headers:
                    if pair not in expect_headers:
                        self.anomaly("received pair was not expected", pair)
                        missing = True
                if not missing:
                    self.anomaly("received and expected headers in differing order")
        expect_output = self.expect_output
        received_output = self.received_output
        if received_output is None:
            self.anomaly("no output received")
        elif expect_output is not None:
            # ignore differences in surrounding whitespace (for editting convenience)
            expect_output = expect_output.strip()
            received_output = received_output.strip()
            if expect_output!=received_output:
                self.anomaly("expected and received output do not exactly match")
            le = len(expect_output)
            lr = len(received_output)
            if le!=lr:
                self.anomaly("expected and received output lengths differ", le, lr)
            minlen = min(le, lr)
            for index in xrange(minlen):
                if expect_output[index]!=received_output[index]:
                    prefix_start = min(0, index-20)
                    suffix_end = index+20
                    expect_prefix = expect_output[prefix_start:index]
                    expect_suffix = expect_output[index:suffix_end]
                    received_prefix = received_output[prefix_start:index]
                    received_suffix = received_output[index:suffix_end]
                    self.anomaly("first output difference at character "+repr(index), ("expected", expect_prefix, expect_suffix), ("got", received_prefix, received_suffix))
                    break
        # end
    def format_anomalies(self):
        anomalies = self.anomalies
        for t in anomalies:
            message = t[0]
            yield message+"\n"
            for data in t[1:]:
                yield "    "+repr(data)+"\n"
    def pass_fail_text(self):
        "respond with 'pass' if passing, else 'fail' followed by anomaly lines"
        not implemented
    def html_report(self):
        yield "<h1>html report for wsgi test application (path=%s)</h1>\n" % self.source_path
        apptext = str( getattr(self.application_to_test, "text", None) )
        yield "<pre>"+qq(apptext)+"</pre>"
        yield "<br>\n"
        if self.wsgi_input is not None:
            yield "<h2>input string</h2>\n"
            yield reprq(self.wsgi_input)+"\n"
        yield "<h2>environment</h2>\n"
        env = self.wsgi_environment
        yield "length="+reprq(len(env))+"<br>\n"
        for pair in env.items():
            yield reprq(pair)+"<br>\n"
        # check for anomalies...
        if self.anomalies:
            yield "<h2>anomalies</h2>\n"
            yield "<pre>\n"
            for x in self.format_anomalies():
                yield qq(x)
            yield "</pre>\n"
        else:
            yield "<h2>no anomalies reported</h2>\n"
        yield "<h2>status = "+reprq(self.received_status)+"</h2>\n\n"
        if self.received_output is None:
            yield "<h2>no output</h2>\n\n"
        else:
            yield "<h2>output</h2>\n\n"
            yield "length = "+reprq(len(self.received_output))
            yield "\n\n<pre>"
            yield qq(self.received_output)
            yield "</pre>\n"

def qq(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def reprq(x):
    return qq(repr(x))

def clean_env(env):
    "for dumping purposes, remove unprintable things from the wsgi environment" # verbose
    result = env.copy()
    # remove all wsgi parameters which do not map to a string
    for (k,v) in env.items():
        if k.startswith("wsgi.") and type(v) not in types.StringTypes:
            del result[k]
    return result

def clean_headers(headers):
    if not headers:
        return headers
    # make sure we have a list of tuples! and remove time change sensitive headers
    result = []
    for (a,b) in headers:
        ua = a.upper()
        if ua.startswith("EXPIRE") or ua.startswith("CACHE"):
            # ignore this header
            pass
        else:
            result.append( (a,b) )
    #return [ (a,b) for (a,b) in headers ]
    return result

def timestamp():
    tp = time.localtime()
    tps = [str(x) for x in tp]
    return "_".join(tps)
    
class CaptureTestCase:
    """middleware to capture a test case and output the result to a file as a template"""
    def __init__(self, page, test_case_path, appendTimeStamps=False):
        self.target_application = page
        self.test_case_path = test_case_path
        self.appendTimeStamps = appendTimeStamps
    def __call__(self, env, start_response):
        (input, fake_env) = self.modify_env(env)
        tester = WhiffTestWrapper(self.target_application, input, fake_env)
        result_list = tester.capture_application_to_test(start_response)
        if result_list is None:
            raise ValueError, "test case returned no value"
        file_text = tester.observed_report()
        file_path = self.test_case_path
        if self.appendTimeStamps:
            file_path = file_path + "." + timestamp()
        outfile = open(file_path, "w")
        outfile.write(file_text)
        outfile.close()
        return result_list
    def modify_env(self, env):
        modified_env = env.copy()
        inputtext = ""
        content_length_str = env.get("CONTENT_LENGTH")
        if content_length_str:
            content_length = int(content_length_str)
            input = env.get("wsgi.input")
            if input:
                inputtext = input.read(content_length)
                del modified_env["wsgi.input"]
        return (inputtext, modified_env)

def Capture(target_application, test_case_path):
    if isinstance(target_application, resolver.WsgiComponentFactory):
        # convert to a real application (it better require no arguments ???)
        target_application = target_application.makeWsgiComponent()
    bind_root = getattr(target_application, "bind_root", None)
    #pr"Capture found bind_root", target_application, bind_root
    app = CaptureTestCase(target_application, test_case_path)
    return resolver.WsgiApplicationWrapper(app, bind_root_operation=bind_root)

class TestError(ValueError):
    "A whiff test failed"

class TestSuiteDirectory:
    def __init__(self, root_application, test_suite_path, extension=".testcase"):
        self.root_application = root_application
        self.test_suite_path = test_suite_path
        self.extension = extension
    def __call__(self, env, start_response):
        "return an index of test cases or the html diagnostic for an individual test case"
        payload = None
        path_info = env.get("PATH_INFO", "")
        spath = path_info.split("/")
        test_case_name = spath[-1]
        if not test_case_name:
            payload = self.html_directory("Please choose a test case.")
        try:
            test_case = self.get_test_case(test_case_name)
        except:
            payload = self.html_directory("could not find test case: "+repr(test_case_name))
        else:
            test_case.test_application()
            payload = self.test_case_report(test_case, test_case_name)
        start_response('200 OK', [('Content-Type', 'text/html')])
        return payload
    def test_case_report(self, test_case, name):
        yield "test case directory = %s\n" % repr(self.test_suite_path)
        if test_case.test_failed():
            yield "<h1>test case %s FAILED</h1>\n" % name
        else:
            yield "<h1>test case %s SUCCEEDED</h1>\n" % name
        for diagnostic_text in test_case.html_report():
            yield diagnostic_text
    def html_directory(self, message=None):
        if message:
            yield message
        yield "<h1>test cases in directory %s</h1>\n" % self.test_suite_path
        count = 0
        for filename in self.get_test_case_filenames():
            count += 1
            yield '<a href="%s">%s</a><br>\n' % (filename, filename)
        yield "<br><br> total = "+repr(count)
        yield "\n\n"
    def run_all(self, diagnostic_directory_path=None, verbose=True):
        "run all test suites and raise an error at the end if any fail, optionally dump html diagnostics to directory"
        # clear the diagnostic directory
        for path in glob.glob(diagnostic_directory_path +"/*"):
            print "VERBOSE: deleting", path
            os.unlink(path)
        test_case_filenames = self.get_test_case_filenames()
        failures = 0
        for filename in test_case_filenames:
            test_case = self.get_test_case(filename)
            status = "SUCCEEDED"
            test_case.test_application()
            if test_case.test_failed():
                failures += 1
                status = "FAILED"
                if verbose:
                    print "VERBOSE: FAILED OUTPUT"
                    print test_case.received_output # verbose
            if diagnostic_directory_path is not None:
                diagnostic_filename = "%s.%s.html" % (status, filename)
                diagnostic_path = os.path.join(diagnostic_directory_path, diagnostic_filename)
                diagnostic_seq = test_case.html_report()
                out = file(diagnostic_path, "w")
                for diagnostic_text in diagnostic_seq:
                    out.write(diagnostic_text)
                out.close()
            if verbose: print status, filename
        if failures>0:
            raise TestError, str(failures)+" test case failures for directory "+repr(self.test_suite_path)+" diagnostics in "+repr(diagnostic_directory_path)
    def get_test_case_filenames(self):
        result = []
        dir_path = self.test_suite_path
        allfilenames = os.listdir(dir_path)
        extension = self.extension
        for filename in allfilenames:
            if filename.endswith(extension):
                result.append(filename)
        return result
    def get_test_case(self, filename):
        "parse the test case to get test arguments, replace the application with the root_app"
        # parse the page
        #filepath = os.path.join(self.test_suite_path, filename)
        filepath = resolver.pathjoin(self.test_suite_path, filename)
        text = open(filepath).read()
        (test, result, cursor) = parseTemplate.parse_page(text, file_path=filepath)
        if not test:
            return (False, "parse for test case failed: "+repr((result, cursor)))
        if cursor<len(text):
            raise ValueError, "test case page not consumed "+repr(text[cursor:cursor+100])
        test_case_page = result
        # extract the urlcomponent from the parsed page
        urlcomp = None
        for component in test_case_page.get_components():
            if isinstance(component, urlcomponent.UrlComponent):
                if urlcomp is not None:
                    return (False, "too many url components found in parsed test case page")
                urlcomp = component
        if urlcomp is None:
            return (False, "did not find url component in test case page")
        # get the urlcomponent arguments
        arguments = urlcomp.get_arguments_dictionary()
        # ignore the application_to_test
        del arguments["application_to_test"]
        # bind the arguments to the root_application
        bound_arguments = stream.bind_arguments(arguments, {}, self.root_application, [], [], filename)
        # set the target app to be root_application
        bound_arguments["application_to_test"] = self.root_application
        # create and return the test case
        result = WhiffTestWrapper(**bound_arguments)
        return result

WhiffTester = resolver.WsgiClassWrapper(WhiffTestWrapper)
import parseTemplate
import urlcomponent
import stream

