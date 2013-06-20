"""Wrapper for MicroStation command script generation."""
import commandfile

EXT = '.txt'
DEFAULT_MODE = 'xy'

class Layer(commandfile.Layer):
    """MicroStation level wrapper.
    
    Sets the bylevel color, line-weight, and line-type to the values provided
    by the co, lw, and lc. The values default to "bylevel" which uses
    ustation's default/current settings.

    :param name: The name visible in ustation after the script is run.
        A tuple of level properties, or a Layer object may be passed as the 
        first argument (name) in which case the new level is initialized with 
        provided values.
    :type name: string OR Layer-like
    :param co: The color of the level.
    :type co: int
    :param lw: The line-weight of the level.
    :type lw: number
    :param lc: The line-class (type) of the level.
    :type lc: number
    """
    def __init__(self, name, co=None, lw=None, lc=None):
        if not co:
            co = 'bylevel'
        if not lw:
            lw = 'bylevel'
        if not lc:
            lc = 'bylevel'
        # Using oldstyle super call
        commandfile.Layer.__init__(self, name, co, lw, lc)
        # Command string conversion template
        #self.template = 'lv={0.name};co={0.co};lw={0.lw};lc={0.lc}'
        self.template = 'level create {0.name}\n'
        self.template += 'lv={0.name};co=bylevel;lw=bylevel;lc=bylevel\n'
        self.template += 'level set bylevel color {0.co} {0.name}\n'
        self.template += 'level set bylevel weight {0.lw} {0.name}\n'
        self.template += 'level set bylevel style {0.lc} {0.name}\n'
        #TODO add other properties like non-plot, transparent, etc.

class CommandFile(commandfile.CommandFile):
    """Wrapper for MicroStation script generation.

    The ustation wrapper should have additional methods for setting ACS and
    placing cells, mirroring the autocad module's methods.

    :param filelike: An object with a write method.
    :type filelike: filelike
    :param setup: Commands to include at the beginning of the script.
    :type setup: string OR callable
    :param teardown: Commands to include at the end of the script.
    :type teardown: string OR callable
    """
    Layer = Layer #: A local binding to the layer class
    def __init__(self, filelike, setup=None, teardown=None):
        commandfile.CommandFile.__init__(self, filelike, setup, teardown)

    def setup(self):
        """Write default configuration info and run user provided setup func."""
        # Write MicroStation specific setup
        #TODO load commands directly from file?
        # Run base class setup
        commandfile.CommandFile.setup(self)

    def teardown(self):
        """Write cleanup commands and run user provided teardown func."""
        # Write MicroStation specific teardown
        #TODO load commands directly from file?
        # Run base class cleanup
        commandfile.CommandFile.teardown(self)

    def point(self, p, reset=False, mode=DEFAULT_MODE, write=True):
        """Convert an iterable into a point of the correct format.

        The mode argument defaults to 'xy=' absolute mode. Other modes can be
        specified, but currently no additional processing is performed.

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
        command = mode.lower() + '={}\n'
        command = command.format(coord)
        if reset:
            command += self.reset(write=False)
        if write:
            self.file.write(command)
        return command

    def points(self, ps, reset=False, mode=DEFAULT_MODE):
        """Calls CommandFile.point on each member of an iterable.

        :param ps: The points to be converted.
        :type command: iterable
        :param reset: Optionally append the result of calling the reset method
            after writing all points.
        :type reset: boolean
        :param mode: Optional point output mode (unimplemented in base class).
        :type mode: string
        """
        commandfile.CommandFile.points(self, ps, mode=mode)
        if reset:
            self.reset()

    def reset(self, write=True):
        """Write a reset command.

        :param write: Flag for writing output to script file.
        :type write: boolean
        :returns: The command that output by reset as a string.
        """
        cmd = 'reset\n'
        if write:
            self.file.write(cmd)
        return cmd

    def line(self, ps, reset=False, mode=DEFAULT_MODE):
        """Write the place line command.

        :param ps: The end points of the lines.
        :type command: iterable
        :param reset: Optionally append the result of calling the reset method
            after writing all points.
        :type reset: boolean
        :param mode: Optional point output mode.
        :type mode: string
        """
        self.cmd("place line")
        self.points(ps, reset=reset, mode=mode)
        return 'l'

    def polyline(self, ps, close=True, reset=False, mode=DEFAULT_MODE):
        """Write the smartline command.

        Support could be added in the future for drawing arc segments or other
        special smartline settings.

        :param ps: The ordered points forming the line.
        :type command: iterable
        :param close: Flag indicating whether the line should end where it started.
        :type close: boolean
        :param reset: Optionally append the result of calling the reset method
            after writing all points.
        :type reset: boolean
        :param mode: Optional point output mode.
        :type mode: string
        """
        if close:
            ps = list(ps)
            ps.append(ps[0])
        self.cmd("place smartline")
        self.points(ps, reset, mode)
        return 'l'
             
    def circle(self, center, radius):
        """Write the place circle command.

        The circle method uses "dx=" mode for setting the radius.
        
        :param center: Point in a format passable to CommandFile.point.
        :type center: iterable
        :param radius: Radius of the circle.
        :type radius: number
        """
        self.cmd("place circle")
        self.point(center)
        self.point((radius, 0), mode='DX')
        self.reset()
        return 'l'

    def text(self, text, p, height=None, ang=None, style=None):
        """Write the place text command.
        
        If a height is provided the text width is set to match. The "choose
        element" command is written after the text to avoid placing the same
        text accidentally.

        :param text: The text to place.
        :type text: string
        :param p: The insertion point in a format passable to CommandFile.point.
        :type p: iterable
        :param height: How tall the text lines are.
        :type height: number
        :param ang: The angle of the text in degrees.
        :type ang: number
        :param style: The text style to activate before placing the text.
        :type style: string
        """
        if style:
            self.file.write('textstyle active {0}\n'.format(style))
        if height:
            self.file.write('TX={0},{0}\n'.format(height))
        if ang:
            self.file.write('AA={}\n'.format(ang))
        self.file.write("place text\n")
        for line in text.split('\n'):
            self.file.write("t,{0}\\010\n".format(line))
        self.point(p)
        # Start default command to exit text entry mode.
        self.cmd('choose element')
        return 'l'

    def _sels(self, els):
        """Sets the provided element as the active selection."""
        self.cmd('choose none')
        if not els:
            raise ValueError('No elements provided!')
        if not hasattr(els, '__iter__'): # Is not iterable
            els = [els]
        for el in els:
            if el.lower() == 'l':
                self.cmd('choose last')
            elif el.lower() == 'p':
                self.cmd('choose previous')
            else:
                self.cmd('choose group add "{}"'.format(el))

    def store(self, name, *els):
        r"""Store provided elements to be manipulated later.

        In MicroStation named groups are used. If 'l' is in els only the last
        element is added to the set. Otherwise the elements in the provided
        groups are joined into the named group.

        :param name: The id used to store the selection.
        :type name: MicroStation quick select group
        :param \*els: The elements to store.
        :type \*els: previous group names, or 'l' for last element 
        :raises: ValueError if no elements are provided.
        :returns: An element group passable to move/copy/rotate/scale methods.
        """
        self._sels(els)
        self.cmd('group add "{}";selview 1;choose none'.format(name))
        return name

    def move(self, els, base=(0, 0), dest=(0, 0)):
        """Transform the provided elements from base to dest.

        :param els: The elements to move.
        :type els: iterable, selection name, 'l' for last, or 'p' for previous
        :param base: The base point to transform from.
        :type base: iterable
        :param dest: The dest point to transform to.
        :type dest: iterable
        :returns: Reference to modified objects.
        """
        self._sels(els)
        self.cmd('move extended')
        self.point(base)
        self.point(dest)
        return els

    def copy(self, els, base=(0, 0), dest=(0, 0)):
        """Transform duplicates of the provided elements from base to dest.

        :param els: The elements to copy.
        :type els: iterable, selection name, 'l' for last, or 'p' for previous
        :param base: The base point to transform from.
        :type base: iterable
        :param dest: The dest point to transform to.
        :type dest: iterable
        :returns: Reference to duplicated objects.
        """
        self._sels(els)
        self.cmd('copy extended')
        self.point(base)
        self.point(dest)
        # FIXME should return newly copied elements
        return els

    def rotate(self, els, base=(0, 0), ang=0):
        """Rotate the provided elements from base by angle.

        :param els: The elements to rotate.
        :type els: iterable, selection name, 'l' for last, or 'p' for previous
        :param base: The base point to transform from.
        :type base: iterable
        :param ang: The angle to rotate in degrees (counter-clockwise).
        :type ang: number
        :returns: Reference to modified objects.
        """
        self._sels(els)
        self.cmd('aa={}'.format(ang))
        self.cmd('rotate original')
        self.point(base)
        self.cmd('aa=0')
        return els

    def scale(self, els, base=(0, 0), scale=1):
        """Scale the provided elements from base by scale.

        :param els: The elements to scale.
        :type els: iterable, selection name, 'l' for last, or 'p' for previous
        :param base: The base point to transform from.
        :type base: iterable
        :param scale: The scale factor to apply.
        :type scale: number
        :returns: Reference to modified objects.
        """
        self._sels(els)
        self.cmd('as={0},{0}'.format(scale))
        self.cmd('scale original')
        self.point(base)
        self.cmd('as=1,1'.format(scale))
        return els
    
    def erase(self, els):
        """Remove the indicated elements.

        :param els: The elements to remove.
        :type els: iterable, selection name, 'l' for last, or 'p' for previous
        """
        self._sels(els)
        self.cmd('delete element')

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

