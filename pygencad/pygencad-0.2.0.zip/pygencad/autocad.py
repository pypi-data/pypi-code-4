"""Wrapper for AutoCAD command script generation."""
from contextlib import contextmanager
import commandfile

EXT = '.scr'

class Layer(commandfile.Layer):
    """AutoCAD layer wrapper.
    
    In addition to color, line-weight, and line-type you can also set
    plot-style, non-plot, and description. The co, lw, and lc values default to
    "bylevel" which means that the attribute is not output in the script.

    :param name: The name visible in Acad after the script is run.
        A tuple of layer properties, or a Layer object may be passed as the 
        first argument (name) in which case the new layer is initialized with 
        provided values.
    :type name: string OR Layer-like
    :param co: The color of the layer.
    :type co: int
    :param lw: The line-weight of the layer.
    :type lw: number
    :param lc: The line-class (type) of the layer.
    :type lc: string
    :param desc: The layer description.
    :type desc: string
    :param st: The layer style.
    :type st: string
    :param plt: Whether the layer is can be plotted.
    :type plt: boolean
    """
    ctemplate = 'c {0.co}\n '
    wtemplate = 'lw {0.lw}\n '
    ltemplate = 'l {0.lc}\n '
    ptemplate = 'p {0.plt}\n '
    stemplate = 'ps {0.st}\n '
    dtemplate = 'd {0.desc}\n{0.name}\n'

    def __init__(self, name, co=None, lw=None, lc=None,
                 desc='', st='', plt=True):
        if not co:
            co = 'bylevel'
        if not lw:
            lw = 'bylevel'
        if not lc:
            lc = 'bylevel'
        # Using oldstyle super call
        commandfile.Layer.__init__(self, name, co, lw, lc)
        if hasattr(name, '__iter__'): # Is iterable
            self.desc, self.st, self.plt = name[1:4]
        elif type(name) not in (str, buffer, unicode):
            # Assume we received another layer object to copy
            self.desc = name.desc
            self.st = name.st
            self.plt = name.plt
        else:
            self.desc = desc
            self.st = st
            self.plt = 'plot' if plt else 'no'
        # Command string conversion template
        self.template = '-layer make {0.name}\n'

    def __str__(self):
        """Render this layer as a string.

        The __str__ method is used to output the commands necessary to set the
        Layer objects properties active in AutoCAD.
        """
        s = self.template
        if self.co != 'bylevel':
            s += self.ctemplate
        if self.lw != 'bylevel':
            s += self.wtemplate
        if self.lc != 'bylevel':
            s += self.ltemplate
        if self.desc:
            s += self.dtemplate
        if self.st:
            s += self.stemplate
        s += self.ptemplate
        return s.format(self)

class CommandFile(commandfile.CommandFile):
    """Wrapper for AutoCAD script generation.

    In addition to implementing the methods defined in the base class this
    class provides a UCS context manager, 3d polyline method, and block method.

    :param filelike: An object with a write method.
    :type filelike: filelike
    :param setup: Commands to include at the beginning of the script.
    :type setup: string OR callable
    :param teardown: Commands to include at the end of the script.
    :type teardown: string OR callable
    """
    Layer = Layer #: Local binding to the Acad Layer class
    def __init__(self, filelike, setup=None, teardown=None):
        commandfile.CommandFile.__init__(self, filelike, setup, teardown)

    def setup(self):
        """Write default configuration info and run user provided setup func.
        
        The default setup stores the active osnaps in a variable named
        "osmodeinit" and turns off osnaps (which normally interfere with
        scripts). The initial value of cmdecho is recorded as "cmdechoinit" and
        cmdecho is also disabled.
        """
        # Write AutoCAD specific setup
        #TODO load commands directly from file?
        self.cmd('!(setq osmodeinit (getvar "OSMODE"))')
        self.cmd("osmode 0")
        self.cmd('!(setq cmdechoinit (getvar "CMDECHO"))')
        self.cmd('!(setvar "CMDECHO" 0)')
        # Add ssjoin lisp
        self.cmd('''!(defun ssjoin ( ss1 ss2 / count )
                        (setq count 0)
                        (repeat (sslength ss2)
                            (ssadd (ssname ss2 count) ss1)
                            (setq count (1+ count))
                        ))''')
        # Run base class setup
        commandfile.CommandFile.setup(self)

    def teardown(self):
        """Write cleanup commands and run user provided teardown func.
        
        The initial values recorded in the setup method are restored.
        """
        # Write AutoCAD specific teardown
        #TODO load commands directly from file?
        self.cmd("osmode !osmodeinit")
        self.cmd('!(setvar "CMDECHO" cmdechoinit)')
        # Run base class cleanup
        commandfile.CommandFile.teardown(self)

    @contextmanager
    def ucs(self, command, points=None, count=1):
        """User Coordinate System context manager.
        
        Write a set of UCS commands and rollback changes when done.

        >>> from pygencad.autocad import CommandFile
        >>> from StringIO import StringIO
        >>> f = StringIO()
        >>> script = CommandFile(f)
        >>> with script.ucs('ucs w\\nucs zaxis', ((0,0,0), (1,1,1)), 2):
        ...     # Draw a circle at origin pointing to the positive quadrant
        ...     script.circle((0,0,0), 5)
        ... 
        'l'
        >>> print f.getvalue()
        ucs w
        ucs zaxis
        0,0,0
        1,1,1
        circle 0,0,0 5
        ucs p
        ucs p
        <BLANKLINE>

        :param command: UCS commands to execute on entry.
        :type command: string
        :param points: A list of points required by the *last* UCS command.
        :type points: iterable
        :param count: How many UCS commands were issued.
        :type count: number
        """
        self.set_ucs(command, points)
        yield
        self.pop_ucs(count)

    def set_ucs(self, command, points=None):
        """Change the active UCS.
        
        :param command: UCS commands to execute on entry.
        :type command: string
        :param points: A list of points required by the *last* UCS command.
        :type points: iterable
        """
        self.cmd(command)
        if points:
            self.points(points)

    def pop_ucs(self, count=1):
        """Rollback the indicated number of UCS changes.
        
        :param count: How many UCS commands need to be rolled back.
        :type count: number
        """
        self.file.write("ucs p\n" * count)
                 
    def point(self, p, reset=False, mode=None, write=True):
        """Convert an iterable into a point of the correct format.

        The mode argument is currently unsupported, but should support
        relative, polar, and relative polar coordinate input.

        :param p: The point to be converted.
        :type command: iterable
        :param reset: Optionally append the result of calling the reset method
            after writing the point.
        :type reset: boolean
        :param mode: Optional point output mode.
        :type mode: string
        :param write: Flag for writing output to script file.
        :type write: boolean
        :returns: The point converted to a string.
        """
        coord = "{0}".format(",".join(str(i) for i in p))
        if reset:
            coord += self.reset(write=False)
        if write:
            self.file.write(coord + '\n')
        return coord

    def points(self, ps, reset=False, mode=None):
        """Calls CommandFile.point on each member of an iterable.

        The mode Argument is currently unsupported, but should support
        relative, polar, and relative polar coordinate input.

        :param ps: The points to be converted.
        :type command: iterable
        :param reset: Optionally append the result of calling the reset method
            after writing all points.
        :type reset: boolean
        :param mode: Optional point output mode.
        :type mode: string
        """
        for p in ps:
            self.point(p, mode)
        if reset:
            self.reset()

    def reset(self, write=True):
        """Write the sequence required to exit the current command.

        For Acad this method currently just outputs a newline.
        
        :param write: Flag for writing output to script file.
        :type write: boolean
        :returns: The command that output by reset as a string.
        """
        cmd = "\n"
        if write:
            self.file.write(cmd)
        return cmd

    def line(self, ps, reset=False, mode=None):
        """Write the Acad line command.

        The mode argument is currently unsupported.
        
        :param ps: The end points of the lines.
        :type command: iterable
        :param reset: Optionally append the result of calling the reset method
            after writing all points.
        :type reset: boolean
        :param mode: Optional point output mode.
        :type mode: string
        :returns: Reference to created object.
        """
        self.cmd("line")
        self.points(ps, reset, mode)
        return 'l'

    def polyline(self, ps, close=True, reset=False, mode=None):
        """Write the Acad pline command.

        Support could be added in the future for drawing arc segments or other
        special pline settings.

        The mode argument is currently unsupported.
        
        :param ps: The ordered points forming the line.
        :type command: iterable
        :param close: Flag indicating whether the line should end where it started.
        :type close: boolean
        :param reset: Optionally append the result of calling the reset method
            after writing all points.
        :type reset: boolean
        :param mode: Optional point output mode.
        :type mode: string
        :returns: Reference to created object.
        """
        self.cmd("pline")
        self.points(ps, mode=mode)
        if close:
            self.cmd("c")
        if reset:
            self.reset()
        return 'l'

    def poly3d(self, ps, close=True, reset=False, mode=None):
        """Write the Acad 3dpolyline command.

        In Acad polylines are strictly 2d in the xy plane of the active UCS. To
        draw non-planer polylines you must use the 3dpolyline. While 2d plines
        support all properties, arc segments, and even splines, 3dpolylines are
        always straight segments, and don't support line-types (as of Acad2012).

        The mode argument is currently unsupported.

        :param ps: The ordered points forming the line.
        :type command: iterable
        :param close: Flag indicating whether the line should end where it started.
        :type close: boolean
        :param reset: Optionally append the result of calling the reset method
            after writing all points.
        :type reset: boolean
        :param mode: Optional point output mode.
        :type mode: string
        :returns: Reference to created object.
        """
        self.cmd("3dpoly")
        self.points(ps, mode=mode)
        if close:
            self.cmd("c")
        if reset:
            self.reset()
        return 'l'

    def circle(self, center, radius):
        """Write the Acad circle command.
        
        :param center: Point in a format passable to CommandFile.point.
        :type center: iterable
        :param radius: Radius of the circle.
        :type radius: number
        :returns: Reference to created object.
        """
        self.cmd("circle {} {}", self.point(center, write=False), radius)
        return 'l'
             
    def text(self, text, p, height=1.0, ang=0, just='tl'):
        """Write a text placement command.
        
        Text is placed as mtext. The text object width is set to 0 (infinite)
        meaning the text does not automatically wrap. Support for setting
        width, and setting the active text style, could be added in the future.

        :param text: The text to place.
        :type text: string
        :param p: The insertion point in a format passable to CommandFile.point.
        :type p: iterable
        :param height: How tall the text lines are.
        :type height: number
        :param ang: The angle of the text in degrees.
        :type ang: number
        :param just: The justification of the text, a pair of [t, c, b][l, c, r].
        :type just: string
        :returns: Reference to created object.
        """
        self.file.write('-mtext\n')
        self.point(p)
        self.file.write('h {0}\n'.format(height))
        self.file.write('j {0}\n'.format(just))
        self.file.write('r {0:0.0{1}f}\n'.format(ang, 4))
        self.file.write('w 0\n') # set mtext width to zero (infinite)
        self.file.write(text)
        self.file.write('\n\n') # Final returns to exit command
        return 'l'

    def block(self, name, loc, ang=0, scale=1, attrs=None):
        """Write a block placement command.

        Currently only basic insertion is supported. Setting non-uniform scale
        factors, setting text values for attribute driven blocks, and setting
        dynamic block attributes could be added in the future.
        
        The attrs argument is currently unsupported.

        :param name: The name of the block in Acad that is to be inserted.
        :type name: string
        :param loc: The block insertion point.
        :type loc: iterable
        :param ang: The rotation angle of the inserted block in degrees.
        :type ang: number
        :param scale: The uniform scale factor of the inserted block.
        :type scale: number
        :param attrs: Attributes to be set for the block after insertion.
        :type attrs: mapping
        :returns: Reference to created object.
        """
        # FIXME check commands
        # FIXME refactor "loc" argument to match other methods
        self.file.write('insert {0}\n'.format(name))
        self.file.write('a {0:0.0{1}f}\n'.format(ang, 8))
        self.file.write('s {0:0.0{1}f}\n'.format(scale, 8))
        self.point(loc)
        return 'l'

    def store(self, name, *els):
        r"""Store provided elements to be manipulated later.

        For AutoCAD named selection sets are created (AutoCAD has a hard limit
        of 128 named selection sets). The selection set name will have a '!'
        prepended, and can be passed to any command expecting a selection. If
        els contains 'l' than only one item (the last drawn) is added to the
        stored selection. Alternately, if els contains only selections set
        names, a new joined selection is created.

        :param name: The id used to store the selection.
        :type name: string
        :param \*els: The elements to store.
        :type \*els: 'l' for last, or selection set names.
        :raises: ValueError if no elements are provided.
        :returns: The name of the selection set.
        """
        if '!' not in name:
            ssname = name
            name = '!' + name
        else:
            ssname = name.strip('!')
        # Handle empty els
        if not els:
            raise ValueError("No elements provided to store!")
        # Create the named selection set if it doesn't exist
        self.cmd("!(if (= {0} nil) (setq {0} (ssadd)))".format(ssname))
        # There are two options for building sets
        if 'l' in els:
            # if 'l' (last) is in the els then only one element can be added
            self.cmd("!(ssadd (entlast) {})".format(ssname))
        else:
            # Otherwise els should be a list of sset names
            for el in els:
                self.cmd('!(ssjoin {} {})'.format(ssname, el.strip('!')))
        return name

    def move(self, els, base=(0, 0), dest=(0, 0)):
        """Transform the provided elements from base to dest.

        :param els: The elements to move.
        :type els: A valid AutoCAD selection string.
        :param base: The base point to transform from.
        :type base: iterable
        :param dest: The dest point to transform to.
        :type dest: iterable
        :returns: Reference to modified objects.
        """
        self.file.write('move {} \n'.format(els))
        self.point(base)
        self.point(dest)
        return els

    def copy(self, els, base=(0, 0), dest=(0, 0)):
        """Transform duplicates of the provided elements from base to dest.

        :param els: The elements to copy.
        :type els: A valid AutoCAD selection string.
        :param base: The base point to transform from.
        :type base: iterable
        :param dest: The dest point to transform to.
        :type dest: iterable
        :returns: Reference to modified objects.
        """
        # TODO copy should return a selection set containing the *new* elements
        self.file.write('copy {} \n'.format(els))
        self.point(base)
        self.point(dest)
        return els

    def rotate(self, els, base=(0, 0), ang=0):
        """Rotate the provided elements from base by angle.

        :param els: The elements to rotate.
        :type els: A valid AutoCAD selection string.
        :param base: The base point to transform from.
        :type base: iterable
        :param ang: The angle to rotate in degrees (counter-clockwise).
        :type ang: number
        :returns: Reference to modified objects.
        """
        self.file.write('rotate {} \n'.format(els))
        self.point(base)
        self.file.write('{}\n'.format(ang))
        return els

    def scale(self, els, base=(0, 0), scale=1):
        """Scale the provided elements from base by scale.
        
        Remember that scaling an axis by -1 is equivalent to mirroring.

        :param els: The elements to scale.
        :type els: A valid AutoCAD selection string.
        :param base: The base point to transform from.
        :type base: iterable
        :param scale: The scale factor to apply.
        :type scale: number
        :returns: Reference to modified objects.
        """
        self.file.write('scale {} \n'.format(els))
        self.point(base)
        self.file.write('{}\n'.format(scale))
        return els
    
    def erase(self, els):
        """Remove the indicated elements.

        :param els: The elements to remove.
        :type els: A valid AutoCAD selection string.
        """
        self.file.write('erase {} \n'.format(els))

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
                script.cmd('line')
                script.point((1, 2))
                script.point((2, 2))
                script.reset()
            with script.layer(mylayer):
                script.cmd('line')
                script.point((2, 2))
                script.point((2, 1))
                script.reset()
            with script.layer('third'):
                script.cmd('line')
                script.points((
                    (2, 1),
                    (1, 1)
                ))
                script.reset()
            with script.layer('fourth'):
                script.cmd('line')
                script.point((1, 1))
                script.point((1, 2))
                script.reset()
        print outfile.getvalue()
