from __future__ import absolute_import
import logging

import re

from clover.sourcefile import SourceFile


logger = logging.getLogger('clover.sourcefiles.Javascript')


class JavascriptSourceFile(SourceFile):
    scanned = False
    _BASE_REGEX_STRING = r'^\s*goog\.%s\(\s*[\'"](.+)[\'"]\s*\)'
    _PROVIDE_REGEX = re.compile(_BASE_REGEX_STRING % 'provide')
    _REQUIRE_REGEX = re.compile(_BASE_REGEX_STRING % 'require')
    # Matches a "/* ... */" comment.
    # Note: We can't definitively distinguish a "/*" in a string literal without a
    # state machine tokenizer. We'll assume that a line starting with whitespace
    # and "/*" is a comment.
    _COMMENT_REGEX = re.compile(
        r"""
        ^\s*   # Start of a new line and whitespace
        /\*    # Opening "/*"
        .*?    # Non greedy match of any characters (including newlines)
        \*/    # Closing "*/""",
        re.MULTILINE | re.DOTALL | re.VERBOSE)
  
    # cached list of require names
    _requires = None

    # cached list of provide names
    _provides = None

    # cached java sourcefile reference
    _java_sourcefile = None

    # enable caching of the java Sourcefile references
    CACHE_JAVA_SOURCEFILE = False
  
    def has_provide_goog_flag(self, source):
        """Determines whether the @provideGoog flag is in a comment."""
        for comment_content in self._COMMENT_REGEX.findall(source):
            if '@provideGoog' in comment_content:
                return True

        return False
    

    def get_provide_names(self):
        """ Get list of names providing. """

        if self._provides is None or self.is_cache_expired():
            self.scan_provides_requires()

        return self._provides

    def get_require_names(self):
        """ Get list of names requiring. """
        if self._requires is None or self.is_cache_expired():
            self.scan_provides_requires()

        return self._requires
    
    def scan_provides_requires(self):
        """Fill in provides and requires by scanning the source."""
        self._provides = []
        self._requires = []
        
        code = self.get_code_cached()
        stripped_source = self._COMMENT_REGEX.sub('', code)
        source_lines = stripped_source.splitlines()
        for line in source_lines:
            
            match = self._PROVIDE_REGEX.match(line)
            if match:
                self._provides.append(match.group(1))
                
            match = self._REQUIRE_REGEX.match(line)
            if match:
                self._requires.append(match.group(1))
                
        if self.has_provide_goog_flag(code):
            if len(self._provides) or len(self._requires):
                raise Exception('Base file should not provide or require namespaces.')
            self._provides.append('goog')
      
    def build_sourcefile(self, client):
        """ Build a sourcefile; keeping it cached if it hasn't been modified. 
        """
        
        if self.CACHE_JAVA_SOURCEFILE:
            if self._java_sourcefile is None or  self.is_cache_expired():
                self._java_sourcefile = self._build_sourcefile(client)
            return self._java_sourcefile
        else:
            return self._build_sourcefile(client)

    def _build_sourcefile(self, client):
        if self.precompile:
            code = self.get_code_cached()
            assert isinstance(code, basestring), "Code must be a string"
            return client.new_sourcefile_from_code(self.path, code)
        else:
            return client.new_sourcefile_from_file(self.path)
