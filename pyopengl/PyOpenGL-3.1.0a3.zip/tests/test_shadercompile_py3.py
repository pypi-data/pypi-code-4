from OpenGL.GL import shaders, GL_VERTEX_SHADER

import pygame
screen = pygame.display.set_mode((800, 800), pygame.OPENGL)

VERTEX_SHADER = shaders.compileShader(b"""
    #version 130
   
    void main()
    {
    }
    """, GL_VERTEX_SHADER)
