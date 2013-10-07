#! /usr/bin/env python
"""Test of routing the modification of one node to another"""
import OpenGL 
OpenGL.FORWARD_COMPATIBLE_ONLY = True
from OpenGLContext_qt.qtcontext import VRMLContext as BaseContext
import os, sys
from OpenGL.GL import *
from OpenGLContext.events.timer import Timer
from OpenGLContext.scenegraph.basenodes import *
try:
    from OpenGLContext.loaders.loader import Loader
except ImportError, err:
    print """This demo requires the VRML97 loader"""

class TestContext( BaseContext ):
    """Context to load wrls/box.wrl and watch routing changes

    The context loads the given file, gets a pointer to a
    particular node within the file, then modifies that node's
    rotation field. The routes in the file forward the changes
    to another node, causing both boxes on-screen to rotate.
    """
    initialPosition = (0,0,10)
    def OnInit( self ):
        """Load the image on initial load of the application"""
        self.frameCounter = None
        buffer = ShaderBuffer(
            buffer = [ 
                [  0, 1, 0,  0,1,0 ],
                [ -1,-1, 0,  1,1,0 ],
                [  1,-1, 0,  0,1,1 ],
                
                [  2,-1, 0,  1,0,0 ],
                [  4,-1, 0,  0,1,0 ],
                [  4, 1, 0,  0,0,1 ],
                [  2,-1, 0,  1,0,0 ],
                [  4, 1, 0,  0,0,1 ],
                [  2, 1, 0,  0,1,1 ],
            ],
        )
        self.sg = sceneGraph(
            children = [
                ShaderGeometry(
                    # test of shader geometry "shape" type...
                    DEF = 'ShaderGeom',
                    slices = [
                        ShaderSlice( 
                            offset=0,
                            count=9,
                        ),
                    ],
                    uniforms = [
                        FloatUniform3f( 
                            name = 'mixColor',
                            value = [1.0,0.0,0.0],
                        ),
                    ],
                    attributes = [
                        ShaderAttribute(
                            name = 'position',
                            offset = 0,
                            stride = 24,
                            size = 3,
                            dataType = 'FLOAT',
                            buffer = buffer,
                            isCoord=True,
                        ),
                        ShaderAttribute(
                            name = 'Color',
                            offset = 12,
                            stride = 24,
                            size = 3,
                            dataType = 'FLOAT',
                            buffer = buffer,
                        ),
                    ],
                    appearance = 	Shader(
                        objects = [GLSLObject(
                            DEF = 'ShaderGeom_shader',
                            shaders = [
                                GLSLShader( 
                                    source = [
                                        """#version 330
        attribute vec3 position;
        attribute vec3 Color;
        uniform vec3 mixColor;
        varying vec4 baseColor;
        void main() {
            gl_Position = gl_ModelViewProjectionMatrix * vec4( position,1.0);
            baseColor = mix( vec4(mixColor,1.0), vec4(Color,1.0), .5 );
        }""",
                                    ],
                                    type = "VERTEX",
                                ),
                                GLSLShader(
                                    source = ["""#version 330
        varying vec4 baseColor;
        void main() { 
            gl_FragColor = baseColor;
        }"""],
                                    type = "FRAGMENT",
                                ),
                            ],
                        ),]
                    ),
                )
        ]
        )
#        gl
#        self.sg = Loader.load( os.path.join("wrls","box.wrl") )

if __name__ == "__main__":
    TestContext.ContextMainLoop(
        definition = {
            'profile': 'core',
        }
    )
