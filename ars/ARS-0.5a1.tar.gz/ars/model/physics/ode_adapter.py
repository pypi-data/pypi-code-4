"""Classes and functions to interface the ODE physics engine with
the API defined in :mod:`physics`.

"""
from abc import ABCMeta

from ...constants import G_VECTOR
from ...lib.pydispatch import dispatcher
from ..collision import ode_adapter as shapes

from . import base, ode_objects_factories, signals

#==============================================================================
# Environment
#==============================================================================


class Engine(base.Engine):

	"""Adapter to the ODE physics engine"""

	world_class = None  # we have to define it below World's definition


class World(base.World):

	"""Adapter to :class:`ode.World`."""

	def __init__(self, gravity=G_VECTOR, ERP=0.8, CFM=1E-10, *args, **kwargs):
		"""Constructor.

		:param gravity: gravity acceleration vector
		:type gravity: 3-sequence of floats
		:param ERP: Error Reduction Parameter
		:type ERP: float
		:param CFM: Constraint Force Mixing
		:type CFM: float

		"""
		super(World, self).__init__(gravity, *args, **kwargs)
		self._inner_object = ode_objects_factories.create_ode_world(
			gravity, ERP, CFM)

	@property
	def gravity(self):
		return self._inner_object.getGravity()

	def step(self, time_step):
		dispatcher.send(signals.WORLD_PRE_STEP, sender=self)
		self._inner_object.step(time_step)
		dispatcher.send(signals.WORLD_POST_STEP, sender=self)


# This is a workaround necessary to solve the issue caused by the fact World
# is defined after Engine thus the latter can't use the former in its own
# definition (class attribute).
Engine.world_class = World

#==============================================================================
# Parents
#==============================================================================


class Body(object):

	"""Abstract class, sort of equivalent to :class:`ode.Body`."""

	__metaclass__ = ABCMeta

	def __init__(self, world, space, mass=None, density=None, *args, **kwargs):
		"""Constructor.

		:param world:
		:type world: :class:`.base.World`
		:param space:
		:type space: :class:`.collision.base.Space`
		:param mass:
		:type mass: float or None
		:param density:
		:type density: float or None

		"""
		self._inner_object = None

	#==========================================================================
	# Getters and setters
	#==========================================================================

	def get_position(self):
		"""Get the position of the body.

		:return: position
		:rtype: 3-sequence of floats

		"""
		return self._inner_object.getPosition()

	def get_linear_velocity(self):
		return self._inner_object.getLinearVel()

	def get_rotation(self):
		"""Get the orientation of the body.

		:return: rotation matrix
		:rtype: 9-sequence of floats

		"""
		return self._inner_object.getRotation()

	def get_angular_velocity(self):
		return self._inner_object.getAngularVel()

	def get_mass(self):
		return self._inner_object.getMass().mass

	def get_center_of_gravity(self):
		return self._inner_object.getMass().c

	def get_inertia_tensor(self):
		return self._inner_object.getMass().I

	def set_position(self, pos):
		"""Set the position of the body.

		Sends :data:`signals.BODY_PRE_SET_POSITION` and
		:data:`signals.BODY_POST_SET_POSITION`.

		:param pos: position
		:type pos: 3-sequence of floats

		"""
		dispatcher.send(signals.BODY_PRE_SET_POSITION, sender=self)
		self._inner_object.setPosition(pos)
		dispatcher.send(signals.BODY_POST_SET_POSITION, sender=self)

	def set_rotation(self, rot):
		"""Set the orientation of the body.

		Sends :data:`signals.BODY_PRE_SET_ROTATION` and
		:data:`signals.BODY_POST_SET_ROTATION`.

		:param rot: rotation matrix
		:type rot: 9-sequence of floats

		"""
		dispatcher.send(signals.BODY_PRE_SET_ROTATION, sender=self)
		self._inner_object.setRotation(rot)
		dispatcher.send(signals.BODY_POST_SET_ROTATION, sender=self)

#==============================================================================
# Bodies
#==============================================================================


class Box(Body, base.Box):
	def __init__(self, world, space, size, mass=None, density=None):
		Body.__init__(self, world, space, mass, density)
		base.Box.__init__(self, size, mass, density)

		body = ode_objects_factories.create_ode_box(
			world._inner_object, size, mass, density)
		geom = shapes.Box(space, size)
		self._inner_object = body
		self.attach_geom(geom)


class Sphere(Body, base.Sphere):
	def __init__(self, world, space, radius, mass=None, density=None):
		Body.__init__(self, world, space, mass, density)
		base.Sphere.__init__(self, radius, mass, density)

		body = ode_objects_factories.create_ode_sphere(
			world._inner_object, radius, mass, density)
		geom = shapes.Sphere(space, radius)
		self._inner_object = body
		self.attach_geom(geom)


class Capsule(Body, base.Capsule):
	def __init__(self, world, space, length, radius, mass=None, density=None):
		"""create capsule body (aligned along the z-axis so that it matches the
		Geom created below,	which is aligned along the Z-axis by default)"""
		Body.__init__(self, world, space, mass, density)
		base.Capsule.__init__(self, length, radius, mass, density)

		body = ode_objects_factories.create_ode_capsule(
			world._inner_object, length, radius, mass, density)
		geom = shapes.Capsule(space, length, radius)
		self._inner_object = body
		self.attach_geom(geom)


class Cylinder(Body, base.Cylinder):
	def __init__(self, world, space, length, radius, mass=None, density=None):
		"""create cylinder body (aligned along the z-axis so that it matches
		the Geom created below,	which is aligned along the Z-axis by default)"""
		Body.__init__(self, world, space, mass, density)
		base.Cylinder.__init__(self, length, radius, mass, density)

		body = ode_objects_factories.create_ode_cylinder(
			world._inner_object, length, radius, mass, density)
		geom = shapes.Cylinder(space, length, radius)
		self._inner_object = body
		self.attach_geom(geom)
