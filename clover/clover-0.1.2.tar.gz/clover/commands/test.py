import sys
import argparse

import selenium
from selenium import webdriver

from clover.builder import Builder
from clover.command import Command
from clover.config.multiconfig import MultiDocConfig


DRIVER_MAP = {
    'chrome': webdriver.PhantomJS,
    'firefox': webdriver.PhantomJS,
    'remote': webdriver.Remote,
    'phantomjs': webdriver.PhantomJS   
}

argparser = argparse.ArgumentParser(description="""\

""")
argparser.add_argument('config')
argparser.add_argument('path', help="path to the test file.")
argparser.add_argument('-d', '--driver', default='chrome', help="The driver to use.")
argparser.add_argument('--server', default='localhost:2323', help="Address to the clover server.")
argparser.add_argument('--xunit', default=False, help="Path to xunit xml.")
argparser.add_argument('--coverage', default=False, help="Path to collect coverage data.")
argparser.add_argument('--coverage-format', default=False, help="Coverage format.")



def parse_stacktrace(trace):
    #https://github.com/eriwen/javascript-stacktrace/blob/master/stacktrace.js
    pass



class Test(Command):
    """ Uses a webdriver to run the javascript testrunner.
    """
    def start(self, args):
        
        parsed_args = argparser.parse_args(args)
        
        service_args = []
        phantom = webdriver.Chrome(service_args=service_args)
        phantom.set_window_size(1024, 768)
        
        # TODO: if no path, or glob path, use rpc to get all paths
        
        url ="http://localhost:2323/configs/%s/testcommand?path=%s" % (parsed_args.config, parsed_args.path)
        phantom.get(url)
        
        
        try:
            # XXX: this does not work with phantomjs
            RESULT = phantom.execute_async_script('''
            RUNTESTS(arguments[arguments.length - 1])
            ''')
            
            print RESULT
        except selenium.common.exceptions.WebDriverException, e:
            pass
        
        
        phantom.close()
        #phantom.execute_script("return TEST_RESULT")
        
        # wait for the test to finish and capture TEST_RESULT

#print dir(phantom)
#if not phantom.save_screenshot("test.png"):
#   raise IOError("Unable to save screenshot to: ")

strin = """
/**
 * parse stacktrace for v8 - works in node.js and chrome
 */
function _parserV8(error){
    // start parse the error stack string
    var lines   = error.stack.split("\n").slice(1);
    var stacktrace  = [];
    lines.forEach(function(line){
        if( line.match(/\(native\)$/) ){
            var matches = line.match(/^\s*at (.+) \(native\)/);
            stacktrace.push(new Stacktrace.Frame({
                fct : matches[1],
                url : 'native',
                line    : 1,
                column  : 1
            }));
        }else if( line.match(/\)$/) ){
            var matches = line.match(/^\s*at (.+) \((.+):(\d+):(\d+)\)/);
            stacktrace.push(new Stacktrace.Frame({
                fct : matches[1],
                url : matches[2],
                line    : parseInt(matches[3], 10),
                column  : parseInt(matches[4], 10)
            }));
        }else{
            var matches = line.match(/^\s*at (.+):(\d+):(\d+)/);
            stacktrace.push(new Stacktrace.Frame({
                url : matches[1],
                fct : '<anonymous>',
                line    : parseInt(matches[2], 10),
                column  : parseInt(matches[3], 10)
            }));
        }
    });
    return stacktrace;
};

/**
 * parse the stacktrace from firefox
 */
function _parserFirefox(error){
    // start parse the error stack string
    var lines   = error.stack.split("\n").slice(0, -1);
    var stacktrace  = [];
    lines.forEach(function(line){
        var matches = line.match(/^(.*)@(.+):(\d+)$/);
        stacktrace.push(new Stacktrace.Frame({
            fct : matches[1] === '' ? '<anonymous>' : matches[1],
            url : matches[2],
            line    : parseInt(matches[3], 10),
            column  : 1
        }));
    });
    return stacktrace;
};


//////////////////////////////////////////////////////////////////////////////////
//      Stacktrace.Frame                        //
//////////////////////////////////////////////////////////////////////////////////

/**
 * handle stack frame
 * 
 * TODO do a .fromOriginId()
 */
StackFrame    = function(opts){
    this.url    = opts.url;
    this.fct    = opts.fct;
    this.line   = opts.line;
    this.column = opts.column;
};

/**
 * return the origin String
 * @return {String} the origin of the stackframe
 */
StackFrame.prototype.originId = function(){
    var str = this.fct + '@' + this.url + ':' + this.line + ':' + this.column;
    return str;
};

/**
 * get the basename of the url
 * @return {string}
 */
StackFrame.prototype.basename = function(){
    return this.url.match(/([^/]*)$/)[1]    || ".";
};
"""

if __name__ == '__main__':
    Build.run(sys.argv[1:])
