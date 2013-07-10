from os import path, environ
from datetime import datetime, timedelta
import sys
import os
import subprocess

class JadeLessCoffeeMiddleware(object):
    directories = None;
    last_compile = datetime.now()

    def __init__(self, app, directories=None):
        self.app = app;
        self.directories = directories
        JLC_DIRS = environ.get("JLC_DIRS", None)
        if directories == None and JLC_DIRS is not None:
            self.directories = JLC_DIRS

        print('JadeLessCoffee compiler will run at every request...\n');

    def __call__(self, environ, response):
    	# if the compiler has run in the last 4 seconds, don't run it again.
    	if datetime.now() - self.last_compile < timedelta(0, 4):
    		return self.app(environ, response)
        
        self.last_compile = datetime.now()

        #if the JLC_DIRS is set then just do them
        if self.directories is not None:
            if isinstance(self.directories, tuple):
                try:
                    for jlcsource, jlcdestination in self.directories:
                        self.compile(path.normpath(jlcsource), path.normpath(jlcdestination))
                except:
                    print("Cannot compile jlc directories. directories should be a tuple of tuples. \ne.g. JLC_DIRS = (\n    ('/path/to/src', '/path/to/'),\n    ('/path/to/other/src', '/path/to/other'),\n)")
            else:
                try:
                    jlcsource, jlcdestination = self.directories
                    self.compile(path.normpath(jlcsource), path.normpath(jlcdestination))
                except:
                    print("Cannot compile jlc directories. directories should be a tuple of tuples. \ne.g. JLC_DIRS = (\n    ('/path/to/src', '/path/to/'),\n    ('/path/to/other/src', '/path/to/other'),\n)")


        return self.app(environ, response)


    def compile(self, source_directory, output_directory):
        if not path.exists(source_directory):
            #print('No such file or directory: "%s"' % source_directory)
            return
        if not path.exists(output_directory):
            #print('No such file or directory: "%s"' % output_directory)
            return

        # shell=True is necessary on windows due to jlc being provided by environment variables in node
        proc = subprocess.Popen("jlc --quiet --incremental --python --out \"%s\" \"%s\"" % (output_directory, source_directory), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        
        if len(err) > 0 and err is not None:
            try:
                error_object = eval(err)
                filename = error_object['filename']
                line_number = error_object['lineNumber']
                offset = error_object['offset']
                line = error_object['lineCode']
                message = 'An error occurred in JadeLessCoffee code.\n%s' % error_object['message']
            except:
                filename = ''
                line_number = 0
                offset = ''
                line = ''
                message = 'An indeterminate error occurred in JadeLessCoffee code.\n%s' % err
                
            raise SyntaxError(message, (filename, line_number, offset, line))
