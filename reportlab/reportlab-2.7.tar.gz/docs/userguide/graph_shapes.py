#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
__version__='''$Id$'''
from tools.docco.rl_doc_utils import *
from reportlab.graphics.shapes import *

heading2("Shapes")

disc("""
This section describes the concept of shapes and their importance
as building blocks for all output generated by the graphics library.
Some properties of existing shapes and their relationship to
diagrams are presented and the notion of having different renderers
for different output formats is briefly introduced.
""")

heading3("Available Shapes")

disc("""
Drawings are made up of Shapes.
Absolutely anything can be built up by combining the same set of
primitive shapes.
The module $shapes.py$ supplies a number of primitive shapes and
constructs which can be added to a drawing.
They are:
""")

bullet("Rect")
bullet("Circle")
bullet("Ellipse")
bullet("Wedge (a pie slice)")
bullet("Polygon")
bullet("Line")
bullet("PolyLine")
bullet("String")
bullet("Group")
bullet("Path (<i>not implemented yet, but will be added in the future</i>)")

disc("""
The following drawing, taken from our test suite, shows most of the
basic shapes (except for groups).
Those with a filled green surface are also called <i>solid shapes</i>
(these are $Rect$, $Circle$, $Ellipse$, $Wedge$ and $Polygon$).
""")

from reportlab.graphics import testshapes

t = testshapes.getDrawing06()
draw(t, "Basic shapes")


heading3("Shape Properties")

disc("""
Shapes have two kinds of properties - some to define their geometry
and some to define their style.
Let's create a red rectangle with 3-point thick green borders:
""")

eg("""
>>> from reportlab.graphics.shapes import Rect
>>> from reportlab.lib.colors import red, green
>>> r = Rect(5, 5, 200, 100)
>>> r.fillColor = red
>>> r.strokeColor = green
>>> r.strokeWidth = 3
>>>
""")

from reportlab.graphics.shapes import Rect
from reportlab.lib.colors import red, green
d = Drawing(220, 120)
r = Rect(5, 5, 200, 100)
r.fillColor = red
r.strokeColor = green
r.strokeWidth = 3
d.add(r)
draw(d, "red rectangle with green border")

disc("""
<i>Note: In future examples we will omit the import statements.</i>
""")

disc("""
All shapes have a number of properties which can be set.
At an interactive prompt, we can use their <i>dumpProperties()</i>
method to list these.
Here's what you can use to configure a Rect:
""")

eg("""
>>> r.dumpProperties()
fillColor = Color(1.00,0.00,0.00)
height = 100
rx = 0
ry = 0
strokeColor = Color(0.00,0.50,0.00)
strokeDashArray = None
strokeLineCap = 0
strokeLineJoin = 0
strokeMiterLimit = 0
strokeWidth = 3
width = 200
x = 5
y = 5
>>>
""")

disc("""
Shapes generally have <i>style properties</i> and <i>geometry
properties</i>.
$x$, $y$, $width$ and $height$ are part of the geometry and must
be provided when creating the rectangle, since it does not make
much sense without those properties.
The others are optional and come with sensible defaults.
""")

disc("""
You may set other properties on subsequent lines, or by passing them
as optional arguments to the constructor.
We could also have created our rectangle this way:
""")

eg("""
>>> r = Rect(5, 5, 200, 100,
             fillColor=red,
             strokeColor=green,
             strokeWidth=3)
""")

disc("""
Let's run through the style properties. $fillColor$ is obvious.
$stroke$ is publishing terminology for the edge of a shape;
the stroke has a color, width, possibly a dash pattern, and
some (rarely used) features for what happens when a line turns
a corner.
$rx$ and $ry$ are optional geometric properties and are used to
define the corner radius for a rounded rectangle.
""")

disc("All the other solid shapes share the same style properties.")


heading3("Lines")

disc("""
We provide single straight lines, PolyLines and curves.
Lines have all the $stroke*$ properties, but no $fillColor$.
Here are a few Line and PolyLine examples and the corresponding
graphics output:
""")

eg("""
    Line(50,50, 300,100,
         strokeColor=colors.blue, strokeWidth=5)
    Line(50,100, 300,50,
         strokeColor=colors.red,
         strokeWidth=10,
         strokeDashArray=[10, 20])
    PolyLine([120,110, 130,150, 140,110, 150,150, 160,110,
              170,150, 180,110, 190,150, 200,110],
             strokeWidth=2,
             strokeColor=colors.purple)
""")

d = Drawing(400, 200)
d.add(Line(50,50, 300,100,strokeColor=colors.blue, strokeWidth=5))
d.add(Line(50,100, 300,50,
           strokeColor=colors.red,
           strokeWidth=10,
           strokeDashArray=[10, 20]))
d.add(PolyLine([120,110, 130,150, 140,110, 150,150, 160,110,
          170,150, 180,110, 190,150, 200,110],
         strokeWidth=2,
         strokeColor=colors.purple))
draw(d, "Line and PolyLine examples")


heading3("Strings")

disc("""
The ReportLab Graphics package is not designed for fancy text
layout, but it can place strings at desired locations and with
left/right/center alignment.
Let's specify a $String$ object and look at its properties:
""")

eg("""
>>> s = String(10, 50, 'Hello World')
>>> s.dumpProperties()
fillColor = Color(0.00,0.00,0.00)
fontName = Times-Roman
fontSize = 10
text = Hello World
textAnchor = start
x = 10
y = 50
>>>
""")

disc("""
Strings have a textAnchor property, which may have one of the
values 'start', 'middle', 'end'.
If this is set to 'start', x and y relate to the start of the
string, and so on.
This provides an easy way to align text.
""")

disc("""
Strings use a common font standard: the Type 1 Postscript fonts
present in Acrobat Reader.
We can thus use the basic 14 fonts in ReportLab and get accurate
metrics for them.
We have recently also added support for extra Type 1 fonts
and the renderers all know how to render Type 1 fonts.
""")

##Until now we have worked with bitmap renderers which have to use
##TrueType fonts and which make some substitutions; this could lead
##to differences in text wrapping or even the number of labels on
##a chart between renderers.

disc("""
Here is a more fancy example using the code snippet below.
Please consult the ReportLab User Guide to see how non-standard
like 'DarkGardenMK' fonts are being registered!
""")

eg("""
    d = Drawing(400, 200)
    for size in range(12, 36, 4):
        d.add(String(10+size*2, 10+size*2, 'Hello World',
                     fontName='Times-Roman',
                     fontSize=size))

    d.add(String(130, 120, 'Hello World',
                 fontName='Courier',
                 fontSize=36))

    d.add(String(150, 160, 'Hello World',
                 fontName='DarkGardenMK',
                 fontSize=36))
""")

from reportlab.pdfbase import pdfmetrics
from reportlab import rl_config
rl_config.warnOnMissingFontGlyphs = 0
afmFile, pfbFile = getJustFontPaths()
T1face = pdfmetrics.EmbeddedType1Face(afmFile, pfbFile)
T1faceName = 'DarkGardenMK'
pdfmetrics.registerTypeFace(T1face)
T1font = pdfmetrics.Font(T1faceName, T1faceName, 'WinAnsiEncoding')
pdfmetrics.registerFont(T1font)

d = Drawing(400, 200)
for size in range(12, 36, 4):
    d.add(String(10+size*2, 10+size*2, 'Hello World',
                 fontName='Times-Roman',
                 fontSize=size))

d.add(String(130, 120, 'Hello World',
             fontName='Courier',
             fontSize=36))

d.add(String(150, 160, 'Hello World',
             fontName='DarkGardenMK',
             fontSize=36))

draw(d, 'fancy font example')


heading3("""Paths""")

disc("""
Postscript paths are a widely understood concept in graphics.
They are not implemented in $reportlab/graphics$ as yet, but they
will be, soon.
""")

# NB This commented out section is for 'future compatibility' - paths haven't
#    been implemented yet, but when they are we can uncomment this back in.

    ##disc("""Postscript paths are a widely understood concept in graphics. A Path
    ##       is a way of defining a region in space. You put an imaginary pen down,
    ##       draw straight and curved segments, and even pick the pen up and move
    ##       it. At the end of this you have described a region, which may consist
    ##       of several distinct close shapes or unclosed lines. At the end, this
    ##       'path' is 'stroked and filled' according to its properties. A Path has
    ##       the same style properties as a solid shape. It can be used to create
    ##       any irregular shape.""")
    ##
    ##disc("""In Postscript-based imaging models such as PDF, Postscript and SVG,
    ##       everything is done with paths. All the specific shapes covered above
    ##       are instances of paths; even text strings (which are shapes in which
    ##       each character is an outline to be filled). Here we begin creating a
    ##       path with a straight line and a bezier curve:""")
    ##
    ##eg("""
    ##>>> P = Path(0,0, strokeWidth=3, strokeColor=red)
    ##>>> P.lineTo(0, 50)
    ##>>> P.curveTo(10,50,80,80,100,30)
    ##>>>
    ##""")

    ##disc("""As well as being the only way to draw complex shapes, paths offer some
    ##       performance advantages in renderers which support them. If you want to
    ##       create a scatter plot with 5000 blue circles of different sizes, you
    ##       can create 5000 circles, or one path object. With the latter, you only
    ##       need to set the color and line width once. PINGO just remembers the
    ##       drawing sequence, and writes it out into the file. In renderers which
    ##       do not support paths, the renderer will still have to decompose it
    ##       into 5000 circles so you won't save anything.""")
    ##
    ##disc("""<b>Note that our current path implementation is an approximation; it
    ##         should be finished off accurately for PDF and PS.</b>""")


heading3("Groups")

disc("""
Finally, we have Group objects.
A group has a list of contents, which are other nodes.
It can also apply a transformation - its contents can be rotated,
scaled or shifted.
If you know the math, you can set the transform directly.
Otherwise it provides methods to rotate, scale and so on.
Here we make a group which is rotated and translated:
""")

eg("""
>>> g =Group(shape1, shape2, shape3)
>>> g.rotate(30)
>>> g.translate(50, 200)
""")

disc("""
Groups provide a tool for reuse.
You can make a bunch of shapes to represent some component - say,
a coordinate system - and put them in one group called "Axis".
You can then put that group into other groups, each with a different
translation and rotation, and you get a bunch of axis.
It is still the same group, being drawn in different places.
""")

disc("""Let's do this with some only slightly more code:""")

eg("""
    d = Drawing(400, 200)

    Axis = Group(
        Line(0,0,100,0),  # x axis
        Line(0,0,0,50),   # y axis
        Line(0,10,10,10), # ticks on y axis
        Line(0,20,10,20),
        Line(0,30,10,30),
        Line(0,40,10,40),
        Line(10,0,10,10), # ticks on x axis
        Line(20,0,20,10),
        Line(30,0,30,10),
        Line(40,0,40,10),
        Line(50,0,50,10),
        Line(60,0,60,10),
        Line(70,0,70,10),
        Line(80,0,80,10),
        Line(90,0,90,10),
        String(20, 35, 'Axes', fill=colors.black)
        )

    firstAxisGroup = Group(Axis)
    firstAxisGroup.translate(10,10)
    d.add(firstAxisGroup)

    secondAxisGroup = Group(Axis)
    secondAxisGroup.translate(150,10)
    secondAxisGroup.rotate(15)

    d.add(secondAxisGroup)

    thirdAxisGroup = Group(Axis,
                           transform=mmult(translate(300,10),
                                           rotate(30)))
    d.add(thirdAxisGroup)
""")

d = Drawing(400, 200)
Axis = Group(
    Line(0,0,100,0),  # x axis
    Line(0,0,0,50),   # y axis
    Line(0,10,10,10), # ticks on y axis
    Line(0,20,10,20),
    Line(0,30,10,30),
    Line(0,40,10,40),
    Line(10,0,10,10), # ticks on x axis
    Line(20,0,20,10),
    Line(30,0,30,10),
    Line(40,0,40,10),
    Line(50,0,50,10),
    Line(60,0,60,10),
    Line(70,0,70,10),
    Line(80,0,80,10),
    Line(90,0,90,10),
    String(20, 35, 'Axes', fill=colors.black)
    )
firstAxisGroup = Group(Axis)
firstAxisGroup.translate(10,10)
d.add(firstAxisGroup)
secondAxisGroup = Group(Axis)
secondAxisGroup.translate(150,10)
secondAxisGroup.rotate(15)
d.add(secondAxisGroup)
thirdAxisGroup = Group(Axis,
                       transform=mmult(translate(300,10),
                                       rotate(30)))
d.add(thirdAxisGroup)
draw(d, "Groups examples")
