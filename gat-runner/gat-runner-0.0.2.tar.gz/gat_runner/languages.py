# coding: utf-8
import logging
import os
import re
import shutil
import subprocess
import sys


LANGUAGES = {
    'py': 'Python',
    'py2': 'Python 2.7',
    'py3': 'Python 3.3',
    'pypy': 'PyPy',
    'st': 'SmallTalk',
    'rb': 'Ruby',
    'rb2': 'Ruby2',
    'scala': 'Scala',
    'java': 'Java',
    'java6': 'Java6',
    'java7': 'Java7',
    'cs': 'C#',
    'c': 'C',
    'cpp': 'C++',
    'go': 'Go',
    'm': 'Objective-C',
    'js': 'Javascript',
    'lua': 'Lua',
    'gy': 'Groovy',
    'gvy': 'Groovy',
    'groovy': 'Groovy',
    'erl': 'Erlang',
    'hs': 'Haskell',
    'clj': 'Clojure',
    'php': 'PHP',
}


class GATFile(object):
    def __init__(self, filepath, filename, extension, language):
        self.filepath = filepath
        self.filename = filename
        self.extension = extension
        self.language = language

    def get_runtime_command(self):
        return [self.language, self.filepath]

    def get_compilation_command(self):
        pass

    def compile(self):
        compilation_command = self.get_compilation_command()
        if compilation_command:
            try:
                logging.debug('[GAT] %s' % compilation_command)
                # If shell is True, the specified command will be executed through the shell.
                # This can be useful if you are using Python primarily for the enhanced control flow it offers over most system shells and
                # still want convenient access to other shell features such as shell pipes, filename wildcards, environment variable expansion,
                # and expansion of ~ to a user’s home directory.
                # If shell is True, it is recommended to pass args as a string rather than as a sequence.
                result = subprocess.call(compilation_command)
            except Exception as e:
                logging.error('Error on execute the command: %s' % compilation_command)
                raise e
            if result == 0:
                print('%s compilation successful: %s' % (self.language, self.filepath))
            else:
                raise OSError('Compilation error: %s (%s)' % (compilation_command, result))


class PythonFile(GATFile):
    def get_compilation_command(self):
        return ['python', '-m', 'py_compile', self.filepath]

    def get_runtime_command(self):
        return ['python', self.filepath]


class Python3File(GATFile):
    def get_compilation_command(self):
        return ['python3.3', '-m', 'py_compile', self.filepath]

    def get_runtime_command(self):
        return ['python3.3', self.filepath]


class RubyFile(GATFile):
    def get_compilation_command(self):
        return ['ruby', '-c', self.filepath]

    def get_runtime_command(self):
        return ['ruby', self.filepath]


class JavaFile(GATFile):
    def get_classpath(self):
        if sys.platform.startswith('win'):
            return '.;./*;lib/*;bin'
        else:
            return '.:./*:lib/*:bin'

    def get_compilation_command(self):
        if os.path.exists('bin'):
            shutil.rmtree('bin')
        os.mkdir('bin')
        # return ['javac', '-d', 'bin', '-source', '1.6', '-target', '1.6', '-classpath', self.get_classpath(), self.filepath]
        return ['javac', '-d', 'bin', '-classpath', self.get_classpath(), self.filepath]

    def get_runtime_command(self):
        main_class = re.sub('.*/', '', self.filepath).replace('.%s' % self.extension, '')
        return ['java', '-classpath', self.get_classpath(), main_class]


class CFile(GATFile):
    def get_compilation_command(self):
        return ['gcc', self.filepath, '-o', '%s.bin' % self.filepath]

    def get_runtime_command(self):
        return ['%s.bin' % self.filepath]


class CppFile(GATFile):
    def get_compilation_command(self):
        return ['g++', self.filepath, '-o', '%s.bin' % self.filepath]

    def get_runtime_command(self):
        return ['%s.bin' % self.filepath]


class ScalaFile(GATFile):
    def get_classpath(self):
        if sys.platform.startswith('win'):
            return '".;./*;lib/*"'
        else:
            return '".:./*:lib/*"'

    def get_compilation_command(self):
        return ['scalac', '-classpath', self.get_classpath(), self.filepath]

    def get_runtime_command(self):
        main_class = self.filepath.replace('.%s' % self.extension, '')
        return ['java', '-classpath', self.get_classpath(), main_class]


class JavascriptFile(GATFile):
    def get_runtime_command(self):
        return ['phantomjs', self.filepath]


class SmalltalkFile(GATFile):
    def get_runtime_command(self):
        return ['gst', self.filepath]


SUPPORTED_LANGUAGES = {
    'py': PythonFile,
    'py3': Python3File,
    'rb': RubyFile,
    'java': JavaFile,
}

CUSTOM_LANGUAGE_VERSIONS = {
    'py3': 'Python 3.3'
}


class GATFileFactory(object):
    @staticmethod
    def create(filepath, language=None):
        filename, extension = GATFileFactory.get_filename_and_extension(filepath)
        if not language:
            language = extension
        if language not in list(SUPPORTED_LANGUAGES.keys()):
            raise ValueError('Programming language not supported: %s (%s)' % (language, filepath))
        GATFile = SUPPORTED_LANGUAGES[language]
        return GATFile(filepath, filename, extension, language)

    @staticmethod
    def get_filename_and_extension(filepath):
        fullfilename = os.path.splitext(os.path.basename(filepath))
        filename = fullfilename[0]
        extension = fullfilename[1]
        return filename, extension.replace('.', '')
