"""Backend that outputs to SVG tags.

SVG is generated using the 'xml.etree' ElementTree std. lib module. A write
parameter has been added to all geometry creation methods, and all methods
return any ELementTree.Elements created. 

.. Note::
    If the svg.CommandFile isn't used as a context manager you will have to
    provide a root ElementTree.Element using CommandFile.set_root method.
    Also you will need to call CommandFile.teardown manually to add the style
    block to the root, and write the tree to the provided file object.

.. Warning::
    The point, points, and reset methods have no meaningful representation in
    SVG. Any script using these methods cannot be run against the SVG backend.

There are several special module attributes:
    
:attr WIDTH: SVG doc width.
:attr HEIGHT: SVG doc height.
:attr FACTOR: The initial scale factor of the drawing.
:attr NAVIGATE: Toggles inclusion of 
                `SVGPan.js <https://code.google.com/p/svgpan/>`_ in teardown.

WIDTH and HEIGHT are written in the <svg> tag as their respective attributes.
The viewbox is set to '0 0 WIDTH HEIGHT' to match display and drawing units.

To better match other CAD packages a group is added inside the SVG tag wrapping
all other elements that mirrors everything across the y-axis so positive y is
up, and everything is translated down by HEIGHT so that the origin is in the
bottom left corner. This is also where initial scale FACTOR is applied.
"""
import os
from xml.etree import ElementTree as ET
from contextlib import contextmanager
import commandfile

EXT = '.svg'
WIDTH = '800px'
HEIGHT = '600px'
FACTOR = 12
NAVIGATE = True
mininav = os.path.abspath(os.path.join(os.path.dirname(__file__), 'SVGPan.js'))
with open(mininav, 'r') as infile:
    mininav = infile.read()

# Patch ElementTree for CDATA support
orig_serialize_xml = ET._serialize_xml
def _serialize_xml(write, elem, encoding, qnames, namespaces):
    """Replace ET serializer with one that handles CDATA blocks.
    
    Lifted from `this answer <http://stackoverflow.com/a/10440166/770443>`_.
    """
    if elem.tag == 'CDATA':
        write("\n<![CDATA[%s]]>\n" %elem.text)
    else:
        orig_serialize_xml(write, elem, encoding, qnames, namespaces)

ET._serialize_xml = _serialize_xml

class Layer(commandfile.Layer):
    """Group objects with identical styles.

    .. Note::
        All layers have a fill style of none.

    :param name: This is the class name for the layer style.
        A tuple of layer properties, or a Layer object may be passed as the 
        first argument (name) in which case the new layer is initialized with 
        provided values.
    :type name: string OR Layer-like
    :param co: The color of the layer [default: black].
    :param lw: The line-weight of the layer [default: 0.1].
    :param lc: The line-class (type) of the layer. The line-class can be None
               for continuous lines, one of the names in the Layer.linecls
               class attribute, or an iterable of ints.
    """
    #: Named line classes
    linecls = { # TODO add indexed (MicroStation like) version 
        'continuous':(0,),
        'hidden':(0.25, 0.2),
        'center':(1, 0.2, 0.2, 0.2),
        'phantom':(0.75, 0.2, 0.2, 0.2, 0.2, 0.2),
    }

    #: Indexed colors
    colors = dict((i+1, co) for i, co in enumerate((
        'red', 
        'yellow', 
        'green', 
        'cyan', 
        'blue', 
        'magenta', 
        'black', 
        'gray', 
        'lightgray', 
    )))

    def __str__(self):
        """Render this layer as a CSS style."""
        style = dict()
        style['name'] = self.name
        # Check for indexed colors
        if type(self.co) == int:
            style['co'] = self.colors[self.co]
        else:
            style['co'] = self.co if self.co else 'black'
        style['lw'] = self.lw if self.lw else 0.1
        lc = self.lc
        if not lc:
            lc = self.linecls['continuous']
        elif lc in self.linecls:
            lc = self.linecls[self.lc]
        style['lc'] = "{}".format(",".join(str(i) for i in lc))

        le = '\n\t\t'
        template = '\t.{name} {{' + le + 'stroke: {co};' + le
        template += 'stroke-width: {lw};' + le + 'stroke-dasharray: {lc};'
        template += '\n\t}}\n'

        return template.format(**style)

class CommandFile(commandfile.CommandFile):
    """Wrapper for SVG generation.

    Convenience methods for building an SVG tree and writing it to a filelike.

    :param filelike: An object with a write method.
    :type filelike: filelike
    :param setup: Commands to include at the beginning of the script.
    :type setup: callable OR valid CommandFile.cmd argument
    :param teardown: Commands to include at the end of the script.
    :type teardown: callable OR valid CommandFile.cmd argument
    """
    Layer = Layer #: A local binding to the SVG Layer class

    def __init__(self, filelike, setup=None, teardown=None):
        commandfile.CommandFile.__init__(self, filelike, setup, teardown)
        self._root = None
        self._container = None
        self._layers = dict()
    
    def set_root(self, el, transform=False):
        """Sets the ElementTree Element to which tags will be added.

        Also adds a wrapper group that modifies the SVG coordinate system.

        :param el: The element to set as root.
        :type el: ElementTree.Element
        :raises: TypeError if el doesn't pass ElementTree.iselement test.
        """
        if ET.iselement(el):
            self._root = el
            if transform:
                # Add coordinate system modifying group
                tfrm = "translate(0,{0}) scale({1},-{1})"
                tfrm = tfrm.format(HEIGHT[:-2], FACTOR)
                self._container = ET.Element('g', id="viewport", transform=tfrm)
                self._root.append(self._container)
            else:
                # Set root as container
                self._container = self._root
        else:
            raise TypeError("Expected Element, got {}".format(type(el)))

    def setup(self):
        """Add default configuration info and run user provided setup func.
        
        Called automatically by CommandFile context manager. Writes default
        setup code, then adds any user provided setup. If the user setup is
        callable the return value is written to the script, otherwise the user
        setup is written as a string.
        
        .. Note::
            User setup is handled differently in SVG, if the user setup is not
            a function it is passed to the cmd method to be added as a tag.
        """
        svg = ET.Element('svg', width=WIDTH, height=HEIGHT, id="svgroot",
                viewbox="0 0 {} {}".format(WIDTH[:-2], HEIGHT[:-2]))
        self.set_root(svg, transform=True)
        # Run user setup
        if self.user_setup:
            try:
                # Assume user_setup is callable
                self.user_setup(self)
            except TypeError:
                # Fall back to treating it as a command
                self.cmd(self.user_setup)

    def teardown(self):
        """Add final tags, run user provided teardown func, and write filelike.
        
        Called automatically by CommandFile context manager. Writes any user
        provided teardown, then writes default teardown code. If the user
        teardown is callable the return value is written to the script,
        otherwise the user teardown is written as a string.

        .. Note::
            User teardown is handled differently in SVG, if the user teardown is
            not a function it is passed to the cmd method to be added as a tag.
        """
        # Run user teardown
        if self.user_teardown:
            try:
                # Assume user_teardown is callable
                self.user_teardown(self)
            except TypeError:
                # Fall back to treating it as a command
                self.cmd(self.user_teardown)
        # Write style tag implementing layers used.
        self._add_style()
        if NAVIGATE:
            self._add_nav()
        # Write output to file
        self.file.write(ET.tostring(self._root))

    def _add_style(self):
        """Write an inline style sheet for default and layer properties."""
        style = ET.Element('style')
        data = ET.SubElement(style, 'CDATA')
        # Add default styles
        data.text = """
        line, polyline, circle {
            stroke: black;
            fill: none;
            stroke-width: 0.1px;
        }"""
        data.text += '\n'
        # Add a style for each layer
        try:
            for layer in self._layers.values():
                data.text += str(layer)
        except AttributeError:
            pass
        self._container.append(style)

    def _add_nav(self):
        """Adds mouse navigation."""
        script = ET.Element('script', type="text/javascript")
        data = ET.SubElement(script, 'CDATA')
        data.text = mininav
        self._container.append(script)
     
    def set_layer(self, layer, *args, **kwargs):
        r"""Activates the provided layer object or description.
        
        :param layer: A layer object, or a valid Layer name argument.
        :param \*args: Valid Layer arguments.
        :param \*\*kwargs: Valid Layer arguments.
        """
        if self._layer:
            self.layer_stack.append(self._layer)
        # Force creation of new layer
        self._layer = self.Layer(layer, *args, **kwargs)
        # Save every layer in a map of name:layer
        self._layers[self._layer.name] = self._layer
 
    def pop_layer(self):
        """Restores active layer prior to last set_layer call."""
        if self.layer_stack:
            self._layer = self.layer_stack.pop()

    def cmd(self, command, *args, **kwargs):
        r"""Add arbitrary elements to script root.
        
        The command argument is expected to be a tag name, or an
        ElementTree.Element, or an iterable of ElementTree Elements. If command
        is a string then \*args and \*\*kwargs are passed to the Element init. 
        if command is already an element then the extra args are ignored.

        :param command: The element(s) to be added to the document.
        :type command: string OR ElementTree.Element OR Element iterable
        :param \*args: The attrib argument of ElementTree.Element.
        :type \*args: dict
        :param \*\*kwargs: Extra attributes for the new ElementTree.Element.
        :param write: Whether the element should be added to root (default=True).
        :type write: boolean
        :returns: Element
        """
        write = kwargs.pop('write', True)
        if hasattr(command, '__iter__'): # Is iterable
            # Handle lists of elements to add
            for el in command:
                self.cmd(el, write=write)
            return command
        elif ET.iselement(command):
            # Handle single element
            el = command
        else:
            # Handle string
            el = ET.Element(command, *args, **kwargs)

        if self._layer:
            el.set('class', self._layer.name)
        if write:
            self._container.append(el)
        return el

    def line(self, ps, reset=False, mode=None, write=True):
        """Add a series of line segment tags to root.
        
        Since the SVG line tag only supports a single line segment multiple
        tags may be added to a single set of points.
        
        :param ps: The end points of the lines.
        :type command: iterable
        :param reset: Unused in SVG backend.
        :type reset: boolean
        :param mode: Unimplemented, relative coordinates could be implemented
                     for individual method invocations.
        :type mode: string
        :param write: Whether the line elements should be added to root.
        :type write: boolean
        :returns: Element list
        """
        # Process the points by connecting the last seen point to the current
        els = list()
        last = None
        for pt in ps:
            pt = [str(i) for i in pt]
            if not last:
                last = pt
                continue
            line = ET.Element('line', x1=last[0], y1=last[1], 
                                              x2=pt[0], y2=pt[1])
            if self._layer:
                line.set('class', self._layer.name)
            els.append(line)
            last = pt
        if write:
            self._container.extend(els)
        return els

    def polyline(self, ps, close=True, reset=False, mode=None, write=True):
        """Add a polyline tag to root.

        Points are written as "x,y" pairs seperated by spaces, so splitting
        produces point strings, and splitting those strings on ',' produces the
        point components.
        
        :param ps: The ordered points forming the line.
        :type command: iterable
        :param close: Flag indicating whether the line should end where it started.
        :type close: boolean
        :param reset: Unused in SVG backend.
        :type reset: boolean
        :param mode: Unimplemented, relative coordinates could be implemented
                     for individual method invocations.
        :type mode: string
        :param write: Whether the element should be added to root.
        :type write: boolean
        :returns: Element
        """
        if close:
            ps = list(ps)
            ps.append(ps[0])
        pnts = ''
        for pt in ps:
            pnts += '{},{} '.format(pt[0], pt[1])
        pline = ET.Element('polyline', points=pnts)
        if self._layer:
            pline.set('class', self._layer.name)
        if write:
            self._container.append(pline)
        return pline
             
    def circle(self, center, radius, write=True):
        """Add a circle tag to root.
        
        :param center: The center of the circle.
        :type center: iterable
        :param radius: The radius of the circle.
        :type radius: number
        :param write: Whether the element should be added to root.
        :type write: boolean
        :returns: Element
        """
        center = [str(i) for i in center]
        circle = ET.Element('circle', cx=center[0], cy=center[1], r=str(radius))
        if self._layer:
            circle.set('class', self._layer.name)
        if write:
            self._container.append(circle)
        return circle

    def text(self, text, p, height=1.0, ang=0, just='tl', write=True):
        """Add a text tag to root.
        
        The text is inspected for newline chars, and <tspan> tags are added
        with (hopefully) appropriate dx/dy values to create multiline text.

        :param text: The text to place.
        :type text: string
        :param p: The insertion point in a format passable to CommandFile.point.
        :type p: iterable
        :param height: How tall the text lines are.
        :type height: number
        :param ang: The angle of the text in degrees.
        :type ang: number
        :param just: The justification of the text, a pair of [t, m, b][l, c, r].
        :type just: string
        :param write: Whether the element should be added to root.
        :type write: boolean
        :returns: Element
        """
        p = [str(i) for i in p]
        if 'l' in just:
            just = 'start'
        elif 'c' in just:
            just = 'middle'
        else:
            just = 'end'
        tel = ET.Element('text', x=p[0], y=p[1], 
                transform="{} {},{}".format(ang, p[0], p[1]),
                style="text-size: {}; text-anchor: {};".format(height, just))
        if '\n' in text:
            lines = text.split('\n')
            last = None
            for line in lines:
                if not last:
                    last = line
                    tel.text = line
                    continue
                tspan = ET.Element('tspan', 
                        dx="-{}ex".format(len(last)), 
                        dy="1em")
                tspan.text = line
                tel.append(tspan)
        else:
            tel.text = text

        if self._layer:
            tel.set('class', self._layer.name)
        if write:
            self._container.append(tel)
        return tel
    
    def store(self, name, *els):
        r"""Store provided elements to be manipulated later.

        This method is provided as a uniform interface for grouping objects
        regardless of backend. In the SVG backend this is a noop.

        :param name: The id used to store the selection.
        :type name: Unused
        :param \*els: The elements to store.
        :type \*els: SVG elements or element lists.
        :raises: ValueError if no elements are provided.
        :returns: An element group passable to move/copy/rotate/scale methods.
        """
        if not els:
            raise ValueError('No elements provided to store!')
        group = list()
        for el in els:
            if isinstance(el, ET.Element):
                group.append(el)
            else:
                group.extend(el)
        return group

    def move(self, els, base=(0, 0), dest=(0, 0)):
        """Transform the provided elements from base to dest.

        :param els: The elements to move.
        :type els: iterable of Elements
        :param base: The base point to transform from.
        :type base: iterable
        :param dest: The dest point to transform to.
        :type dest: iterable
        :returns: Element list
        """
        if not hasattr(els, '__iter__'): # Is *not* iterable
            els = [els]
        vec = (dest[0] - base[0], dest[1] - base[1])
        trans = "translate({} {})".format(*vec)
        for el in els:
            if 'transform' in el.attrib:
                el.attrib['transform'] += ', ' + trans
            else:
                el.attrib['transform'] = trans
        return els

    def copy(self, els, base=(0, 0), dest=(0, 0), write=True):
        """Transform duplicates of the provided elements from base to dest.

        :param els: The elements to copy.
        :type els: iterable of Elements
        :param base: The base point to transform from.
        :type base: iterable
        :param dest: The dest point to transform to.
        :type dest: iterable
        :param write: Whether the elements should be added to root.
        :type write: boolean
        :returns: Element list
        """
        if not hasattr(els, '__iter__'): # Is *not* iterable
            els = [els]
        copies = [el.copy() for el in els]
        if write:
            self._container.extend(copies)
        return self.move(copies, base, dest)
    
    def rotate(self, els, base=(0, 0), ang=0):
        """Rotate the provided elements from base by angle.

        :param els: The elements to rotate.
        :type els: iterable of Elements
        :param base: The base point to transform from.
        :type base: iterable
        :param ang: The angle to rotate in degrees (counter-clockwise).
        :type ang: number
        :returns: Element list
        """
        if not hasattr(els, '__iter__'): # Is *not* iterable
            els = [els]
        trans = "rotate({} {},{})".format(ang, *base[:2])
        for el in els:
            if 'transform' in el.attrib:
                el.attrib['transform'] += ', ' + trans
            else:
                el.attrib['transform'] = trans
        return els

    def scale(self, els, base=(0, 0), scale=(1, 1)):
        """Scale the provided elements from base by scale.
        
        Remember that scaling an axis by -1 is equivalent to mirroring.

        :param els: The elements to scale.
        :type els: iterable of Elements
        :param base: The base point to transform from.
        :type base: iterable
        :param scale: The x and y scale factor to apply.
        :type scale: iterable
        :returns: Element list
        """
        if not hasattr(els, '__iter__'): # Is *not* iterable
            els = [els]
        trans = "translate({} {})".format(*base)
        trans += "scale({} {})".format(*scale)
        trans += "translate({} {})".format(-base[0], -base[1])
        for el in els:
            if 'transform' in el.attrib:
                el.attrib['transform'] += ', ' + trans
            else:
                el.attrib['transform'] = trans
        return els

    def erase(self, els):
        """Remove the indicated elements from root.

        :param els: The elements to remove.
        :type els: iterable of Elements
        :returns: Element list
        """
        if not hasattr(els, '__iter__'): # Is *not* iterable
            els = [els]
        for el in els:
            if el in self._container:
                self._container.remove(el)
        return els

if __name__ == "__main__": # pragma: no cover
    # When run as a script generate a square
    from cStringIO import StringIO
    from contextlib import closing

    with closing(StringIO()) as outfile:
        # Build custom layer
        mylayer = Layer('custom')
        # Create script file
        with CommandFile(outfile) as script:
            # Draw a shape
            with script.layer('first'):
                script.line(((1, 2), (2, 2)))
            with script.layer(mylayer):
                script.line(((2, 2), (2, 1)))
            with script.layer('third'):
                script.line(((2, 1), (1, 1)))
            with script.layer('fourth'):
                script.line(((1, 1), (1, 2)))
        print outfile.getvalue()
