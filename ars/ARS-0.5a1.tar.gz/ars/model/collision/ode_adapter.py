"""Classes and functions to interface with the collision library
included in ODE.

"""
from abc import ABCMeta
import logging

import ode

from . import base
from . import ode_objects_factories
from .base import NearCallbackArgs


logger = logging.getLogger(__name__)

#==============================================================================
# Environment
#==============================================================================


class Engine(base.Engine):

	"""Adapter to the ODE collision engine."""

	@classmethod
	def calc_collision(cls, geom1, geom2):
		"""Calculate information of the collision between these geoms.

		Check if ``geom1`` and ``geom2`` actually collide and
		create a list of contact data objects if they do.

		:param geom1:
		:type geom1: :class:`ode.GeomObject`
		:param geom2:
		:type geom2: :class:`ode.GeomObject`
		:return: contacts information
		:rtype: list of :class:`ode.Contact`

		"""
		return ode.collide(geom1, geom2)

	@classmethod
	def are_geoms_connected(cls, geom1, geom2):
		"""(see parent method)

		:param geom1:
		:type geom1: :class:`ode.GeomObject`
		:param geom2:
		:type geom2: :class:`ode.GeomObject`

		"""
		return ode.areConnected(geom1.getBody(), geom2.getBody())

	@classmethod
	def is_ray(cls, geom):
		"""Return whether ``geom`` is a :class:`ode.GeomRay` object or not.

		:param geom:
		:type geom: :class:`ode.GeomObject`
		:return: True if ``geom`` is an instance of :class:`ode.GeomRay`
		:rtype: bool

		"""
		return isinstance(geom, ode.GeomRay)

	@classmethod
	def process_collision_contacts(cls, args, geom1, geom2, contacts):
		"""(see parent :meth:`.base.Engine.process_collision_contacts`)

		:param geom1:
		:type geom1: :class:`ode.GeomObject`
		:param geom2:
		:type geom2: :class:`ode.GeomObject`
		:param contacts:
		:type contacts: list of :class:`ode.Contact`

		"""
		# Contact object parameters:
		# -bounce: default=0.2
		# -mu: default=500. Very slippery 0-5, normal 50-500, very sticky 5000
		contact_bounce = 0.2
		contact_mu = 500

		world = args.world.inner_object
		contact_group = args.contact_group.inner_object

		for contact in contacts:
			# set contact parameters
			contact.setBounce(contact_bounce)
			contact.setMu(contact_mu)
			# create contact joint and attach it to the bodies
			c_joint = ode.ContactJoint(world, contact_group, contact)
			c_joint.attach(geom1.getBody(), geom2.getBody())

	@classmethod
	def process_ray_collision_contacts(cls, ray, other_geom, contacts):
		"""(see parent :meth:`.base.Engine.process_ray_collision_contacts`)

		:param ray: monkey-patched object whose attribute ``outer_object``
			references its wrapper (a :class:`.base.Ray` object)
		:type ray: :class:`ode.GeomRay`
		:param other_geom:
		:type other_geom: :class:`ode.GeomObject`
		:param contacts:
		:type contacts: list of :class:`ode.Contact`

		"""
		for contact in contacts:
			# pos: intersection position
			# depth: distance
			(pos, normal, depth, geom1, geom2) = contact.getContactGeomParams()
			ray_contact = base.RayContactData(
				ray, other_geom, pos, normal, depth)
			try:
				ray.outer_object.set_last_contact(ray_contact)
			except AttributeError:
				logger.error("`ray` has no attribute `outer_object` ")
			except Exception:
				logger.exception("Ray's encapsulating object's last_contact"
				                 "attribute could not be set")


class Space(base.Space):

	"""Adapter to :class:`ode.SimpleSpace`."""

	def __init__(self):
		self._inner_object = ode_objects_factories.create_ode_simple_space()

	def collide(self, args, callback=None):
		"""Call ``callback`` with ``args`` for all potentially intersecting
		geom pairs.

		Function ``callback`` must accept 3 arguments: ``args, geom1, geom2``.

		:param args: data object passed to ``callback`` in each call
		:type args: :class:`NearCallbackArgs`
		:param callback: a function with signature ``args, geom1, geom2``
		:type callback: function or None

		"""
		if callback is None:
			self._inner_object.collide(args, Engine.near_callback)
		else:
			self._inner_object.collide(args, callback)

#==============================================================================
# Parents
#==============================================================================


class Geom(base.Geom):

	"""Abstract class, sort of equivalent to :class:`ode.GeomObject`."""

	def attach_body(self, body):
		super(Geom, self).attach_body(body)
		self._inner_object.setBody(body.inner_object)

	#==========================================================================
	# Getters and setters
	#==========================================================================

	def get_position(self):
		"""Get the position of the geom.

		:return: position
		:rtype: 3-sequence of floats

		"""
		return self._inner_object.getPosition()

	def get_rotation(self):
		"""Get the orientation of the geom.

		:return: rotation matrix
		:rtype: 9-sequence of floats

		"""
		return self._inner_object.getRotation()

	def set_position(self, pos):
		"""Set the position of the geom.

		:param pos: position
		:type pos: 3-sequence of floats

		"""
		self._inner_object.setPosition(pos)

	def set_rotation(self, rot):
		"""Set the orientation of the geom.

		:param rot: rotation matrix
		:type rot: 9-sequence of floats

		"""
		self._inner_object.setRotation(rot)


class BasicShape(Geom):

	__metaclass__ = ABCMeta

#==============================================================================
# Other shapes
#==============================================================================


class Plane(BasicShape, base.Plane):

	"""Plane, different from a box"""

	def __init__(self, space, normal, dist):
		BasicShape.__init__(self)
		base.Plane.__init__(self, space, normal, dist)

		self._inner_object = ode_objects_factories.create_ode_plane(
			space.inner_object, normal, dist)


class Ray(Geom, base.Ray):

	def __init__(self, space, length):
		Geom.__init__(self)
		base.Ray.__init__(self, space, length)
		self._inner_object = ode_objects_factories.create_ode_ray(
			space.inner_object, length)
		self._inner_object.outer_object = self  # the encapsulating object

	def get_length(self):
		return self._inner_object.getLength()

	def set_length(self, length):
		self._inner_object.setLength(length)


class Trimesh(Geom, base.Trimesh):

	def __init__(self, space, vertices, faces):
		Geom.__init__(self)
		base.Trimesh.__init__(self, space, vertices, faces)

		self._inner_object = ode_objects_factories.create_ode_trimesh(
			space.inner_object, vertices, faces)

#==============================================================================
# Basic Shapes
#==============================================================================


class Box(BasicShape, base.Box):
	"""Box shape, aligned along the X, Y and Z axii by default"""

	def __init__(self, space, size):
		BasicShape.__init__(self)
		base.Box.__init__(self, space, size)

		self._inner_object = ode_objects_factories.create_ode_box(
			space.inner_object, size)


class Sphere(BasicShape, base.Sphere):
	"""Spherical shape"""

	def __init__(self, space, radius):
		BasicShape.__init__(self)
		base.Sphere.__init__(self, space, radius)

		self._inner_object = ode_objects_factories.create_ode_sphere(
			space.inner_object, radius)


class Capsule(BasicShape, base.Capsule):
	"""Capsule shape, aligned along the Z-axis by default"""

	def __init__(self, space, length, radius):
		BasicShape.__init__(self)
		base.Capsule.__init__(self, space, length, radius)

		self._inner_object = ode_objects_factories.create_ode_capsule(
			space.inner_object, length, radius)


class Cylinder(BasicShape, base.Cylinder):
	"""Cylinder shape, aligned along the Z-axis by default"""

	def __init__(self, space, length, radius):
		BasicShape.__init__(self)
		base.Cylinder.__init__(self, space, length, radius)

		self._inner_object = ode_objects_factories.create_ode_cylinder(
			space.inner_object, length, radius)

#==============================================================================
# aux classes
#==============================================================================


class ContactGroup(base.ContactGroup):

	def __init__(self):
		self._inner_object = ode_objects_factories.create_ode_joint_group()

	def empty(self):
		self._inner_object.empty()
