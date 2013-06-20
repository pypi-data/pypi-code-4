"""Base classes for implementing drawing backend wrappers.

The base CommandFile class methods implement AutoCAD like outputs, and some are
used un-modified in the autocad.CommandFile implementation.
"""
from contextlib import contextmanager

class Layer(object):
    """Object representing a grouping and styling context.
    
    Layer like objects are expected to support at least
    naming, color, line weight, and line type.
    All properties except name are expected to be optional.

    >>> from pygencad.commandfile import Layer
    >>> l = Layer("test")
    >>> l
    <pygencad.commandfile.Layer object at 0x...>
    >>> print l # doctest: +NORMALIZE_WHITESPACE
    Layer:
        lv=test
        co=None
        lw=None
        lc=None

    :param name: The name visible in the backend after the script is run.
        A tuple of layer properties, or a Layer object may be passed as the 
        first argument (name) in which case the new layer is initialized with 
        provided values.
    :type name: string OR Layer-like
    :param co: The color of the layer.
    :param lw: The line-weight of the layer.
    :param lc: The line-class (type) of the layer.
    """
    def __init__(self, name, co=None, lw=None, lc=None):
        """Store properties and setup template."""
        # When passed a layer-like object return a new copy
        #if type(name) in (list, tuple): # Is iterable, but not string
        if hasattr(name, '__iter__'): # Is iterable
            self.name, self.co, self.lw, self.lc = name[:4]
        elif isinstance(name, Layer):
            # Assume we received another level object to copy
            self.name = name.name
            self.co = name.co
            self.lw = name.lw
            self.lc = name.lc
        else:
            self.name = name
            self.co = co
            self.lw = lw
            self.lc = lc
        # Command string conversion template
        self.template = 'Layer:\n\tlv={0.name}\n\tco={0.co}'
        self.template += '\n\tlw={0.lw}\n\tlc={0.lc}'

    def __str__(self):
        """Render this layer as a string.

        The __str__ method is used to output the commands necessary to set the
        Layer objects properties active in the script context.
        """
        return self.template.format(self)

class CommandFile(object):
    """Script generation interface.

    Provides convenience methods for issuing common commands, managing script
    context, and for issuing arbitrary commands.

    >>> from pygencad.commandfile import CommandFile
    >>> from StringIO import StringIO
    >>> f = StringIO()
    >>> with CommandFile(f) as script:
    ...     script.cmd("test")
    ... 
    'l'
    >>> print f.getvalue()
    test
    <BLANKLINE>

    :param filelike: An object with a write method.
    :type filelike: filelike
    :param setup: Commands to include at the beginning of the script.
    :type setup: string OR callable
    :param teardown: Commands to include at the end of the script.
    :type teardown: string OR callable
    """
    Layer = Layer #: A local binding to the backend specific Layer class
    def __init__(self, filelike, setup=None, teardown=None):
        self.file = filelike
        self._layer = None
        self.layer_stack = list()
        self.anno_layer = 'annotation'
        self.user_teardown = teardown
        self.user_setup = setup

    def setup(self):
        """Write default configuration info and run user provided setup func.
        
        Called automatically by CommandFile context manager. Writes default
        setup code, then adds any user provided setup. If the user setup is
        callable the return value is written to the script, otherwise the user
        setup is written as a string.
        """
        if self.user_setup:
            try:
                # Assume user_setup is callable
                self.user_setup(self)
            except TypeError:
                # Fall back to printing it as a string
                self.file.write(self.user_setup)

    def teardown(self):
        """Write cleanup commands and run user provided teardown func.
        
        Called automatically by CommandFile context manager. Writesany user
        provided teardown, then writes default teardown code. If the user
        teardown is callable the return value is written to the script,
        otherwise the user teardown is written as a string.
        """
        if self.user_teardown:
            try:
                # Assume user_teardown is callable
                self.user_teardown(self)
            except TypeError:
                # Fall back to printing it as a string
                self.file.write(self.user_teardown)

    def __enter__(self):
        """Setup script context."""
        self.setup()
        return self

    def __exit__(self, kind, value, traceback):
        """Cleanup script context."""
        self.teardown()

    @contextmanager
    def layer(self, layer, *args, **kwargs):
        r"""Script layer context manager.
        
        Activates the provided layer settings, and resets layer state on exit.

        >>> from pygencad.commandfile import CommandFile
        >>> from StringIO import StringIO
        >>> f = StringIO()
        >>> with CommandFile(f) as script:
        ...     with script.layer('layer'):
        ...         script.cmd("test")
        ... 
        'l'
        >>> print f.getvalue() # doctest: +NORMALIZE_WHITESPACE
        Layer:
            lv=layer
            co=None
            lw=None
            lc=None
        test
        <BLANKLINE>

        :param \*args: Valid Layer arguments.
        :param \*\*kwargs: Valid Layer arguments.
        """
        self.set_layer(layer, *args, **kwargs)
        yield
        self.pop_layer()
    
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
        self.file.write('{0}\n'.format(self._layer))

    def pop_layer(self):
        """Restores active layer prior to last set_layer call."""
        if self.layer_stack:
            self._layer = self.layer_stack.pop()
            self.file.write('{0}\n'.format(self._layer))

    def cmd(self, command, *args):
        r"""Write an arbitrary script command.

        If the command string contains format expressions, and additional
        arguments were passed, the command string will be formated using the
        additional arguments.

        >>> from pygencad.commandfile import CommandFile
        >>> from StringIO import StringIO
        >>> f = StringIO()
        >>> with CommandFile(f) as script:
        ...     script.cmd("command with data: {:0.5f}", 355/113.0)
        ... 
        'l'
        >>> print f.getvalue()
        command with data: 3.14159
        <BLANKLINE>
        
        :param command: The command to be written to the script.
        :type command: string
        :param \*args: Values to be formated by the command string.
        :returns: Some reference to any object created.
        """
        try:
            self.file.write(command.format(*args) + '\n')
        except (IndexError, KeyError):
            # String format failed with too few args, user used literal {}?
            self.file.write(command + '\n')
        return 'l'

    def point(self, p, reset=False, mode=None, write=True):
        """Convert an iterable into a point of the correct format.

        This method should be overridden in sub-classes.

        >>> from pygencad.commandfile import CommandFile
        >>> from StringIO import StringIO
        >>> f = StringIO()
        >>> point = (1, 2, 3)
        >>> with CommandFile(f) as script:
        ...     script.point(point)
        ...     script.point(point, reset=True)
        ...     script.point(point, mode='special')
        ...     p = script.point(point, write=False)
        ...     script.cmd("Here is the point: {}", p)
        ... 
        '1,2,3'
        '1,2,3\\n'
        '1,2,3'
        'l'
        >>> print f.getvalue()
        1,2,3
        1,2,3
        <BLANKLINE>
        1,2,3
        Here is the point: 1,2,3
        <BLANKLINE>
        
        :param p: The point to be converted.
        :type command: iterable
        :param reset: Optionally append the result of calling the reset method
            after writing the point.
        :type reset: boolean
        :param mode: Optional point output mode (unimplemented in base class).
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

        This method may need to be overridden in sub-classes.

        >>> from pygencad.commandfile import CommandFile
        >>> from StringIO import StringIO
        >>> f = StringIO()
        >>> with CommandFile(f) as script:
        ...     script.points((
        ...         (1, 2),
        ...         (3, 4),
        ...         (5, 6),
        ...     ))
        ... 
        >>> print f.getvalue()
        1,2
        3,4
        5,6
        <BLANKLINE>
        
        :param ps: The points to be converted.
        :type command: iterable
        :param reset: Optionally append the result of calling the reset method
            after writing all points.
        :type reset: boolean
        :param mode: Optional point output mode (unimplemented in base class).
        :type mode: string
        """
        for p in ps:
            self.point(p, mode=mode)
        if reset:
            self.reset()

    def reset(self, write=True):
        """Write the sequence required to exit the current command.
        
        This method may need to be overridden in sub-classes.
        
        :param write: Flag for writing output to script file.
        :type write: boolean
        :returns: The command that output by reset as a string.
        """
        cmd = "\n"
        if write:
            self.file.write(cmd)
        return cmd
    
    def line(self, ps, reset=False, mode=None):
        """Write a line segment command for each pair of points provided
        
        This method should be overridden in sub-classes.
        The output command for the line method is expected to produce a set of
        disconnected line segments. See the polyline command for outputting
        connected "line strings".
        
        :param ps: The end points of the lines.
        :type command: iterable
        :param reset: Optionally append the result of calling the reset method
            after writing all points.
        :type reset: boolean
        :param mode: Optional point output mode unimplemented in base class.
        :type mode: string
        :returns: Some reference to any object created.
        """
        self.cmd("line")
        self.points(ps, reset, mode)
        return 'l'

    def polyline(self, ps, close=True, reset=False, mode=None):
        """Write a string of lines connected at each of the provided points.
        
        This method should be overridden in sub-classes.
        The output command for the polyline method is expected to produce a
        single object connecting all the provided points in order. The object
        produced is expected to be "closable". Otherwise the method should
        ensure that the last point is equal to the first to close the polyline.
        
        :param ps: The ordered points forming the line.
        :type command: iterable
        :param close: Flag indicating whether the line should end where it started.
        :type close: boolean
        :param reset: Optionally append the result of calling the reset method
            after writing all points.
        :type reset: boolean
        :param mode: Optional point output mode unimplemented in base class.
        :type mode: string
        :returns: Some reference to any object created.
        """
        # This method is a placeholder and should be overridden in subclasses
        # Polylines are connected line strings, optionally closed
        if close:
            ps = list(ps)
            ps.append(ps[0])
        self.cmd("polyline")
        self.points(ps, reset, mode)
        return 'l'
             
    def circle(self, center, radius):
        """Write a circle command.
        
        This method should be overridden in sub-classes.

        :param center: Point in a format passable to CommandFile.point.
        :type center: iterable
        :param radius: Radius of the circle.
        :type radius: number
        :returns: Some reference to any object created.
        """
        self.cmd("circle {} {}", self.point(center, write=False), radius)
        return 'l'

    def text(self, text, p, height=1.0):
        """Write a text placement command.
        
        This method should be overridden in sub-classes.

        :param text: The text to place.
        :type text: string
        :param p: The insertion point in a format passable to CommandFile.point.
        :type p: iterable
        :param height: How tall the text lines are.
        :type height: number
        :returns: Some reference to any object created.
        """
        self.cmd("text {} {} h={}", self.point(p, write=False), text, height)
        return 'l'

    def store(self, name, *els):
        r"""Store provided elements to be manipulated later.

        This method should be overridden in sub-classes.

        This method provides a uniform interface for grouping objects
        regardless of backend. This is required for the move/copy/rotate/scale
        methods to be of any practical use. Each backend's store method should
        transparently handle combining elements and groups.

        :param name: The id used to store the selection.
        :type name: backend specific
        :param \*els: The elements to store.
        :type \*els: backend specific
        :raises: ValueError if no elements are provided.
        :returns: An element group passable to move/copy/rotate/scale methods.
        """
        if not els:
            raise ValueError('No elements provided to store!')
        self.file.write('{}({})\n'.format(name, ','.join(els)))
        return name

    def move(self, els, base=(0, 0), dest=(0, 0)):
        """Transform the provided elements from base to dest.

        :param els: The elements to move.
        :type els: backend specific
        :param base: The base point to transform from.
        :type base: iterable
        :param dest: The dest point to transform to.
        :type dest: iterable
        :returns: Some reference to modified objects.
        """
        self.file.write('move {} {} {}\n'.format(str(els), base, dest))
        return els

    def copy(self, els, base=(0, 0), dest=(0, 0)):
        """Transform duplicates of the provided elements from base to dest.

        :param els: The elements to copy.
        :type els: backend specific
        :param base: The base point to transform from.
        :type base: iterable
        :param dest: The dest point to transform to.
        :type dest: iterable
        :returns: Some reference to duplicated objects.
        """
        self.file.write('copy {} {} {}\n'.format(str(els), base, dest))
        return els

    def rotate(self, els, base=(0, 0), ang=0):
        """Rotate the provided elements from base by angle.

        :param els: The elements to rotate.
        :type els: backend specific
        :param base: The base point to transform from.
        :type base: iterable
        :param ang: The angle to rotate in degrees (counter-clockwise).
        :type ang: number
        :returns: Some reference to modified objects.
        """
        self.file.write('rotate {} {} {}\n'.format(els, base, ang))
        return els

    def scale(self, els, base=(0, 0), scale=1):
        """Scale the provided elements from base by scale.
        
        Remember that scaling an axis by -1 is equivalent to mirroring.

        :param els: The elements to scale.
        :type els: backend specific
        :param base: The base point to transform from.
        :type base: iterable
        :param scale: The scale factor to apply.
        :type scale: number
        :returns: Some reference to modified objects.
        """
        self.file.write('scale {} {} {}\n'.format(els, base, scale))
        return els
    
    def erase(self, els):
        """Remove the indicated elements.

        :param els: The elements to remove.
        :type els: backend specific
        """
        self.file.write('erase {}\n'.format(els))

if __name__ == "__main__": # pragma: no cover
    # When run as a script generate a square
    from cStringIO import StringIO
    from contextlib import closing

    with closing(StringIO()) as outfile:
        # Build custom layer
        mylayer = Layer('custom')
        # Create script file
        with CommandFile(outfile, "Initialize\n", "Finalize\n") as script:
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
