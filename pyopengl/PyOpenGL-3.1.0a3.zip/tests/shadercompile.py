'''
This module shows...
a) how GLSL error locations are presented depending on how the shader source is passed
   (one string vs array of strings),
b) whether a single token can spread across several source strings.

'''
import unittest, pygame, pygame.display, time, traceback, os, sys
from functools import wraps
import logging 
logging.basicConfig()
import OpenGL 
OpenGL.CONTEXT_CHECKING = True
OpenGL.FORWARD_COMPATIBLE_ONLY = False

from pygamegltest import gltest

import ctypes
from OpenGL import GL

SCREEN = None

# An example shader with an error in line 5

source = '''\
#version 330                          // 1
                                      // 2
void main() {                         // 3
                                      // 4
    gl_Position = vec4(1,2,three,4);  // 5   error here
                                      // 6
}                                     // 7
'''

# This shader is correct, but is split into two strings inside a token

alt_source_list = [
    '#version 330\nvo',
    'id main() { gl_Position = vec4(',
    '0,0,0,0);',
    '}',
]


@gltest
def run(splits):

    shader = GL.glCreateShader(GL.GL_VERTEX_SHADER)

    if splits:
        keep_eols = True
        source_lines = source.splitlines(keep_eols)     #  It is important to keep newlines.
        c_sources = map(ctypes.c_char_p, source_lines)
    else:
        c_sources = [ctypes.c_char_p(source)]

    
    ctype_char_p_arr = ctypes.c_char_p * len(c_sources)
    c_sources_array = ctype_char_p_arr(*c_sources)

    if splits:
        assert len(c_sources) > 1
    else:
        assert len(c_sources) == 1

    GL.glShaderSource.wrappedOperation(shader, len(c_sources), c_sources_array, None)
    GL.glCompileShader(shader)
    print 'Compile status:', bool(GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS))
    print 'Info log:'
    print GL.glGetShaderInfoLog(shader)


@gltest
def run2():

    shader = GL.glCreateShader(GL.GL_VERTEX_SHADER)
    c_sources = map(ctypes.c_char_p, alt_source_list)
    ctype_char_p_arr = ctypes.c_char_p * len(c_sources)
    c_sources_array = ctype_char_p_arr(*c_sources)

    assert len(c_sources) == 4

    GL.glShaderSource.wrappedOperation(shader, len(c_sources), c_sources_array, None)
    GL.glCompileShader(shader)
    print 'Compile status:', bool(GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS))
    print 'Info log:'
    print GL.glGetShaderInfoLog(shader)



def main():
    print '# Shader as lines:'
    print '(Expected an error in line 5)'
    run(True)
    print '# Shader as one block:'
    print '(Expected an error in line 5)'
    run(False)
    print '# Tokens across block'
    print '(Expected success if the token can span through strings)'
    run2()


if __name__ == '__main__':
    main()
