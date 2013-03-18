# coding: utf8
"""
    cairocffi.context
    ~~~~~~~~~~~~~~~~~

    Bindings for Context objects.

    :copyright: Copyright 2013 by Simon Sapin
    :license: BSD, see LICENSE for details.

"""

from . import ffi, cairo, _check_status, Matrix
from .patterns import Pattern
from .surfaces import Surface
from .fonts import FontFace, ScaledFont, FontOptions, _encode_string
from .compat import xrange


PATH_POINTS_PER_TYPE = {
    'MOVE_TO': 1,
    'LINE_TO': 1,
    'CURVE_TO': 3,
    'CLOSE_PATH': 0}


def _encode_path(path_items):
    """Take an iterable of ``(path_operation, coordinates)`` tuples
    in the same format as from :meth:`Context.copy_path`
    and return a ``(path, data)`` tuple of cdata object.

    The first cdata object is a ``cairo_path_t *`` pointer
    that can be used as long as both objects live.

    """
    points_per_type = PATH_POINTS_PER_TYPE
    path_items = list(path_items)
    length = 0
    for path_type, coordinates in path_items:
        num_points = points_per_type[path_type]
        length += 1 + num_points  # 1 header + N points
        if len(coordinates) != 2 * num_points:
            raise ValueError('Expected %d coordinates, got %d.' % (
                2 * num_points, len(coordinates)))

    data = ffi.new('cairo_path_data_t[]', length)
    position = 0
    for path_type, coordinates in path_items:
        header = data[position].header
        header.type = path_type
        header.length = 1 + len(coordinates) // 2
        position += 1
        for i in xrange(0, len(coordinates), 2):
            point = data[position].point
            point.x = coordinates[i]
            point.y = coordinates[i + 1]
            position += 1
    path = ffi.new('cairo_path_t *', ('SUCCESS', data, length))
    return path, data


def _iter_path(pointer):
    """Take a cairo_path_t * pointer
    and yield ``(path_operation, coordinates)`` tuples.

    See :meth:`Context.copy_path` for the data structure.

    """
    _check_status(pointer.status)
    data = pointer.data
    num_data = pointer.num_data
    points_per_type = PATH_POINTS_PER_TYPE
    position = 0
    while position < num_data:
        path_data = data[position]
        path_type = path_data.header.type
        points = ()
        for i in xrange(points_per_type[path_type]):
            point = data[position + i + 1].point
            points += (point.x, point.y)
        yield (path_type, points)
        position += path_data.header.length


class Context(object):
    """A :class:`Context` contains the current state of the rendering device,
    including coordinates of yet to be drawn shapes.

    Cairo contexts are central to cairo
    and all drawing with cairo is always done to a :class:`Context` object.

    :param target: The target :class:`Surface` object.

    Cairo contexts can be used as Python :ref:`context managers <with>`.
    See :meth:`save`.

    """
    def __init__(self, target):
        self._init_pointer(cairo.cairo_create(target._pointer))

    def _init_pointer(self, pointer):
        self._pointer = ffi.gc(pointer, cairo.cairo_destroy)
        self._check_status()

    def _check_status(self):
        _check_status(cairo.cairo_status(self._pointer))

    @classmethod
    def _from_pointer(cls, pointer, incref):
        """Wrap an existing :c:type:`cairo_t *` cdata pointer.

        :type incref: bool
        :param incref:
            Whether increase the :ref:`reference count <refcounting>` now.
        :return:
            A new :class:`Context` instance.

        """
        if pointer == ffi.NULL:
            raise ValueError('Null pointer')
        if incref:
            cairo.cairo_reference(pointer)
        self = object.__new__(cls)
        cls._init_pointer(self, pointer)
        return self

    def get_target(self):
        """Return this context’s target surface.

        :returns:
            An instance of :class:`Surface` or one of its sub-classes,
            a new Python object referencing the existing cairo surface.

        """
        return Surface._from_pointer(
            cairo.cairo_get_target(self._pointer), incref=True)

    ##
    ##  Save / restore
    ##

    def save(self):
        """Makes a copy of the current state of this context
        and saves it on an internal stack of saved states.
        When :meth:`restore` is called,
        the context will be restored to the saved state.
        Multiple calls to :meth:`save` and :meth:`restore` can be nested;
        each call to :meth:`restore` restores the state
        from the matching paired :meth:`save`.

        Instead of using :meth:`save` and :meth:`restore` directly,
        it is recommended to use a :ref:`with statement <with>`::

            with context:
                do_something(context)

        … which is equivalent to::

            context.save()
            try:
                do_something(context)
            finally:
                context.restore()

        """
        cairo.cairo_save(self._pointer)
        self._check_status()

    def restore(self):
        """Restores the context to the state saved
        by a preceding call to :meth:`save`
        and removes that state from the stack of saved states.

        """
        cairo.cairo_restore(self._pointer)
        self._check_status()

    def __enter__(self):
        self.save()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.restore()

    ##
    ##  Groups
    ##

    def push_group(self):
        """Temporarily redirects drawing to an intermediate surface
        known as a group.
        The redirection lasts until the group is completed
        by a call to :meth:`pop_group` or :meth:`pop_group_to_source`.
        These calls provide the result of any drawing
        to the group as a pattern,
        (either as an explicit object, or set as the source pattern).

        This group functionality can be convenient
        for performing intermediate compositing.
        One common use of a group is to render objects
        as opaque within the group,  (so that they occlude each other),
        and then blend the result with translucence onto the destination.

        Groups can be nested arbitrarily deep
        by making balanced calls to :meth:`push_group` / :meth:`pop_group`.
        Each call pushes / pops the new target group onto / from a stack.

        The :meth:`group` method calls :meth:`save`
        so that any changes to the graphics state
        will not be visible outside the group,
        (the pop_group methods call :meth:`restore`).

        By default the intermediate group will have
        a content type of :obj:`COLOR_ALPHA <CONTENT_COLOR_ALPHA>`.
        Other content types can be chosen for the group
        by using :meth:`push_group_with_content` instead.

        As an example,
        here is how one might fill and stroke a path with translucence,
        but without any portion of the fill being visible under the stroke::

            context.push_group()
            context.set_source(fill_pattern)
            context.fill_preserve()
            context.set_source(stroke_pattern)
            context.stroke()
            context.pop_group_to_source()
            context.paint_with_alpha(alpha)

        """
        cairo.cairo_push_group(self._pointer)
        self._check_status()

    def push_group_with_content(self, content):
        """Temporarily redirects drawing to an intermediate surface
        known as a group.
        The redirection lasts until the group is completed
        by a call to :meth:`pop_group` or :meth:`pop_group_to_source`.
        These calls provide the result of any drawing
        to the group as a pattern,
        (either as an explicit object, or set as the source pattern).

        The group will have a content type of :obj:`content`.
        The ability to control this content  type
        is the only distinction between this method and :meth:`push_group`
        which you should see for a more detailed description
        of group rendering.

        :param content: A :ref:`CONTENT` string.

        """
        cairo.cairo_push_group_with_content(self._pointer, content)
        self._check_status()

    def pop_group(self):
        """Terminates the redirection begun by a call to :meth:`push_group`
        or :meth:`push_group_with_content`
        and returns a new pattern containing the results
        of all drawing operations performed to the group.

        The :meth:`pop_group` method calls :meth:`restore`,
        (balancing a call to :meth:`save` by the push_group method),
        so that any changes to the graphics state
        will not be visible outside the group.

        :returns:
            A newly created :class:`SurfacePattern`
            containing the results of all drawing operations
            performed to the group.

        """
        return Pattern._from_pointer(
            cairo.cairo_pop_group(self._pointer), incref=False)

    def pop_group_to_source(self):
        """Terminates the redirection begun by a call to :meth:`push_group`
        or :meth:`push_group_with_content`
        and installs the resulting pattern
        as the source pattern in the given cairo context.

        The behavior of this method is equivalent to::

            context.set_source(context.pop_group())

        """
        cairo.cairo_pop_group_to_source(self._pointer)
        self._check_status()

    def get_group_target(self):
        """Returns the current destination surface for the context.
        This is either the original target surface
        as passed to :class:`Context`
        or the target surface for the current group as started
        by the most recent call to :meth:`push_group`
        or :meth:`push_group_with_content`.

        """
        return Surface._from_pointer(
            cairo.cairo_get_group_target(self._pointer), incref=True)

    ##
    ##  Sources
    ##

    def set_source_rgba(self, red, green, blue, alpha=1):
        """Sets the source pattern within this context to a solid color.
        This color will then be used for any subsequent drawing operation
        until a new source pattern is set.

        The color and alpha components are
        floating point numbers  in the range 0 to 1.
        If the values passed in are outside that range, they will be clamped.

        The default source pattern is opaque black,
        (that is, it is equivalent to ``context.set_source_rgba(0, 0, 0)``).

        :param red: Red component of the color.
        :param green: Green component of the color.
        :param blue: Blue component of the color.
        :param alpha:
            Alpha component of the color.
            1 (the default) is opaque, 0 fully transparent.
        :type red: float
        :type green: float
        :type blue: float
        :type alpha: float

        """
        cairo.cairo_set_source_rgba(self._pointer, red, green, blue, alpha)
        self._check_status()

    def set_source_rgb(self, red, green, blue):
        """Same as :meth:`set_source_rgba` with alpha always 1.
        Exists for compatibility with pycairo.

        """
        cairo.cairo_set_source_rgb(self._pointer, red, green, blue)
        self._check_status()

    def set_source_surface(self, surface, x=0, y=0):
        """This is a convenience method for creating a pattern from surface
        and setting it as the source in this context with :meth:`set_source`.

        The :obj:`x` and :obj:`y` parameters give the user-space coordinate
        at which the surface origin should appear.
        (The surface origin is its upper-left corner
        before any transformation has been applied.)
        The :obj:`x` and :obj:`y` parameters are negated
        and then set as translation values in the pattern matrix.

        Other than the initial translation pattern matrix, as described above,
        all other pattern attributes, (such as its extend mode),
        are set to the default values as in :class:`SurfacePattern`.
        The resulting pattern can be queried with :meth:`get_source`
        so that these attributes can be modified if desired,
        (eg. to create a repeating pattern with :meth:`Pattern.set_extend`).

        :param surface:
            A :class:`Surface` to be used to set the source pattern.
        :param x: User-space X coordinate for surface origin.
        :param y: User-space Y coordinate for surface origin.
        :type x: float
        :type y: float

        """
        cairo.cairo_set_source_surface(self._pointer, surface._pointer, x, y)
        self._check_status()

    def set_source(self, source):
        """Sets the source pattern within this context to :obj:`source`.
        This pattern will then be used for any subsequent drawing operation
        until a new source pattern is set.

        .. note::

            The pattern's transformation matrix will be locked
            to the user space in effect at the time of :meth:`set_source`.
            This means that further modifications
            of the current transformation matrix
            will not affect the source pattern.
            See :meth:`Pattern.set_matrix`.

        The default source pattern is opaque black,
        (that is, it is equivalent to ``context.set_source_rgba(0, 0, 0)``).

        :param source:
            A :class:`Pattern` to be used
            as the source for subsequent drawing operations.

        """
        cairo.cairo_set_source(self._pointer, source._pointer)
        self._check_status()

    def get_source(self):
        """Return this context’s source.

        :returns:
            An instance of :class:`Pattern` or one of its sub-classes,
            a new Python object referencing the existing cairo pattern.

        """
        return Pattern._from_pointer(
            cairo.cairo_get_source(self._pointer), incref=True)

    ##
    ##  Context parameters
    ##

    def set_antialias(self, antialias):
        """Set the :ref:`ANTIALIAS` of the rasterizer used for drawing shapes.
        This value is a hint,
        and a particular backend may or may not support a particular value.
        At the current time,
        no backend supports :obj:`SUBPIXEL <ANTIALIAS_SUBPIXEL>`
        when drawing shapes.

        Note that this option does not affect text rendering,
        instead see :meth:`FontOptions.set_antialias`.

        :param antialias: An :ref:`ANTIALIAS` string.

        """
        cairo.cairo_set_antialias(self._pointer, antialias)
        self._check_status()

    def get_antialias(self):
        """Return the :ref:`ANTIALIAS` string."""
        return cairo.cairo_get_antialias(self._pointer)

    def set_dash(self, dashes, offset=0):
        """Sets the dash pattern to be used by :meth:`stroke`.
        A dash pattern is specified by dashes, a list of positive values.
        Each value provides the length of alternate "on" and "off"
        portions of the stroke.
        :obj:`offset` specifies an offset into the pattern
        at which the stroke begins.

        Each "on" segment will have caps applied
        as if the segment were a separate sub-path.
        In particular, it is valid to use an "on" length of 0
        with :obj:`LINE_CAP_ROUND` or :obj:`LINE_CAP_SQUARE`
        in order to distributed dots or squares along a path.

        Note: The length values are in user-space units
        as evaluated at the time of stroking.
        This is not necessarily the same as the user space
        at the time of :meth:`set_dash`.

        If :obj:`dashes` is empty dashing is disabled.
        If it is of length 1 a symmetric pattern is assumed
        with alternating on and off portions of the size specified
        by the single value.

        :param dashes:
            A list of floats specifying alternate lengths
            of on and off stroke portions.
        :type offset: float
        :param offset:
            An offset into the dash pattern at which the stroke should start.
        :raises:
            :exc:`CairoError`
            if any value in dashes is negative,
            or if all values are 0.
            The context  will be put into an error state.

        """
        cairo.cairo_set_dash(
            self._pointer, ffi.new('double[]', dashes), len(dashes), offset)
        self._check_status()

    def get_dash(self):
        """Return the current dash pattern.

        :returns:
            A ``(dashes, offset)`` tuple of a list and a float.
            :obj:`dashes` is a list of floats,
            empty if no dashing is in effect.

        """
        dashes = ffi.new('double[]', cairo.cairo_get_dash_count(self._pointer))
        offset = ffi.new('double *')
        cairo.cairo_get_dash(self._pointer, dashes, offset)
        self._check_status()
        return list(dashes), offset[0]

    def get_dash_count(self):
        """Same as ``len(context.get_dash()[0])``."""
        # Not really useful with get_dash() returning a list,
        # but retained for compatibility with pycairo.
        return cairo.cairo_get_dash_count(self._pointer)

    def set_fill_rule(self, fill_rule):
        """Set the current :ref:`FILL_RULE` within the cairo context.
        The fill rule is used to determine which regions are inside
        or outside a complex (potentially self-intersecting) path.
        The current fill rule affects both :meth:`fill` and :meth:`clip`.

        The default fill rule is :obj:`WINDING <FILL_RULE_WINDING>`.

        :param fill_rule: A :ref:`FILL_RULE` string.

        """
        cairo.cairo_set_fill_rule(self._pointer, fill_rule)
        self._check_status()

    def get_fill_rule(self):
        """Return the current :ref:`FILL_RULE` string."""
        return cairo.cairo_get_fill_rule(self._pointer)

    def set_line_cap(self, line_cap):
        """Set the current :ref:`LINE_CAP` within the cairo context.
        As with the other stroke parameters,
        the current line cap style is examined by
        :meth:`stroke`, :meth:`stroke_extents`, and :meth:`stroke_to_path`,
        but does not have any effect during path construction.

        The default line cap is :obj:`BUTT <LINE_CAP_BUTT>`.

        :param line_cap: A :ref:`LINE_CAP` string.

        """
        cairo.cairo_set_line_cap(self._pointer, line_cap)
        self._check_status()

    def get_line_cap(self):
        """Return the current :ref:`LINE_CAP` string."""
        return cairo.cairo_get_line_cap(self._pointer)

    def set_line_join(self, line_join):
        """Set the current :ref:`LINE_JOIN` within the cairo context.
        As with the other stroke parameters,
        the current line cap style is examined by
        :meth:`stroke`, :meth:`stroke_extents`, and :meth:`stroke_to_path`,
        but does not have any effect during path construction.

        The default line cap is :obj:`MITER <LINE_JOIN_MITER>`.

        :param line_join: A :ref:`LINE_JOIN` string.

        """
        cairo.cairo_set_line_join(self._pointer, line_join)
        self._check_status()

    def get_line_join(self):
        """Return the current :ref:`LINE_JOIN` string."""
        return cairo.cairo_get_line_join(self._pointer)

    def set_line_width(self, width):
        """Sets the current line width within the cairo context.
        The line width value specifies the diameter of a pen
        that is circular in user space,
        (though device-space pen may be an ellipse in general
        due to scaling / shear / rotation of the CTM).

        .. note::
            When the description above refers to user space and CTM
            it refers to the user space and CTM in effect
            at the time of the stroking operation,
            not the user space and CTM in effect
            at the time of the call to :meth:`set_line_width`.
            The simplest usage makes both of these spaces identical.
            That is, if there is no change to the CTM
            between a call to :meth:`set_line_width`
            and the stroking operation,
            then one can just pass user-space values to :meth:`set_line_width`
            and ignore this note.

        As with the other stroke parameters,
        the current line cap style is examined by
        :meth:`stroke`, :meth:`stroke_extents`, and :meth:`stroke_to_path`,
        but does not have any effect during path construction.

        The default line width value is 2.0.

        :type width: float
        :param width: The new line width.

        """
        cairo.cairo_set_line_width(self._pointer, width)
        self._check_status()

    def get_line_width(self):
        """Return the current line width as a float."""
        return cairo.cairo_get_line_width(self._pointer)

    def set_miter_limit(self, limit):
        """Sets the current miter limit within the cairo context.

        If the current line join style is set to :obj:`MITER <LINE_JOIN_MITER>`
        (see :meth:`set_line_join`),
        the miter limit is used to determine
        whether the lines should be joined with a bevel instead of a miter.
        Cairo divides the length of the miter by the line width.
        If the result is greater than the miter limit,
        the style is converted to a bevel.

        As with the other stroke parameters,
        the current line cap style is examined by
        :meth:`stroke`, :meth:`stroke_extents`, and :meth:`stroke_to_path`,
        but does not have any effect during path construction.

        The default miter limit value is 10.0,
        which will convert joins with interior angles less than 11 degrees
        to bevels instead of miters.
        For reference,
        a miter limit of 2.0 makes the miter cutoff at 60 degrees,
        and a miter limit of 1.414 makes the cutoff at 90 degrees.

        A miter limit for a desired angle can be computed as:
        ``miter_limit = 1. / sin(angle / 2.)``

        :param limit: The miter limit to set.
        :type limit: float

        """
        cairo.cairo_set_miter_limit(self._pointer, limit)
        self._check_status()

    def get_miter_limit(self):
        """Return the current miter limit as a float."""
        return cairo.cairo_get_miter_limit(self._pointer)

    def set_operator(self, operator):
        """Set the current :ref:`OPERATOR`
        to be used for all drawing operations.

        The default operator is :obj:`OVER <OPERATOR_OVER>`.

        :param operator: A :ref:`OPERATOR` string.

        """
        cairo.cairo_set_operator(self._pointer, operator)
        self._check_status()

    def get_operator(self):
        """Return the current :ref:`OPERATOR` string."""
        return cairo.cairo_get_operator(self._pointer)

    def set_tolerance(self, tolerance):
        """Sets the tolerance used when converting paths into trapezoids.
        Curved segments of the path will be subdivided
        until the maximum deviation between the original path
        and the polygonal approximation is less than tolerance.
        The default value is 0.1.
        A larger value will give better performance,
        a smaller value, better appearance.
        (Reducing the value from the default value of 0.1
        is unlikely to improve appearance significantly.)
        The accuracy of paths within Cairo is limited
        by the precision of its internal arithmetic,
        and the prescribed tolerance is restricted
        to the smallest representable internal value.

        :type tolerance: float
        :param tolerance: The tolerance, in device units (typically pixels)

        """
        cairo.cairo_set_tolerance(self._pointer, tolerance)
        self._check_status()

    def get_tolerance(self):
        """Return the current tolerance as a float."""
        return cairo.cairo_get_tolerance(self._pointer)

    ##
    ##  CTM: Current transformation matrix
    ##

    def translate(self, tx, ty):
        """Modifies the current transformation matrix (CTM)
        by translating the user-space origin by ``(tx, ty)``.
        This offset is interpreted as a user-space coordinate
        according to the CTM in place before the new call to :meth:`translate`.
        In other words, the translation of the user-space origin takes place
        after any existing transformation.

        :param tx: Amount to translate in the X direction
        :param ty: Amount to translate in the Y direction
        :type tx: float
        :type ty: float

        """
        cairo.cairo_translate(self._pointer, tx, ty)
        self._check_status()

    def scale(self, sx, sy=None):
        """Modifies the current transformation matrix (CTM)
        by scaling the X and Y user-space axes
        by :obj:`sx` and :obj:`sy` respectively.
        The scaling of the axes takes place after
        any existing transformation of user space.

        If :obj:`sy` is omitted, it is the same as :obj:`sx`
        so that scaling preserves aspect ratios.

        :param sx: Scale factor in the X direction.
        :param sy: Scale factor in the Y direction.
        :type sx: float
        :type sy: float

        """
        if sy is None:
            sy = sx
        cairo.cairo_scale(self._pointer, sx, sy)
        self._check_status()

    def rotate(self, radians):
        """Modifies the current transformation matrix (CTM)
        by rotating the user-space axes by angle :obj:`radians`.
        The rotation of the axes takes places
        after any existing transformation of user space.

        :type radians: float
        :param radians:
            Angle of rotation, in radians.
            The direction of rotation is defined such that positive angles
            rotate in the direction from the positive X axis
            toward the positive Y axis.
            With the default axis orientation of cairo,
            positive angles rotate in a clockwise direction.

        """
        cairo.cairo_rotate(self._pointer, radians)
        self._check_status()

    def transform(self, matrix):
        """Modifies the current transformation matrix (CTM)
        by applying :obj:`matrix` as an additional transformation.
        The new transformation of user space takes place
        after any existing transformation.

        :param matrix:
            A transformation :class:`Matrix`
            to be applied to the user-space axes.

        """
        cairo.cairo_transform(self._pointer, matrix._pointer)
        self._check_status()

    def set_matrix(self, matrix):
        """Modifies the current transformation matrix (CTM)
        by setting it equal to :obj:`matrix`.

        :param matrix:
            A transformation :class:`Matrix` from user space to device space.

        """
        cairo.cairo_set_matrix(self._pointer, matrix._pointer)
        self._check_status()

    def get_matrix(self):
        """Return a copy of the current transformation matrix (CTM)."""
        matrix = Matrix()
        cairo.cairo_get_matrix(self._pointer, matrix._pointer)
        self._check_status()
        return matrix

    def identity_matrix(self):
        """Resets the current transformation matrix (CTM)
        by setting it equal to the identity matrix.
        That is, the user-space and device-space axes will be aligned
        and one user-space unit will transform to one device-space unit.

        """
        cairo.cairo_identity_matrix(self._pointer)
        self._check_status()

    def user_to_device(self, x, y):
        """Transform a coordinate from user space to device space
        by multiplying the given point
        by the current transformation matrix (CTM).

        :param x: X position.
        :param y: Y position.
        :type x: float
        :type y: float
        :returns: A ``(device_x, device_y)`` tuple of floats.

        """
        xy = ffi.new('double[2]', [x, y])
        cairo.cairo_user_to_device(self._pointer, xy + 0, xy + 1)
        self._check_status()
        return tuple(xy)

    def user_to_device_distance(self, dx, dy):
        """Transform a distance vector from user space to device space.
        This method is similar to :meth:`Context.user_to_device`
        except that the translation components of the CTM
        will be ignored when transforming ``(dx, dy)``.

        :param x: X component of a distance vector.
        :param y: Y component of a distance vector.
        :type x: float
        :type y: float
        :returns: A ``(device_dx, device_dy)`` tuple of floats.

        """
        xy = ffi.new('double[2]', [dx, dy])
        cairo.cairo_user_to_device_distance(self._pointer, xy + 0, xy + 1)
        self._check_status()
        return tuple(xy)

    def device_to_user(self, x, y):
        """Transform a coordinate from device space to user space
        by multiplying the given point
        by the inverse of the current transformation matrix (CTM).

        :param x: X position.
        :param y: Y position.
        :type x: float
        :type y: float
        :returns: A ``(user_x, user_y)`` tuple of floats.

        """
        xy = ffi.new('double[2]', [x, y])
        cairo.cairo_device_to_user(self._pointer, xy + 0, xy + 1)
        self._check_status()
        return tuple(xy)

    def device_to_user_distance(self, dx, dy):
        """Transform a distance vector from device space to user space.
        This method is similar to :meth:`Context.device_to_user`
        except that the translation components of the inverse CTM
        will be ignored when transforming ``(dx, dy)``.

        :param x: X component of a distance vector.
        :param y: Y component of a distance vector.
        :type x: float
        :type y: float
        :returns: A ``(user_dx, user_dy)`` tuple of floats.

        """
        xy = ffi.new('double[2]', [dx, dy])
        cairo.cairo_device_to_user_distance(self._pointer, xy + 0, xy + 1)
        self._check_status()
        return tuple(xy)

    ##
    ##  Path
    ##

    def has_current_point(self):
        """Returns whether a current point is defined on the current path.
        See :meth:`get_current_point`.

        """
        return bool(cairo.cairo_has_current_point(self._pointer))

    def get_current_point(self):
        """Return the current point of the current path,
        which is conceptually the final point reached by the path so far.

        The current point is returned in the user-space coordinate system.
        If there is no defined current point
        or if the context is in an error status,
        ``(0, 0)`` is returned.
        It is possible to check this in advance with :meth:`has_current_point`.

        Most path construction methods alter the current point.
        See the following for details on how they affect the current point:
        :meth:`new_path`,
        :meth:`new_sub_path`,
        :meth:`append_path`,
        :meth:`close_path`,
        :meth:`move_to`,
        :meth:`line_to`,
        :meth:`curve_to`,
        :meth:`rel_move_to`,
        :meth:`rel_line_to`,
        :meth:`rel_curve_to`,
        :meth:`arc`,
        :meth:`arc_negative`,
        :meth:`rectangle`,
        :meth:`text_path`,
        :meth:`glyph_path`,
        :meth:`stroke_to_path`.

        Some methods use and alter the current point
        but do not otherwise change current path:
        :meth:`show_text`,
        :meth:`show_glyphs`,
        :meth:`show_text_glyphs`.

        Some methods unset the current path and as a result, current point:
        :meth:`fill`,
        :meth:`stroke`.

        :returns:
            A ``(x, y)`` tuple of floats, the coordinates of the current point.

        """
        # I’d prefer returning None if self.has_current_point() is False
        # But keep (0, 0) for compat with pycairo.
        xy = ffi.new('double[2]')
        cairo.cairo_get_current_point(self._pointer, xy + 0, xy + 1)
        self._check_status()
        return tuple(xy)

    def new_path(self):
        """ Clears the current path.
        After this call there will be no path and no current point.

        """
        cairo.cairo_new_path(self._pointer)
        self._check_status()

    def new_sub_path(self):
        """Begin a new sub-path.
        Note that the existing path is not affected.
        After this call there will be no current point.

        In many cases, this call is not needed
        since new sub-paths are frequently started with :meth:`move_to`.

        A call to :meth:`new_sub_path` is particularly useful
        when beginning a new sub-path with one of the :meth:`arc` calls.
        This makes things easier as it is no longer necessary
        to manually compute the arc's initial coordinates
        for a call to :meth:`move_to`.

        """
        cairo.cairo_new_sub_path(self._pointer)
        self._check_status()

    def move_to(self, x, y):
        """Begin a new sub-path.
        After this call the current point will be ``(x, y)``.

        :param x: X position of the new point.
        :param y: Y position of the new point.
        :type float: x
        :type float: y

        """
        cairo.cairo_move_to(self._pointer, x, y)
        self._check_status()

    def rel_move_to(self, dx, dy):
        """Begin a new sub-path.
        After this call the current point will be offset by ``(dx, dy)``.

        Given a current point of ``(x, y)``,
        ``context.rel_move_to(dx, dy)`` is logically equivalent to
        ``context.move_to(x + dx, y + dy)``.

        :param dx: The X offset.
        :param dy: The Y offset.
        :type float: dx
        :type float: dy
        :raises:
            :exc:`CairoError` if there is no current point.
            Doing so will cause leave the context in an error state.

        """
        cairo.cairo_rel_move_to(self._pointer, dx, dy)
        self._check_status()

    def line_to(self, x, y):
        """Adds a line to the path from the current point
        to position ``(x, y)`` in user-space coordinates.
        After this call the current point will be ``(x, y)``.

        If there is no current point before the call to :meth:`line_to`
        this method will behave as ``context.move_to(x, y)``.

        :param x: X coordinate of the end of the new line.
        :param y: Y coordinate of the end of the new line.
        :type float: x
        :type float: y

        """
        cairo.cairo_line_to(self._pointer, x, y)
        self._check_status()

    def rel_line_to(self, dx, dy):
        """ Relative-coordinate version of :meth:`line_to`.
        Adds a line to the path from the current point
        to a point that is offset from the current point
        by ``(dx, dy)`` in user space.
        After this call the current point will be offset by ``(dx, dy)``.

        Given a current point of ``(x, y)``,
        ``context.rel_line_to(dx, dy)`` is logically equivalent to
        ``context.line_to(x + dx, y + dy)``.

        :param dx: The X offset to the end of the new line.
        :param dy: The Y offset to the end of the new line.
        :type float: dx
        :type float: dy
        :raises:
            :exc:`CairoError` if there is no current point.
            Doing so will cause leave the context in an error state.

        """
        cairo.cairo_rel_line_to(self._pointer, dx, dy)
        self._check_status()

    def rectangle(self, x, y, width, height):
        """Adds a closed sub-path rectangle
        of the given size to the current path
        at position ``(x, y)`` in user-space coordinates.

        This method is logically equivalent to::

            context.move_to(x, y)
            context.rel_line_to(width, 0)
            context.rel_line_to(0, height)
            context.rel_line_to(-width, 0)
            context.close_path()

        :param x: The X coordinate of the top left corner of the rectangle.
        :param y: The Y coordinate of the top left corner of the rectangle.
        :param width: Width of the rectangle.
        :param height: Height of the rectangle.
        :type float: x
        :type float: y
        :type float: width
        :type float: heigth

        """
        cairo.cairo_rectangle(self._pointer, x, y, width, height)
        self._check_status()

    def arc(self, xc, yc, radius, angle1, angle2):
        """Adds a circular arc of the given radius to the current path.
        The arc is centered at ``(xc, yc)``,
        begins at :obj:`angle1`
        and proceeds in the direction of increasing angles
        to end at :obj:`angle2`.
        If :obj:`angle2` is less than :obj:`angle1`
        it will be progressively increased by ``2 * pi``
        until it is greater than :obj:`angle1`.

        If there is a current point,
        an initial line segment will be added to the path
        to connect the current point to the beginning of the arc.
        If this initial line is undesired,
        it can be avoided by calling :meth:`new_sub_path`
        before calling :meth:`arc`.

        Angles are measured in radians.
        An angle of 0 is in the direction of the positive X axis
        (in user space).
        An angle of ``pi / 2`` radians (90 degrees)
        is in the direction of the positive Y axis (in user space).
        Angles increase in the direction from the positive X axis
        toward the positive Y axis.
        So with the default transformation matrix,
        angles increase in a clockwise direction.

        (To convert from degrees to radians, use ``degrees * pi / 180``.)

        This method gives the arc in the direction of increasing angles;
        see :meth:`arc_negative` to get the arc
        in the direction of decreasing angles.

        The arc is circular in user space.
        To achieve an elliptical arc,
        you can scale the current transformation matrix
        by different amounts in the X and Y directions.
        For example, to draw an ellipse in the box
        given by x, y, width, height::

            from math import pi
            with context:
                context.translate(x + width / 2., y + height / 2.)
                context.scale(width / 2., height / 2.)
                context.arc(0, 0, 1, 0, 2 * pi)

        :param xc: X position of the center of the arc.
        :param yc: Y position of the center of the arc.
        :param radius: The radius of the arc.
        :param angle1: The start angle, in radians.
        :param angle2: The end angle, in radians.
        :type xc: float
        :type yc: float
        :type radius: float
        :type angle1: float
        :type angle2: float

        """
        cairo.cairo_arc(self._pointer, xc, yc, radius, angle1, angle2)
        self._check_status()

    def arc_negative(self, xc, yc, radius, angle1, angle2):
        """Adds a circular arc of the given radius to the current path.
        The arc is centered at ``(xc, yc)``,
        begins at :obj:`angle1`
        and proceeds in the direction of decreasing angles
        to end at :obj:`angle2`.
        If :obj:`angle2` is greater than :obj:`angle1`
        it will be progressively decreased by ``2 * pi``
        until it is greater than :obj:`angle1`.

        See :meth:`arc` for more details.
        This method differs only in
        the direction of the arc between the two angles.

        :param xc: X position of the center of the arc.
        :param yc: Y position of the center of the arc.
        :param radius: The radius of the arc.
        :param angle1: The start angle, in radians.
        :param angle2: The end angle, in radians.
        :type xc: float
        :type yc: float
        :type radius: float
        :type angle1: float
        :type angle2: float

        """
        cairo.cairo_arc_negative(self._pointer, xc, yc, radius, angle1, angle2)
        self._check_status()

    def curve_to(self, x1, y1, x2, y2, x3, y3):
        """Adds a cubic Bézier spline to the path
        from the current point
        to position ``(x3, y3)`` in user-space coordinates,
        using ``(x1, y1)`` and ``(x2, y2)`` as the control points.
        After this call the current point will be ``(x3, y3)``.

        If there is no current point before the call to :meth:`curve_to`
        this method will behave as if preceded by
        a call to ``context.move_to(x1, y1)``.

        :param x1: The X coordinate of the first control point.
        :param y1: The Y coordinate of the first control point.
        :param x2: The X coordinate of the second control point.
        :param y2: The Y coordinate of the second control point.
        :param x3: The X coordinate of the end of the curve.
        :param y3: The Y coordinate of the end of the curve.
        :type x1: float
        :type y1: float
        :type x2: float
        :type y2: float
        :type x3: float
        :type y3: float

        """
        cairo.cairo_curve_to(self._pointer, x1, y1, x2, y2, x3, y3)
        self._check_status()

    def rel_curve_to(self, dx1, dy1, dx2, dy2, dx3, dy3):
        """ Relative-coordinate version of :meth:`curve_to`.
        All offsets are relative to the current point.
        Adds a cubic Bézier spline to the path from the current point
        to a point offset from the current point by ``(dx3, dy3)``,
        using points offset by ``(dx1, dy1)`` and ``(dx2, dy2)``
        as the control points.
        After this call the current point will be offset by ``(dx3, dy3)``.

        Given a current point of ``(x, y)``,
        ``context.rel_curve_to(dx1, dy1, dx2, dy2, dx3, dy3)``
        is logically equivalent to
        ``context.curve_to(x+dx1, y+dy1, x+dx2, y+dy2, x+dx3, y+dy3)``.

        :param dx1: The X offset to the first control point.
        :param dy1: The Y offset to the first control point.
        :param dx2: The X offset to the second control point.
        :param dy2: The Y offset to the second control point.
        :param dx3: The X offset to the end of the curve.
        :param dy3: The Y offset to the end of the curve.
        :type dx1: float
        :type dy1: float
        :type dx2: float
        :type dy2: float
        :type dx3: float
        :type dy3: float
        :raises:
            :exc:`CairoError` if there is no current point.
            Doing so will cause leave the context in an error state.

        """
        cairo.cairo_rel_curve_to(self._pointer, dx1, dy1, dx2, dy2, dx3, dy3)
        self._check_status()

    def text_path(self, text):
        """Adds closed paths for text to the current path.
        The generated path if filled,
        achieves an effect similar to that of :meth:`show_text`.

        Text conversion and positioning is done similar to :meth:`show_text`.

        Like :meth:`show_text`,
        after this call the current point is moved to the origin of where
        the next glyph would be placed in this same progression.
        That is, the current point will be at the origin of the final glyph
        offset by its advance values.
        This allows for chaining multiple calls to to :meth:`text_path`
        without having to set current point in between.

        :param text: The text to show, as an Unicode or UTF-8 string.

        .. note::
            The :meth:`text_path` method is part of
            what the cairo designers call the "toy" text API.
            It is convenient for short demos and simple programs,
            but it is not expected to be adequate
            for serious text-using applications.
            See :ref:`fonts` for details,
            and :meth:`glyph_path` for the "real" text path API in cairo.

        """
        cairo.cairo_text_path(self._pointer, _encode_string(text))
        self._check_status()

    def glyph_path(self, glyphs):
        """Adds closed paths for the glyphs to the current path.
        The generated path if filled,
        achieves an effect similar to that of :meth:`show_glyphs`.

        :param glyphs:
            The glyphs to show.
            See :meth:`show_text_glyphs` for the data structure.

        """
        glyphs = ffi.new('cairo_glyph_t[]', glyphs)
        cairo.cairo_glyph_path(self._pointer, glyphs, len(glyphs))
        self._check_status()

    def close_path(self):
        """Adds a line segment to the path
        from the current point
        to the beginning of the current sub-path,
        (the most recent point passed to cairo_move_to()),
        and closes this sub-path.
        After this call the current point will be
        at the joined endpoint of the sub-path.

        The behavior of :meth:`close_path` is distinct
        from simply calling :meth:`line_to` with the equivalent coordinate
        in the case of stroking.
        When a closed sub-path is stroked,
        there are no caps on the ends of the sub-path.
        Instead, there is a line join
        connecting the final and initial segments of the sub-path.

        If there is no current point before the call to :meth:`close_path`,
        this method will have no effect.

        """
        cairo.cairo_close_path(self._pointer)
        self._check_status()

    def copy_path(self):
        """Return a copy of the current path.

        :returns:
            A list of ``(path_operation, coordinates)`` tuples
            of a :ref:`PATH_OPERATION` string
            and a tuple of floats coordinates
            whose content depends on the operation type:

            * :obj:`MOVE_TO <PATH_MOVE_TO>`: 1 point ``(x, y)``
            * :obj:`LINE_TO <PATH_LINE_TO>`: 1 point ``(x, y)``
            * :obj:`CURVE_TO <PATH_CURVE_TO>`: 3 points
              ``(x1, y1, x2, y2, x3, y3)``
            * :obj:`CLOSE_PATH <PATH_CLOSE_PATH>` 0 points ``()`` (empty tuple)

        """
        path = cairo.cairo_copy_path(self._pointer)
        result = list(_iter_path(path))
        cairo.cairo_path_destroy(path)
        return result

    def copy_path_flat(self):
        """Return a flattened copy of the current path

        This method is like :meth:`copy_path`
        except that any curves in the path will be approximated
        with piecewise-linear approximations,
        (accurate to within the current tolerance value,
        see :meth:`set_tolerance`).
        That is,
        the result is guaranteed to not have any elements
        of type :obj:`CURVE_TO <PATH_CURVE_TO>`
        which will instead be replaced by
        a series of :obj:`LINE_TO <PATH_LINE_TO>` elements.

        :returns:
            A list of ``(path_operation, coordinates)`` tuples.
            See :meth:`copy_path` for the data structure.

        """
        path = cairo.cairo_copy_path_flat(self._pointer)
        result = list(_iter_path(path))
        cairo.cairo_path_destroy(path)
        return result

    def append_path(self, path):
        """Append :obj:`path` onto the current path.
        The path may be either the return value from one of :meth:`copy_path`
        or :meth:`copy_path_flat` or it may be constructed manually.

        :param path:
            An iterable of tuples
            in the same format as returned by :meth:`copy_path`.

        """
        # Both objects need to stay alive
        # until after cairo.cairo_append_path() is finished, but not after.
        path, _ = _encode_path(path)
        cairo.cairo_append_path(self._pointer, path)
        self._check_status()

    def path_extents(self):
        """Computes a bounding box in user-space coordinates
        covering the points on the current path.
        If the current path is empty,
        returns an empty rectangle ``(0, 0, 0, 0)``.
        Stroke parameters, fill rule, surface dimensions and clipping
        are not taken into account.

        Contrast with :meth:`fill_extents` and :meth:`stroke_extents`
        which return the extents of only the area that would be "inked"
        by the corresponding drawing operations.

        The result of :meth:`path_extents`
        is defined as equivalent to the limit of :meth:`stroke_extents`
        with :obj:`LINE_CAP_ROUND` as the line width approaches 0,
        (but never reaching the empty-rectangle
        returned by :meth:`stroke_extents` for a line width of 0).

        Specifically, this means that zero-area sub-paths
        such as :meth:`move_to`; :meth:`line_to()` segments,
        (even degenerate cases
        where the coordinates to both calls are identical),
        will be considered as contributing to the extents.
        However, a lone :meth:`move_to` will not contribute
        to the results of :meth:`path_extents`.

        :return:
            A ``(x1, y1, x2, y2)`` tuple of floats:
            the left, top, right and bottom of the resulting extents,
            respectively.

        """
        extents = ffi.new('double[4]')
        cairo.cairo_path_extents(
            self._pointer, extents + 0, extents + 1, extents + 2, extents + 3)
        self._check_status()
        return tuple(extents)

    ##
    ##  Drawing operators
    ##

    def paint(self):
        """A drawing operator that paints the current source everywhere
        within the current clip region.

        """
        cairo.cairo_paint(self._pointer)
        self._check_status()

    def paint_with_alpha(self, alpha):
        """A drawing operator that paints the current source everywhere
        within the current clip region
        using a mask of constant alpha value alpha.
        The effect is similar to :meth:`paint`,
        but the drawing is faded out using the :obj:`alpha` value.

        :type alpha: float
        :param alpha: Alpha value, between 0 (transparent) and 1 (opaque).

        """
        cairo.cairo_paint_with_alpha(self._pointer, alpha)
        self._check_status()

    def mask(self, pattern):
        """A drawing operator that paints the current source
        using the alpha channel of :obj:`pattern` as a mask.
        (Opaque areas of :obj:`pattern` are painted with the source,
        transparent areas are not painted.)

        :param pattern: A :class:`Pattern` object.

        """
        cairo.cairo_mask(self._pointer, pattern._pointer)
        self._check_status()

    def mask_surface(self, surface, surface_x=0, surface_y=0):
        """A drawing operator that paints the current source
        using the alpha channel of :obj:`surface` as a mask.
        (Opaque areas of :obj:`surface` are painted with the source,
        transparent areas are not painted.)

        :param pattern: A :class:`Surface` object.
        :param surface_x: X coordinate at which to place the origin of surface.
        :param surface_y: Y coordinate at which to place the origin of surface.
        :type surface_x: float
        :type surface_y: float

        """
        cairo.cairo_mask_surface(
            self._pointer, surface._pointer, surface_x, surface_y)
        self._check_status()

    def fill(self):
        """A drawing operator that fills the current path
        according to the current fill rule,
        (each sub-path is implicitly closed before being filled).
        After :meth:`fill`,
        the current path will be cleared from the cairo context.

        See :meth:`set_fill_rule` and :meth:`fill_preserve`.

        """
        cairo.cairo_fill(self._pointer)
        self._check_status()

    def fill_preserve(self):
        """A drawing operator that fills the current path
        according to the current fill rule,
        (each sub-path is implicitly closed before being filled).
        Unlike :meth:`fill`,
        :meth:`fill_preserve` preserves the path within the cairo context.

        See :meth:`set_fill_rule` and :meth:`fill`.

        """
        cairo.cairo_fill_preserve(self._pointer)
        self._check_status()

    def fill_extents(self):
        """Computes a bounding box in user-space coordinates
        covering the area that would be affected, (the "inked" area),
        by a :meth:`fill` operation given the current path and fill parameters.
        If the current path is empty,
        returns an empty rectangle ``(0, 0, 0, 0)``.
        Surface dimensions and clipping are not taken into account.

        Contrast with :meth:`path_extents` which is similar,
        but returns non-zero extents for some paths with no inked area,
        (such as a simple line segment).

        Note that :meth:`fill_extents` must necessarily do more work
        to compute the precise inked areas in light of the fill rule,
        so :meth:`path_extents` may be more desirable for sake of performance
        if the non-inked path extents are desired.

        See :meth:`fill`, :meth:`set_fill_rule` and :meth:`fill_preserve`.

        :return:
            A ``(x1, y1, x2, y2)`` tuple of floats:
            the left, top, right and bottom of the resulting extents,
            respectively.

        """
        extents = ffi.new('double[4]')
        cairo.cairo_fill_extents(
            self._pointer, extents + 0, extents + 1, extents + 2, extents + 3)
        self._check_status()
        return tuple(extents)

    def in_fill(self, x, y):
        """Tests whether the given point is inside the area
        that would be affected by a :meth:`fill` operation
        given the current path and filling parameters.
        Surface dimensions and clipping are not taken into account.

        See :meth:`fill`, :meth:`set_fill_rule` and :meth:`fill_preserve`.

        :param x: X coordinate of the point to test
        :param y: Y coordinate of the point to test
        :type x: float
        :type y: float
        :returns: A boolean.

        """
        return bool(cairo.cairo_in_fill(self._pointer, x, y))

    def stroke(self):
        """A drawing operator that strokes the current path
        according to the current line width, line join, line cap,
        and dash settings.
        After :meth:`stroke`,
        the current path will be cleared from the cairo context.
        See :meth:`set_line_width`, :meth:`set_line_join`,
        :meth:`set_line_cap`, :meth:`set_dash`, and :meth:`stroke_preserve`.

        Note: Degenerate segments and sub-paths are treated specially
        and provide a useful result.
        These can result in two different situations:

        1. Zero-length "on" segments set in :meth:`set_dash`.
           If the cap style is :obj:`ROUND <LINE_CAP_ROUND>`
           or :obj:`SQUARE <LINE_CAP_SQUARE>`
           then these segments will be drawn
           as circular dots or squares respectively.
           In the case of :obj:`SQUARE <LINE_CAP_SQUARE>`,
           the orientation of the squares is determined
           by the direction of the underlying path.
        2. A sub-path created by :meth:`move_to` followed
           by either a :meth:`close_path`
           or one or more calls to :meth:`line_to`
           to the same coordinate as the :meth:`move_to`.
           If the cap style is :obj:`ROUND <LINE_CAP_ROUND>`
           then these sub-paths will be drawn as circular dots.
           Note that in the case of :obj:`SQUARE <LINE_CAP_SQUARE>`
           a degenerate sub-path will not be drawn at all,
           (since the correct orientation is indeterminate).

        In no case will a cap style of :obj:`BUTT <LINE_CAP_BUTT>`
        cause anything to be drawn
        in the case of either degenerate segments or sub-paths.

        """
        cairo.cairo_stroke(self._pointer)
        self._check_status()

    def stroke_preserve(self):
        """A drawing operator that strokes the current path
        according to the current line width, line join, line cap,
        and dash settings.
        Unlike :meth:`stroke`,
        :meth:`stroke_preserve` preserves the path within the cairo context.
        See :meth:`set_line_width`, :meth:`set_line_join`,
        :meth:`set_line_cap`, :meth:`set_dash`, and :meth:`stroke`.

        """
        cairo.cairo_stroke_preserve(self._pointer)
        self._check_status()

    def stroke_extents(self):
        """Computes a bounding box in user-space coordinates
        covering the area that would be affected, (the "inked" area),
        by a :meth:`stroke` operation given the current path
        and stroke parameters.
        If the current path is empty,
        returns an empty rectangle ``(0, 0, 0, 0)``.
        Surface dimensions and clipping are not taken into account.

        Note that if the line width is set to exactly zero,
        then :meth:`stroke_extents` will return an empty rectangle.
        Contrast with :meth:`path_extents`
        which can be used to compute the non-empty bounds
        as the line width approaches zero.

        Note that :meth:`stroke_extents` must necessarily do more work
        to compute the precise inked areas in light of the stroke parameters,
        so :meth:`path_extents` may be more desirable for sake of performance
        if the non-inked path extents are desired.

        See :meth:`stroke`, :meth:`set_line_width`, :meth:`set_line_join`,
        :meth:`set_line_cap`, :meth:`set_dash`, and :meth:`stroke_preserve`.

        :return:
            A ``(x1, y1, x2, y2)`` tuple of floats:
            the left, top, right and bottom of the resulting extents,
            respectively.

        """
        extents = ffi.new('double[4]')
        cairo.cairo_stroke_extents(
            self._pointer, extents + 0, extents + 1, extents + 2, extents + 3)
        self._check_status()
        return tuple(extents)

    def in_stroke(self, x, y):
        """Tests whether the given point is inside the area
        that would be affected by a :meth:`stroke` operation
        given the current path and stroking parameters.
        Surface dimensions and clipping are not taken into account.

        See :meth:`stroke`, :meth:`set_line_width`, :meth:`set_line_join`,
        :meth:`set_line_cap`, :meth:`set_dash`, and :meth:`stroke_preserve`.

        :param x: X coordinate of the point to test
        :param y: Y coordinate of the point to test
        :type x: float
        :type y: float
        :returns: A boolean.

        """
        return bool(cairo.cairo_in_stroke(self._pointer, x, y))

    def clip(self):
        """Establishes a new clip region
        by intersecting the current clip region
        with the current path as it would be filled by :meth:`fill`
        and according to the current fill rule (see :meth:`set_fill_rule`).

        After :meth:`clip`,
        the current path will be cleared from the cairo context.

        The current clip region affects all drawing operations
        by effectively masking out any changes to the surface
        that are outside the current clip region.

        Calling :meth:`clip` can only make the clip region smaller,
        never larger.
        But the current clip is part of the graphics state,
        so a temporary restriction of the clip region can be achieved
        by calling :meth:`clip` within a :meth:`save` / :meth:`restore` pair.
        The only other means of increasing the size of the clip region
        is :meth:`reset_clip`.

        """
        cairo.cairo_clip(self._pointer)
        self._check_status()

    def clip_preserve(self):
        """Establishes a new clip region
        by intersecting the current clip region
        with the current path as it would be filled by :meth:`fill`
        and according to the current fill rule (see :meth:`set_fill_rule`).

        Unlike :meth:`clip`,
        :meth:`clip_preserve` preserves the path within the cairo context.

        The current clip region affects all drawing operations
        by effectively masking out any changes to the surface
        that are outside the current clip region.

        Calling :meth:`clip_preserve` can only make the clip region smaller,
        never larger.
        But the current clip is part of the graphics state,
        so a temporary restriction of the clip region can be achieved
        by calling :meth:`clip_preserve`
        within a :meth:`save` / :meth:`restore` pair.
        The only other means of increasing the size of the clip region
        is :meth:`reset_clip`.

        """
        cairo.cairo_clip_preserve(self._pointer)
        self._check_status()

    def clip_extents(self):
        """Computes a bounding box in user coordinates
        covering the area inside the current clip.

        :return:
            A ``(x1, y1, x2, y2)`` tuple of floats:
            the left, top, right and bottom of the resulting extents,
            respectively.

        """
        extents = ffi.new('double[4]')
        cairo.cairo_clip_extents(
            self._pointer, extents + 0, extents + 1, extents + 2, extents + 3)
        self._check_status()
        return tuple(extents)

    def copy_clip_rectangle_list(self):
        """Return the current clip region as a list of rectangles
        in user coordinates.

        :return:
            A list of rectangles,
            as ``(x, y, width, height)`` tuples of floats.
        :raises:
            :exc:`CairoError`
            if  the clip region cannot be represented as a list
            of user-space rectangles.

        """
        rectangle_list = cairo.cairo_copy_clip_rectangle_list(self._pointer)
        _check_status(rectangle_list.status)
        rectangles = rectangle_list.rectangles
        result = []
        for i in xrange(rectangle_list.num_rectangles):
            rect = rectangles[i]
            result.append((rect.x, rect.y, rect.width, rect.height))
        cairo.cairo_rectangle_list_destroy(rectangle_list)
        return result

    def in_clip(self, x, y):
        """Tests whether the given point is inside the area
        that would be visible through the current clip,
        i.e. the area that would be filled by a :meth:`paint` operation.

        See :meth:`clip`, and :meth:`clip_preserve`.

        :param x: X coordinate of the point to test
        :param y: Y coordinate of the point to test
        :type x: float
        :type y: float
        :returns: A boolean.

        *New in cairo 1.10.*

        """
        return bool(cairo.cairo_in_clip(self._pointer, x, y))

    def reset_clip(self):
        """Reset the current clip region to its original, unrestricted state.
        That is, set the clip region to an infinitely large shape
        containing the target surface.
        Equivalently, if infinity is too hard to grasp,
        one can imagine the clip region being reset
        to the exact bounds of the target surface.

        Note that code meant to be reusable
        should not call :meth:`reset_clip`
        as it will cause results unexpected by higher-level code
        which calls :meth:`clip`.
        Consider using :meth:`cairo` and :meth:`restore` around :meth:`clip`
        as a more robust means of temporarily restricting the clip region.

        """
        cairo.cairo_reset_clip(self._pointer)
        self._check_status()

    ##
    ##  Fonts
    ##

    def select_font_face(self, family='', slant='NORMAL', weight='NORMAL'):
        """Selects a family and style of font from a simplified description
        as a family name, slant and weight.

        .. note::

            The :meth:`select_font_face` method is part of
            what the cairo designers call the "toy" text API.
            It is convenient for short demos and simple programs,
            but it is not expected to be adequate
            for serious text-using applications.
            See :ref:`fonts` for details.

        Cairo provides no operation to list available family names
        on the system (this is a "toy", remember),
        but the standard CSS2 generic family names,
        (``"serif"``, ``"sans-serif"``, ``"cursive"``, ``"fantasy"``,
        ``"monospace"``),
        are likely to work as expected.

        If family starts with the string ``"cairo:"``,
        or if no native font backends are compiled in,
        cairo will use an internal font family.
        The internal font family recognizes many modifiers
        in the family string,
        most notably, it recognizes the string ``"monospace"``.
        That is, the family name ``"cairo:monospace"``
        will use the monospace version of the internal font family.

        If text is drawn without a call to :meth:`select_font_face`,
        (nor :meth:`set_font_face` nor :meth:`set_scaled_font`),
        the default family is platform-specific,
        but is essentially ``"sans-serif"``.
        Default slant is :obj:`NORMAL <FONT_SLANT_NORMAL>`,
        and default weight is :obj:`NORMAL <FONT_WEIGHT_NORMAL>`.

        This method is equivalent to a call to :class:`ToyFontFace`
        followed by :meth:`set_font_face`.

        """
        cairo.cairo_select_font_face(
            self._pointer, _encode_string(family), slant, weight)
        self._check_status()

    def set_font_face(self, font_face):
        """Replaces the current font face with :obj:`font_face`.

        :param font_face:
            A :class:`FontFace` object,
            or :obj:`None` to restore the default font.

        """
        font_face = font_face._pointer if font_face is not None else ffi.NULL
        cairo.cairo_set_font_face(self._pointer, font_face)
        self._check_status()

    def get_font_face(self):
        """Return the current font face.

        :param font_face:
            A new :class:`FontFace` object
            wrapping an existing cairo object.

        """
        return FontFace._from_pointer(
            cairo.cairo_get_font_face(self._pointer), incref=True)

    def set_font_size(self, size):
        """Sets the current font matrix to a scale by a factor of :obj:`size`,
        replacing any font matrix previously set with :meth:`set_font_size`
        or :meth:`set_font_matrix`.
        This results in a font size of size user space units.
        (More precisely, this matrix will result in the font's
        em-square being a size by size square in user space.)

        If text is drawn without a call to :meth:`set_font_size`,
        (nor :meth:`set_font_matrix` nor :meth:`set_scaled_font`),
        the default font size is 10.0.

        :param size: The new font size, in user space units
        :type size: float

        """
        cairo.cairo_set_font_size(self._pointer, size)
        self._check_status()

    def set_font_matrix(self, matrix):
        """Sets the current font matrix to :obj:`matrix`.
        The font matrix gives a transformation
        from the design space of the font
        (in this space, the em-square is 1 unit by 1 unit)
        to user space.
        Normally, a simple scale is used (see :meth:`set_font_size`),
        but a more complex font matrix can be used
        to shear the font or stretch it unequally along the two axes

        :param matrix:
            A :class:`Matrix`
            describing a transform to be applied to the current font.

        """
        cairo.cairo_set_font_matrix(self._pointer, matrix._pointer)
        self._check_status()

    def get_font_matrix(self):
        """Copies the current font matrix. See :meth:`set_font_matrix`.

        :returns: A new :class:`Matrix`.

        """
        matrix = Matrix()
        cairo.cairo_get_font_matrix(self._pointer, matrix._pointer)
        self._check_status()
        return matrix

    def set_font_options(self, font_options):
        """Sets a set of custom font rendering options.
        Rendering options are derived by merging these options
        with the options derived from underlying surface;
        if the value in options has a default value
        (like :obj:`ANTIALIAS_DEFAULT`),
        then the value from the surface is used.

        :param font_options: A :class:`FontOptions` object.

        """
        cairo.cairo_set_font_options(self._pointer, font_options._pointer)
        self._check_status()

    def get_font_options(self):
        """Retrieves font rendering options set via :meth:`set_font_options`.
        Note that the returned options do not include any options
        derived from the underlying surface;
        they are literally the options passed to :meth:`set_font_options`.

        :return: A new :class:`FontOptions` object.

        """
        font_options = FontOptions()
        cairo.cairo_get_font_options(self._pointer, font_options._pointer)
        return font_options

    def set_scaled_font(self, scaled_font):
        """Replaces the current font face, font matrix, and font options
        with those of :obj:`scaled_font`.
        Except for some translation, the current CTM of the context
        should be the same as that of the :obj:`scaled_font`,
        which can be accessed using :meth:`ScaledFont.get_ctm`.

        :param scaled_font: A :class:`ScaledFont` object.

        """
        cairo.cairo_set_scaled_font(self._pointer, scaled_font._pointer)
        self._check_status()

    def get_scaled_font(self):
        """Return the current scaled font.

        :return:
            A new :class:`ScaledFont` object,
            wrapping an existing cairo object.

        """
        return ScaledFont._from_pointer(
            cairo.cairo_get_scaled_font(self._pointer), incref=True)

    def font_extents(self):
        """Return the extents of the currently selected font.

        Values are given in the current user-space coordinate system.

        Because font metrics are in user-space coordinates, they are mostly,
        but not entirely, independent of the current transformation matrix.
        If you call :meth:`context.scale(2) <scale>`,
        text will be drawn twice as big,
        but the reported text extents will not be doubled.
        They will change slightly due to hinting
        (so you can't assume that metrics are independent
        of the transformation matrix),
        but otherwise will remain unchanged.

        :returns:
            A ``(ascent, descent, height, max_x_advance, max_y_advance)``
            tuple of floats.

        :obj:`ascent`
            The distance that the font extends above the baseline.
            Note that this is not always exactly equal to
            the maximum of the extents of all the glyphs in the font,
            but rather is picked to express the font designer's intent
            as to how the font should align with elements above it.
        :obj:`descent`
            The distance that the font extends below the baseline.
            This value is positive for typical fonts
            that include portions below the baseline.
            Note that this is not always exactly equal
            to the maximum of the extents of all the glyphs in the font,
            but rather is picked to express the font designer's intent
            as to how the font should align with elements below it.
        :obj:`height`
            The recommended vertical distance between baselines
            when setting consecutive lines of text with the font.
            This is greater than ``ascent + descent``
            by a quantity known as the line spacing or external leading.
            When space is at a premium, most fonts can be set
            with only a distance of ``ascent + descent`` between lines.
        :obj:`max_x_advance`
            The maximum distance in the X direction
            that the origin is advanced for any glyph in the font.
        :obj:`max_y_advance`
            The maximum distance in the Y direction
            that the origin is advanced for any glyph in the font.
            This will be zero for normal fonts used for horizontal writing.
            (The scripts of East Asia are sometimes written vertically.)

        """
        extents = ffi.new('cairo_font_extents_t *')
        cairo.cairo_font_extents(self._pointer, extents)
        self._check_status()
        # returning extents as is would be a nice API,
        # but return a tuple for compat with pycairo.
        return (
            extents.ascent, extents.descent, extents.height,
            extents.max_x_advance, extents.max_y_advance)

    ##
    ##  Text
    ##

    def text_extents(self, text):
        """Returns the extents for a string of text.

        The extents describe a user-space rectangle
        that encloses the "inked" portion of the text,
        (as it would be drawn by :meth:`show_text`).
        Additionally, the :obj:`x_advance` and :obj:`y_advance` values
        indicate the amount by which the current point would be advanced
        by :meth:`show_text`.

        Note that whitespace characters do not directly contribute
        to the size of the rectangle (:obj:`width` and :obj:`height`).
        They do contribute indirectly by changing the position
        of non-whitespace characters.
        In particular, trailing whitespace characters are likely
        to not affect the size of the rectangle,
        though they will affect the x_advance and y_advance values.

        Because text extents are in user-space coordinates,
        they are mostly, but not entirely,
        independent of the current transformation matrix.
        If you call :meth:`context.scale(2) <scale>`,
        text will be drawn twice as big,
        but the reported text extents will not be doubled.
        They will change slightly due to hinting
        (so you can't assume that metrics are independent
        of the transformation matrix),
        but otherwise will remain unchanged.

        :param text: The text to measure, as an Unicode or UTF-8 string.
        :returns:
            A ``(x_bearing, y_bearing, width, height, x_advance, y_advance)``
            tuple of floats.

        :obj:`x_bearing`
            The horizontal distance
            from the origin to the leftmost part of the glyphs as drawn.
            Positive if the glyphs lie entirely to the right of the origin.

        :obj:`y_bearing`
            The vertical distance
            from the origin to the topmost part of the glyphs as drawn.
            Positive only if the glyphs lie completely below the origin;
            will usually be negative.

        :obj:`width`
            Width of the glyphs as drawn.

        :obj:`height`
            Height of the glyphs as drawn.

        :obj:`x_advance`
            Distance to advance in the X direction
            after drawing these glyphs.

        :obj:`y_advance`
            Distance to advance in the Y direction
            after drawing these glyphs.
            Will typically be zero except for vertical text layout
            as found in East-Asian languages.

        """
        extents = ffi.new('cairo_text_extents_t *')
        cairo.cairo_text_extents(self._pointer, _encode_string(text), extents)
        self._check_status()
        # returning extents as is would be a nice API,
        # but return a tuple for compat with pycairo.
        return (
            extents.x_bearing, extents.y_bearing,
            extents.width, extents.height,
            extents.x_advance, extents.y_advance)

    def glyph_extents(self, glyphs):
        """Returns the extents for a list of glyphs.

        The extents describe a user-space rectangle
        that encloses the "inked" portion of the glyphs,
        (as it would be drawn by :meth:`show_glyphs`).
        Additionally, the :obj:`x_advance` and :obj:`y_advance` values
        indicate the amount by which the current point would be advanced
        by :meth:`show_glyphs`.

        :param glyphs:
            A list of glyphs.
            See :meth:`show_text_glyphs` for the data structure.
        :returns:
            A ``(x_bearing, y_bearing, width, height, x_advance, y_advance)``
            tuple of floats.
            See :meth:`text_extents` for details.

        """
        glyphs = ffi.new('cairo_glyph_t[]', glyphs)
        extents = ffi.new('cairo_text_extents_t *')
        cairo.cairo_glyph_extents(
            self._pointer, glyphs, len(glyphs), extents)
        self._check_status()
        return (
            extents.x_bearing, extents.y_bearing,
            extents.width, extents.height,
            extents.x_advance, extents.y_advance)

    def show_text(self, text):
        """A drawing operator that generates the shape from a string text,
        rendered according to the current
        font :meth:`face <set_font_face>`,
        font :meth:`size <set_font_size>`
        (font :meth:`matrix <set_font_matrix>`),
        and font :meth:`options <set_font_options>`.

        This method first computes a set of glyphs for the string of text.
        The first glyph is placed so that its origin is at the current point.
        The origin of each subsequent glyph
        is offset from that of the previous glyph
        by the advance values of the previous glyph.

        After this call the current point is moved
        to the origin of where the next glyph would be placed
        in this same progression.
        That is, the current point will be at
        the origin of the final glyph offset by its advance values.
        This allows for easy display of a single logical string
        with multiple calls to :meth:`show_text`.

        :param text: The text to show, as an Unicode or UTF-8 string.

        .. note::

            This method is part of
            what the cairo designers call the "toy" text API.
            It is convenient for short demos and simple programs,
            but it is not expected to be adequate
            for serious text-using applications.
            See :ref:`fonts` for details
            and :meth:`show_glyphs` for the "real" text display API in cairo.

        """
        cairo.cairo_show_text(self._pointer, _encode_string(text))
        self._check_status()

    def show_glyphs(self, glyphs):
        """A drawing operator that generates the shape from a list of glyphs,
        rendered according to the current
        font :meth:`face <set_font_face>`,
        font :meth:`size <set_font_size>`
        (font :meth:`matrix <set_font_matrix>`),
        and font :meth:`options <set_font_options>`.

        :param glyphs:
            The glyphs to show.
            See :meth:`show_text_glyphs` for the data structure.

        """
        glyphs = ffi.new('cairo_glyph_t[]', glyphs)
        cairo.cairo_show_glyphs(self._pointer, glyphs, len(glyphs))
        self._check_status()

    def show_text_glyphs(self, text, glyphs, clusters, clusters_backwards):
        """This operation has rendering effects similar to :meth:`show_glyphs`
        but, if the target surface supports it
        (see :meth:`Surface.has_show_text_glyphs`),
        uses the provided text and cluster mapping
        to embed the text for the glyphs shown in the output.
        If the target does not support the extended attributes,
        this method acts like the basic :meth:`show_glyphs`
        as if it had been passed :obj:`glyphs`.

        The mapping between :obj:`text` and :obj:`glyphs`
        is provided by an list of clusters.
        Each cluster covers a number of UTF-8 text bytes and glyphs,
        and neighboring clusters cover neighboring areas
        of :obj:`text` and :obj:`glyphs`.
        The clusters should collectively cover :obj:`text` and :obj:`glyphs`
        in entirety.

        :param text:
            The text to show, as an Unicode or UTF-8 string.
            Because of how :obj:`clusters` work,
            using UTF-8 bytes might be more convenient.
        :param glyphs:
            A list of glyphs.
            Each glyph is a ``(glyph_id, x, y)`` tuple.
            :obj:`glyph_id` is an opaque integer.
            Its exact interpretation depends on the font technology being used.
            :obj:`x` and :obj:`y` are the float offsets
            in the X and Y direction
            between the origin used for drawing or measuring the string
            and the origin of this glyph.
            Note that the offsets are not cumulative.
            When drawing or measuring text,
            each glyph is individually positioned
            with respect to the overall origin.
        :param clusters:
            A list of clusters.
            A text cluster is a minimal mapping of some glyphs
            corresponding to some UTF-8 text,
            represented as a ``(num_bytes, num_glyphs)`` tuple of integers,
            the number of UTF-8 bytes and glyphs covered by the cluster.
            For a cluster to be valid,
            both :obj:`num_bytes` and :obj:`num_glyphs` should be non-negative,
            and at least one should be non-zero.
            Note that clusters with zero glyphs
            are not as well supported as normal clusters.
            For example, PDF rendering applications
            typically ignore those clusters when PDF text is being selected.
        :type clusters_backwards: bool
        :param clusters_backwards:
            The first cluster always covers bytes
            from the beginning of :obj:`text`.
            If :obj:`clusters_backwards` is false,
            the first cluster also covers the beginning of :obj:`glyphs`,
            otherwise it covers the end of the :obj:`glyphs` list
            and following clusters move backward.

        """
        glyphs = ffi.new('cairo_glyph_t[]', glyphs)
        clusters = ffi.new('cairo_text_cluster_t[]', clusters)
        flags = 'BACKWARDS' if clusters_backwards else 0
        cairo.cairo_show_text_glyphs(
            self._pointer, _encode_string(text), -1,
            glyphs, len(glyphs), clusters, len(clusters), flags)
        self._check_status()

    ##
    ##  Pages
    ##

    def show_page(self):
        """Emits and clears the current page
        for backends that support multiple pages.
        Use :meth:`copy_page` if you don't want to clear the page.

        This is a convenience method
        that simply calls :meth:`Surface.show_page`
        on the context’s target.

        """
        cairo.cairo_show_page(self._pointer)
        self._check_status()

    def copy_page(self):
        """Emits the current page  for backends that support multiple pages,
        but doesn't clear it,
        so the contents of the current page will be retained
        for the next page too.
        Use :meth:`show_page` if you want to clear the page.

        This is a convenience method
        that simply calls :meth:`Surface.copy_page`
        on the context’s target.

        """
        cairo.cairo_copy_page(self._pointer)
        self._check_status()
