from math import pi

from .utils.mathematical import mult_by_scalar3

#==============================================================================
# GEOMETRY
#==============================================================================

X_AXIS = (1.0, 0.0, 0.0)
X_AXIS_NEG = (-1.0, 0.0, 0.0)
Y_AXIS = (0.0, 1.0, 0.0)
Y_AXIS_NEG = (0.0, -1.0, 0.0)
Z_AXIS = (0.0, 0.0, 1.0)
Z_AXIS_NEG = (0.0, 0.0, -1.0)

RIGHT_AXIS = X_AXIS
LEFT_AXIS = X_AXIS_NEG
UP_AXIS = Y_AXIS
DOWN_AXIS = Y_AXIS_NEG
OUT_AXIS = Z_AXIS  # out of the screen
IN_AXIS = Z_AXIS_NEG  # into the screen

#==============================================================================
# MATH & ALGEBRA
#==============================================================================

EYE_3X3 = ((1,0,0),(0,1,0),(0,0,1))

#==============================================================================
# PHYSICS
#==============================================================================

# "typical" constant of gravity acceleration
G_NORM = 9.81
G_VECTOR = mult_by_scalar3(DOWN_AXIS, G_NORM)

#==============================================================================
# COLORS
#==============================================================================

def convert_color(R_int, G_int, B_int):
	return mult_by_scalar3((R_int,G_int,B_int), 1.0 / 256)

# names according to W3C Recommendation - 4.4 Recognized color keyword names
# http://www.w3.org/TR/SVG/types.html#ColorKeywords

COLOR_BLACK = 		convert_color(0,0,0)
COLOR_BLUE = 		convert_color(0,0,255)
COLOR_BROWN = 		convert_color(165,42,42)
COLOR_CYAN = 		convert_color(0,255,255)
COLOR_GOLD =		convert_color(255,215,0)
COLOR_GRAY = 		convert_color(128,128,128)
COLOR_GREEN = 		convert_color(0,128,0)
COLOR_LIME = 		convert_color(0,255,0)
COLOR_LIME_GREEN = 	convert_color(50,205,50)
COLOR_MAROON = 		convert_color(128,0,0)
COLOR_MAGENTA = 	convert_color(255,0,255)
COLOR_NAVY = 		convert_color(0,0,128)
COLOR_OLIVE = 		convert_color(128,128,0)
COLOR_ORANGE = 		convert_color(255,165,0)
COLOR_PINK = 		convert_color(255,192,203)
COLOR_PURPLE = 		convert_color(128,0,128)
COLOR_RED = 		convert_color(255,0,0)
COLOR_SILVER = 		convert_color(192,192,192)
COLOR_SNOW = 		convert_color(255,250,250)
COLOR_VIOLET = 		convert_color(238,130,238)
COLOR_YELLOW = 		convert_color(255,255,0)
COLOR_WHITE = 		convert_color(255,255,255)
