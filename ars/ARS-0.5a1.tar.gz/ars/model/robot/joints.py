"""Module of all the classes related to physical joints.
These are objects that link 2 bodies together.

There are two base abstract classes for all joints:
:class:`Joint` and :class:`ActuatedJoint`.
They are not coupled (at all) with ODE or any other
physics or collision library/engine.

The classes that implement at least one of those interfaces are these:

* :class:`Fixed`
* :class:`Rotary`
* :class:`Universal`
* :class:`BallSocket`
* :class:`Slider`

There is also an auxiliary class: :class:`JointFeedback`.

"""
from abc import ABCMeta, abstractmethod

import ode

from ... import exceptions as exc
from ...lib.pydispatch import dispatcher

from . import signals


class Joint(object):

	"""Entity that links 2 bodies together, enforcing one or more
	movement constraints.

	This is an abstract class.

	"""

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, world, inner_joint, body1=None, body2=None):
		"""Constructor.

		:param world:
		:type world: :class:`physics.base.World`
		:param inner_joint:
		:type inner_joint: :class:`ode.Joint`
		:param body1:
		:type body1: :class:`physics.base.Body`
		:param body2:
		:type body2: :class:`physics.base.Body`

		"""
		self._world = world
		self._inner_joint = inner_joint
		self._body1 = body1
		self._body2 = body2

	@property
	def body1(self):
		return self._body1

	@property
	def body2(self):
		return self._body2


class ActuatedJoint(Joint):

	"""A joint with an actuator that can exert force and/or torque
	to connected bodies.

	This is an abstract class.

	"""

	__metaclass__ = ABCMeta


class Fixed(Joint):

	def __init__(self, world, body1, body2):
		"""Constructor.

		:param world:
		:type world: :class:`physics.base.World`
		:param body1:
		:type body1: :class:`physics.base.Body`
		:param body2:
		:type body2: :class:`physics.base.Body`

		"""
		try:
			inner_joint = ode.FixedJoint(world._inner_object)
			inner_joint.attach(body1.inner_object, body2.inner_object)
			inner_joint.setFixed()

			super(Fixed, self).__init__(world, inner_joint, body1, body2)
		except:
			raise exc.PhysicsObjectCreationError(type_='Fixed joint')


class Rotary(ActuatedJoint):

	def __init__(self, world, body1, body2, anchor, axis):
		"""Constructor.

		:param world:
		:type world: :class:`physics.base.World`
		:param body1:
		:type body1: :class:`physics.base.Body`
		:param body2:
		:type body2: :class:`physics.base.Body`
		:param anchor: joint anchor point
		:type anchor: 3-tuple of floats
		:param axis: rotation axis
		:type axis: 3-tuple of floats

		"""
		try:
			inner_joint = ode.HingeJoint(world._inner_object)
			inner_joint.attach(body1.inner_object, body2.inner_object)
			inner_joint.setAnchor(anchor)
			# TODO: see contrib.Ragdoll.addHingeJoint for possible modification
			inner_joint.setAxis(axis)

			# TODO: necessary?
			lo_stop = -ode.Infinity
			hi_stop = ode.Infinity
			inner_joint.setParam(ode.ParamLoStop, lo_stop)
			inner_joint.setParam(ode.ParamHiStop, hi_stop)

			super(Rotary, self).__init__(world, inner_joint, body1, body2)
		except:
			raise exc.PhysicsObjectCreationError(type_='Rotary joint')

	def add_torque(self, torque):
		"""Apply torque about the rotation axis.

		:param torque: magnitude
		:type torque: float

		"""
		dispatcher.send(signals.JOINT_PRE_ADD_TORQUE, sender=self,
		                torque=torque)
		try:
			self._inner_joint.addTorque(torque)
		except:
			raise exc.JointError(self, 'Failed to add torque to this joint')
		dispatcher.send(signals.JOINT_POST_ADD_TORQUE, sender=self,
		                torque=torque)

	@property
	def angle(self):
		"""Return the angle between the two bodies.

		The zero angle is determined by the position of the bodies
		when joint's anchor was set.

		:return: value ranging ``-pi`` and ``+pi``
		:rtype: float

		"""
		try:
			return self._inner_joint.getAngle()
		except:
			raise exc.JointError(self, 'Failed to get the angle of this joint')

	@property
	def angle_rate(self):
		"""Return the rate of change of the angle between the two bodies.

		:return: angle rate
		:rtype: float

		"""
		try:
			return self._inner_joint.getAngleRate()
		except:
			raise exc.JointError(self, 'Failed to get the angle rate of this joint')

	def set_speed(self, speed, max_force=None):
		"""Set rotation speed to ``speed``.

		The joint will set that speed by applying a force up to
		``max_force``, so it is not guaranteed that ``speed``
		will be reached.

		:param speed: speed to set
		:type speed: float
		:param max_force: if not None, the maximum force the joint can
			apply when trying to set the rotation speed
		:type max_force: float or None

		"""
		dispatcher.send(signals.JOINT_PRE_SET_SPEED, sender=self, speed=speed)
		if max_force is not None:
			self._inner_joint.setParam(ode.ParamFMax, max_force)
		self._inner_joint.setParam(ode.ParamVel, speed)
		dispatcher.send(signals.JOINT_POST_SET_SPEED, sender=self, speed=speed)


class Universal(Joint):

	def __init__(self, world, body1, body2, anchor, axis1, axis2):
		"""Constructor.

		:param world:
		:type world: :class:`physics.base.World`
		:param body1:
		:type body1: :class:`physics.base.Body`
		:param body2:
		:type body2: :class:`physics.base.Body`
		:param anchor: joint anchor point
		:type anchor: 3-tuple of floats
		:param axis1: first universal axis
		:type axis1: 3-tuple of floats
		:param axis2: second universal axis
		:type axis2: 3-tuple of floats

		"""
		try:
			inner_joint = ode.UniversalJoint(world._inner_object)
			inner_joint.attach(body1.inner_object, body2.inner_object)
			inner_joint.setAnchor(anchor)
			# TODO: see contrib.Ragdoll.addHingeJoint for possible modification
			inner_joint.setAxis1(axis1)
			inner_joint.setAxis2(axis2)

			# TODO: necessary?
			lo_stop1 = -ode.Infinity
			hi_stop1 = ode.Infinity
			lo_stop2 = -ode.Infinity
			hi_stop2 = ode.Infinity
			inner_joint.setParam(ode.ParamLoStop, lo_stop1)
			inner_joint.setParam(ode.ParamHiStop, hi_stop1)
			inner_joint.setParam(ode.ParamLoStop2, lo_stop2)
			inner_joint.setParam(ode.ParamHiStop2, hi_stop2)

			super(Universal, self).__init__(world, inner_joint, body1, body2)
		except:
			raise exc.PhysicsObjectCreationError(type_='Universal joint')


class BallSocket(Joint):

	def __init__(self, world, body1, body2, anchor):
		"""Constructor.

		:param world:
		:type world: :class:`physics.base.World`
		:param body1:
		:type body1: :class:`physics.base.Body`
		:param body2:
		:type body2: :class:`physics.base.Body`
		:param anchor: joint anchor point
		:type anchor: 3-tuple of floats

		"""
		try:
			inner_joint = ode.BallJoint(world._inner_object)
			inner_joint.attach(body1.inner_object, body2.inner_object)
			inner_joint.setAnchor(anchor)

			super(BallSocket, self).__init__(world, inner_joint, body1, body2)
		except:
			raise exc.PhysicsObjectCreationError(type_='Ball and Socket joint')


class Slider(ActuatedJoint):

	"""Joint with one DOF that constrains two objects to line up along an axis.

	It is different from a Piston joint (which has two DOF) in that the Slider
	does not allow rotation.

	"""

	def __init__(self, world, body1, body2, axis):
		"""Constructor.

		:param world:
		:type world: :class:`physics.base.World`
		:param body1:
		:type body1: :class:`physics.base.Body`
		:param body2:
		:type body2: :class:`physics.base.Body`
		:param axis: rotation axis
		:type axis: 3-tuple of floats

		"""
		try:
			inner_joint = ode.SliderJoint(world._inner_object)
			inner_joint.attach(body1.inner_object, body2.inner_object)
			inner_joint.setAxis(axis)

			# TODO: necessary?
			# see http://ode-wiki.org/wiki/index.php?title=Manual:_Joint_Types_and_Functions#Parameter_Functions
			lo_stop = -ode.Infinity
			hi_stop = ode.Infinity
			inner_joint.setParam(ode.ParamLoStop, lo_stop)
			inner_joint.setParam(ode.ParamHiStop, hi_stop)

			super(Slider, self).__init__(world, inner_joint, body1, body2)
		except:
			raise exc.PhysicsObjectCreationError(type_='Slider joint')

	def add_force(self, force):
		"""Apply a force of magnitude ``force`` along the joint's axis.

		:type force: float

		"""
		dispatcher.send(signals.JOINT_PRE_ADD_FORCE, sender=self, force=force)
		try:
			self._inner_joint.addForce(force)
		except:
			raise exc.JointError(self, 'Failed to add force to this joint')
		dispatcher.send(signals.JOINT_POST_ADD_FORCE, sender=self, force=force)

	@property
	def position(self):
		"""Return position of the joint with respect to its initial position.

		The zero position is established when the joint's axis is set.

		:rtype: float

		"""
		try:
			return self._inner_joint.getPosition()
		except:
			raise exc.JointError(self, 'Failed to get the position')

	@property
	def position_rate(self):
		"""Return position's time derivative, i.e. "speed".

		:rtype: float

		"""
		try:
			return self._inner_joint.getPositionRate()
		except:
			raise exc.JointError(self, 'Failed to get the position rate')

#==============================================================================
# aux classes
#==============================================================================


class JointFeedback(object):

	"""Data structure to hold the forces and torques resulting from
	the interaction of 2 bodies through a joint.

	All attributes are private. The results (:attr:`force1`, :attr:`force2`,
	:attr:`torque1`, :attr:`torque2`) are all length-3 tuples of floats.

	"""

	def __init__(self, body1, body2, force1=None, force2=None,
	             torque1=None, torque2=None):
		"""Constructor.

		:param body1:
		:type body1: :class:`physics.base.Body`
		:param body2:
		:type body2: :class:`physics.base.Body`
		:param force1:
		:type force1: 3-tuple of floats
		:param force2:
		:type force2: 3-tuple of floats
		:param torque1:
		:type torque1: 3-tuple of floats
		:param torque2:
		:type torque2: 3-tuple of floats

		"""
		self._body1 = body1
		self._body2 = body2
		self._force1 = force1
		self._force2 = force2
		self._torque1 = torque1
		self._torque2 = torque2

	@property
	def body1(self):
		return self._body1

	@property
	def body2(self):
		return self._body2

	@property
	def force1(self):
		return self._force1

	@property
	def force2(self):
		return self._force2

	@property
	def torque1(self):
		return self._torque1

	@property
	def torque2(self):
		return self._torque2
