"""This module defines the basic functionality for collision, as well
as the base classes that compose an abstract interface to the library
developers choose to use.

Both :class:`Space` and :class:`Geom` (parent class of :class:`Ray`,
:class:`Trimesh`, :class:`Box`, :class:`Sphere`, :class:`Plane`, etc)
wrap the corresponding "native" object that the adapted library uses,
assigned to private attribute ``_inner_object``. To access (not set) it,
these classes have public property ``inner_object``.

This module also contains the auxiliary classes :class:`RayContactData` and
:class:`NearCallbackArgs`.


The following are common abbreviations present both in code and documentation:

* geom: geometry object
* trimesh: triangular mesh

"""
from abc import ABCMeta, abstractmethod
import logging

from ... import exceptions as exc
from ...lib.pydispatch import dispatcher

from . import signals


logger = logging.getLogger(__name__)

#==============================================================================
# Environment
#==============================================================================


class Engine(object):

	"""Collision engine abstract base class.

	"""

	__metaclass__ = ABCMeta

	@classmethod
	def calc_collision(cls, geom1, geom2):
		"""Calculate information of the collision between these geoms.

		Check if ``geom1`` and ``geom2`` actually collide and
		create a list of contact data objects if they do.

		:param geom1:
		:type geom1: type of :attr:`Geom.inner_object`
		:param geom2:
		:type geom2: type of :attr:`Geom.inner_object`
		:return: contacts information
		:rtype: list of contact data objects

		"""
		# Raising an exception efectively makes this definition be that of
		# an abstract method (i.e. calling it directly raises an exception),
		# except that it not requires the subclass to implement it if it is
		# not used. We would like to use @classmethod AND @abstractmethod,
		# but until Python 3.3 that doesn't work correctly.
		# http://docs.python.org/3/library/abc.html
		raise NotImplementedError()

	@classmethod
	def near_callback(cls, args, geom1, geom2):
		"""Handle possible collision between ``geom1`` and ``geom2``.

		The responsible for determining if there is an actual collision
		is :meth:`calc_collision`, which will return a list of contact
		data objects.

		That information is passed to either
		:meth:`process_collision_contacts` or
		:meth:`process_ray_collision_contacts`, depending on whether
		``geom1`` or ``geom2`` is a ray or not. It's an unhandled
		case that both geoms were rays.

		This function is usually the callback function for
		:meth:`Space.collide`, although it will probably be handed over to
		the inner object of a :class:`Space` subclass.

		:param args: data structure wrapping the objects necessary to
			process the collision
		:type args: :class:`NearCallbackArgs`
		:param geom1:
		:type geom1: type of :attr:`Geom.inner_object`
		:param geom2:
		:type geom2: type of :attr:`Geom.inner_object`

		"""
		# Don't continue if the geoms are connected and
		# that case should be ignored.
		if args.ignore_connected and cls.are_geoms_connected(geom1, geom2):
			return

		# Ray's special case.
		# Collision between a ray and another geom must be handled in a special
		# way because no contact joints are to be generated, there is no
		# "real" collision.
		#   1. Check if any of both geoms is a ray.
		#   2. If both are, that's an error.
		#   3. If they are not, all is fine.
		#   4. If one is a ray, assign it to a special variable so the special
		#      function is called with parameters in the correct order.
		ray_geom = None
		other_geom = None

		if cls.is_ray(geom1):
			if cls.is_ray(geom2):
				logger.error("Weird, ODE says two rays may collide. "
				             "That case is not handled.")  # TODO: better msg
				return
			ray_geom = geom1
			other_geom = geom2
		elif cls.is_ray(geom2):
			ray_geom = geom2
			other_geom = geom1

		# calculate collision contacts data
		contacts = cls.calc_collision(geom1, geom2)
		if ray_geom is None:
			cls.process_collision_contacts(args, geom1, geom2, contacts)
		else:
			cls.process_ray_collision_contacts(ray_geom, other_geom, contacts)

	@classmethod
	def process_collision_contacts(cls, args, geom1, geom2, contacts):
		"""Process ``contacts`` of a collision between ``geom1`` and ``geom2``.

		This method should create movement constraints for the bodies
		attached to the geoms. This is necessary for the simulation to
		prevent bodies' volumes from penetrating each other, making them
		really collide (i.e. exert mutually opposing forces).

		.. warning::
		   Neither ``geom1`` nor ``geom2`` can be rays. If one of them is,
		   use method :meth:`process_ray_collision_contacts`.

		:param args:
		:type args: :class:`NearCallbackArgs`
		:param geom1:
		:type geom1: type of :attr:`Geom.inner_object`
		:param geom2:
		:type geom2: type of :attr:`Geom.inner_object`
		:param contacts: collision data returned by :meth:`calc_collision`
		:type contacts: list of contact data objects

		"""
		# Like :meth:`calc_collision`, this is an @abtractclassmethod too.
		raise NotImplementedError()

	@classmethod
	def process_ray_collision_contacts(cls, ray, other_geom, contacts):
		"""Process special case of collision between a ray and a regular geom.

		.. seealso::
		   For regular geoms collision, see :meth:`process_collision_contacts`.

		Since rays have no attached body, they can't "really" collide
		with other geoms. However, they do intersect, which is of
		interest to non-physical aspects of the simulation. A common
		use case is that of laser distance sensors.

		.. warning::
		   Collision between two rays is a singularity and should never happen.

		:param ray:
		:type ray: type of :attr:`Ray.inner_object`
		:param other_geom:
		:type other_geom: type of :attr:`Geom.inner_object`
		:param contacts: collision data returned by :meth:`calc_collision`
		:type contacts: list of contact data objects

		"""
		# Like :meth:`calc_collision`, this is an @abtractclassmethod too.
		raise NotImplementedError()

	@classmethod
	def are_geoms_connected(cls, geom1, geom2):
		"""Return whether ``geom1``'s body is connected to ``geom2``'s body.

		The *connection* is checked as whether geoms bodies are connected
		through a joint or not.

		:param geom1:
		:type geom1: type of :attr:`Geom.inner_object`
		:param geom2:
		:type geom2: type of :attr:`Geom.inner_object`
		:return: True if geoms' bodies are connected; False otherwise
		:rtype: bool

		"""
		# Like :meth:`calc_collision`, this is an @abtractclassmethod too.
		raise NotImplementedError()

	@classmethod
	def is_ray(cls, geom):
		"""Return whether ``geom`` is a ray-like object or not.

		:param geom:
		:type geom: type of :attr:`Geom.inner_object`
		:return: True if ``geom`` is an instance of the class representing a
			ray in the adapted library
		:rtype: bool

		"""
		# Like :meth:`calc_collision`, this is an @abtractclassmethod too.
		raise NotImplementedError()


class Space(object):

	"""Collision space abstract base class.

	This class wraps the corresponding "native" object the
	adapted-to library (e.g. ODE) uses, assigned to
	:attr:`_inner_object`.

	Subclasses must implement these methods:

	* :meth:`__init__`
	* :meth:`collide`

	"""

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self):
		self._inner_object = None

	@property
	def inner_object(self):
		return self._inner_object

	@abstractmethod
	def collide(self, args, callback):
		pass

#==============================================================================
# Parents
#==============================================================================


class Geom(object):

	"""Geometry object encapsulation.

	This class wraps the corresponding "native" object the
	adapted-to library (e.g. ODE) uses, assigned to
	:attr:`_inner_object`.

	Subclasses must implement these methods:

	* :meth:`__init__`
	* :meth:`attach_body`
	* :meth:`get_position`, :meth:`set_position`
	* :meth:`get_rotation`, :meth:`set_rotation`

	"""

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self):
		self._inner_object = None
		self._attached_body = None

	@abstractmethod
	def attach_body(self, body):
		self._attached_body = body

	#==========================================================================
	# Getters and setters
	#==========================================================================
	@property
	def inner_object(self):
		return self._inner_object

	def get_attached_body(self):
		return self._attached_body

	@abstractmethod
	def get_position(self):
		"""Get the position of the geom.

		:return: position
		:rtype: 3-sequence of floats

		"""
		pass

	@abstractmethod
	def get_rotation(self):
		"""Get the orientation of the geom.

		:return: rotation matrix
		:rtype: 9-sequence of floats

		"""
		pass

	@abstractmethod
	def set_position(self, pos):
		"""Set the position of the geom.

		:param pos: position
		:type pos: 3-sequence of floats

		"""
		pass

	@abstractmethod
	def set_rotation(self, rot):
		"""Set the orientation of the geom.

		:param rot: rotation matrix
		:type rot: 9-sequence of floats

		"""
		pass


class BasicShape(Geom):

	"""Abstract class from whom every solid object's shape derive"""

	__metaclass__ = ABCMeta

#==============================================================================
# Other shapes
#==============================================================================


class Plane(BasicShape):

	"""Plane, different from a box"""

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, space, normal, dist):
		super(Plane, self).__init__()


class Ray(Geom):

	"""
	Ray aligned along the Z-axis by default.
	"A ray is different from all the other geom classes in that it does not
	represent a solid object. It is an infinitely thin line that starts from
	the geom's position and	extends in the direction of the geom's local
	Z-axis." (ODE Wiki Manual)

	"""

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, space, length):
		super(Ray, self).__init__()
		self._last_contact = None
		self._closer_contact = None

	@abstractmethod
	def get_length(self):
		pass

	@abstractmethod
	def set_length(self, length):
		pass

	def get_last_contact(self):
		"""Return the contact object corresponding to the last collision of
		the ray with another geom. Note than in each simulation step, several
		collisions may occur, one for each intersection geom (in ODE).
		The object returned may or may not be the same returned by
		`get_closer_contact`.

		"""
		return self._last_contact

	def get_closer_contact(self):
		"""Return the contact object corresponding to the collision closest to
		the ray's origin.

		It may or may not be the same object returned by `get_last_contact`.

		"""
		return self._closer_contact

	def set_last_contact(self, last_contact):
		"""Set the contact data of ray's last collision. It also
		checks if `last_contact` is closer than the previously existing one.
		The result can be obtained with the `get_closer_contact` method.
		"""
		dispatcher.send(signals.RAY_PRE_SET_LAST_CONTACT, sender=self)
		if self._last_contact is None:
			self._closer_contact = last_contact
		else:
			if self._last_contact.depth > last_contact.depth:
				self._closer_contact = last_contact
		self._last_contact = last_contact
		dispatcher.send(signals.RAY_POST_SET_LAST_CONTACT, sender=self)

	def clear_last_contact(self):
		dispatcher.send(signals.RAY_PRE_CLEAR_LAST_CONTACT, sender=self)
		self._last_contact = None
		dispatcher.send(signals.RAY_POST_CLEAR_LAST_CONTACT, sender=self)

	def clear_closer_contact(self):
		dispatcher.send(signals.RAY_PRE_CLEAR_CLOSER_CONTACT, sender=self)
		self._closer_contact = None
		dispatcher.send(signals.RAY_POST_CLEAR_CLOSER_CONTACT, sender=self)

	def clear_contacts(self):
		self.clear_last_contact()
		self.clear_closer_contact()


class Trimesh(Geom):

	"""A triangular mesh i.e. a surface composed of triangular faces.

	.. note::
	   Note that a trimesh need not be closed. For example, it could be
	   used to model the ground surface.

	Its geometry is defined by two attributes: :attr:`vertices` and
	:attr:`faces`, both list of 3-tuple numbers. However, each tuple
	in :attr:`vertices` designates a 3D point in space whereas each tuple
	in :attr:`faces` is a group of indices referencing points in
	:attr:`vertices`.

	.. warning::
	   The order of vertices indices for each face **does** matter.

	Example::

		vertices = [(0, 0.0, 0), (0, 0.0, 1), (0, 0.0, 2), (0, 0.0, 3),
		            (1, 0.0, 0), (1, 0.0, 1), (1, 0.0, 2), (1, 0.0, 3)]

		faces = [(0, 1, 4), (1, 5, 4), (1, 6, 5),
		         (1, 2, 6), (2, 3, 6), (3, 7, 6)]

	The, the first face is defined by points:
	``(0, 0.0, 0), (0, 0.0, 1), (1, 0.0, 0)``.
	With that order, the normal to the face is ``(0, 1.0, 0)`` i.e. the Y axis.
	The rationale to determining the *inwards* and *outwards* directions
	follows the well-known "right hand rule".

	"""

	@abstractmethod
	def __init__(self, space, vertices, faces):
		super(Trimesh, self).__init__()

	@staticmethod
	def swap_faces_indices(faces):
		"""Faces had to change their indices to work with ODE. With the initial
		get_faces, the normal to the triangle defined by the 3 vertices pointed
		(following the right-hand rule) downwards. Swapping the third with the
		first index, now the triangle normal pointed upwards."""

		new_faces = []
		for face in faces:
			new_faces.append((face[2], face[1], face[0]))
		return new_faces


class HeightfieldTrimesh(Trimesh):

	def __init__(self, space, size_x, size_z, vertices):
		faces = self.calc_faces(size_x, size_z)
		super(HeightfieldTrimesh, self).__init__(space, vertices, faces)

	@staticmethod
	def calc_faces(size_x, size_z):
		"""Return the faces for a horizontal grid of ``size_x`` by ``size_z``
		cells.

		Faces are triangular, so each is composed by 3 vertices. Consequently,
		each returned face is a length-3 sequence of the vertex indices.

		:param size_x: number of cells along the X axis
		:type size_x: positive int
		:param size_z: number of cells along the Z axis
		:type size_z: positive int
		:return: faces for a heightfield trimesh based in a horizontal grid of
			``size_x`` by ``size_z`` cells
		:rtype: list of 3-tuple of ints

		>>> HeightfieldTrimesh.calc_faces(2, 4)
		[(0, 1, 4), (1, 5, 4), (1, 6, 5), (1, 2, 6), (2, 3, 6), (3, 7, 6)]

		"""
		# index of each square is calculated because it is needed to define faces
		indices = []

		for x in range(size_x):
			indices_x = []
			for z in range(size_z):
				indices_x.insert(z, size_z * x + z)
			indices.insert(x, indices_x)

		# faces = [(1a,1b,1c), (2a,2b,2c), ...]
		faces = []

		for x in range(size_x - 1):
			for z in range(size_z - 1):

				zero = indices[x][z]			# top-left corner
				one = indices[x][z + 1]			# bottom-left
				two = indices[x + 1][z]			# top-right
				three = indices[x + 1][z + 1] 	# bottom-right

				# there are two face types for each square
				# contiguous squares must have different face types
				face_type = zero
				if size_z % 2 == 0:
					face_type += 1

				# there are 2 faces per square
				if face_type % 2 == 0:
					face1 = (zero, three, two)
					face2 = (zero, one, three)
				else:
					face1 = (zero, one, two)
					face2 = (one, three, two)

				faces.append(face1)
				faces.append(face2)

		return faces


class ConstantHeightfieldTrimesh(HeightfieldTrimesh):

	"""A trimesh that is a heightfield at constant level.

	.. note::
	   More than anything, this geom is for demonstration purposes,
	   because it could be easily replaced with a :class:`Plane`.

	"""

	def __init__(self, space, size_x, size_z, height):
		"""Constructor.

		:param space:
		:type space: :class:`Space`
		:param size_x: number of cells along the X axis
		:type size_x: positive int
		:param size_z: number of cells along the Z axis
		:type size_z: positive int
		:param height:
		:type height: float

		"""
		vertices = self.calc_vertices(size_x, size_z, height)
		super(ConstantHeightfieldTrimesh, self).__init__(
			space, size_x, size_z, vertices)

	@staticmethod
	def calc_vertices(size_x, size_z, height=0.0):
		"""Return the vertices of a horizontal grid of ``size_x`` by ``size_z``
		cells at a certain ``height``.

		:param size_x: number of cells along the X axis
		:type size_x: positive int
		:param size_z: number of cells along the Z axis
		:type size_z: positive int
		:param height:
		:type height: float

		>>> ConstantHeightfieldTrimesh.calc_vertices(2, 4)
		[(0, 0.0, 0), (0, 0.0, 1), (0, 0.0, 2), ..., (1, 0.0, 3)]

		"""
		verts = []
		for x in range(size_x):
			for z in range(size_z):
				verts.append((x, height, z))
		return verts

#==============================================================================
# Basic Shapes
#==============================================================================


class Box(BasicShape):
	"""Box shape, aligned along the X, Y and Z axii by default"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, space, size):
		super(Box, self).__init__()


class Sphere(BasicShape):
	"""Spherical shape"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, space, radius):
		super(Sphere, self).__init__()


class Capsule(BasicShape):
	"""Capsule shape, aligned along the Z-axis by default"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, space, length, radius):
		super(Capsule, self).__init__()


class Cylinder(BasicShape):
	"""Cylinder shape, aligned along the Z-axis by default"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, space, length, radius):
		super(Cylinder, self).__init__()


class Cone(BasicShape):
	"""Cone"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self):
		super(Cone, self).__init__()

#==============================================================================
# aux classes
#==============================================================================


class ContactGroup(object):

	"""Wrapper around a collection-like class storing contact data instances.

	What these instances are (attributes, behavior) is up to the
	implementation of the adpater.

	"""

	@abstractmethod
	def __init__(self):
		self._inner_object = None

	@abstractmethod
	def empty(self):
		"""Remove all the stored contact data instances."""
		pass

	@property
	def inner_object(self):
		return self._inner_object


class RayContactData(object):

	"""Data structure to save the contact information of a collision
	between :attr:`ray` and :attr:`shape`.

	All attributes are read-only (set at initialization).

	"""

	def __init__(self, ray=None, shape=None, pos=None, normal=None, depth=None):
		"""Constructor.

		:param ray:
		:type ray: the type of :class:`Ray` subclass' ``inner_object``
		:param shape:
		:type shape: the type of :class:`Geom` subclass' ``inner_object``
		:param pos: point at which the ray intersects the surface of the other
			shape/geom
		:type pos: 3-tuple of floats
		:param normal: vector normal to the surface of the other geom
			at the contact point
		:type normal: 3-tuple of floats
		:param depth: distance from the origin of the ray to the contact point
		:type depth: float

		"""
		self._ray = ray
		self._shape = shape
		self._position = pos
		self._normal = normal
		self._depth = depth

	@property
	def ray(self):
		return self._ray

	@property
	def shape(self):
		return self._shape

	@property
	def position(self):
		return self._position

	@property
	def normal(self):
		return self._normal

	@property
	def depth(self):
		return self._depth


class NearCallbackArgs(object):

	"""Data structure to save the args passed to
	:meth:`Engine.near_callback`.

	All attributes are read-only (set at initialization).

	"""

	def __init__(self, world=None, contact_group=None, ignore_connected=True):
		"""Constructor.

		:param world:
		:type world: :class:`.physics.base.World`
		:param contact_group:
		:type contact_group: :class:`ContactGroup`
		:param ignore_connected: whether to ignore collisions of geoms
			whose bodies are connected, or not
		:type ignore_connected: bool

		"""
		self._world = world
		self._contact_group = contact_group
		self._ignore_connected = ignore_connected

	@property
	def world(self):
		return self._world

	@property
	def contact_group(self):
		return self._contact_group

	@property
	def ignore_connected(self):
		return self._ignore_connected
