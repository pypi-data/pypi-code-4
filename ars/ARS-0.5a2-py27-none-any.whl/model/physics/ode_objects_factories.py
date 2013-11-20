"""ODE objects factories i.e. functions that create ODE objects.

"""
import ode

from ...constants import G_VECTOR

#==============================================================================
# Environment
#==============================================================================


def create_ode_world(gravity=G_VECTOR, ERP=0.8, CFM=1E-10):
	"""Create an ODE world object.

	:param gravity: gravity acceleration vector
	:type gravity: 3-sequence of floats
	:param ERP: Error Reduction Parameter
	:type ERP: float
	:param CFM: Constraint Force Mixing
	:type CFM: float
	:return: world
	:rtype: :class:`ode.World`

	"""
	world = ode.World()
	world.setGravity(gravity)
	world.setERP(ERP)
	world.setCFM(CFM)
	return world

#==============================================================================
# Bodies
#==============================================================================


def create_ode_box(world, size, mass=None, density=None):
	"""Create an ODE body with box-like mass parameters.

	:param world:
	:type world: :class:`ode.World`
	:param size:
	:type size: 3-sequence of floats
	:param mass:
	:type mass: float or None
	:param density:
	:type density: float or None
	:return: box body
	:rtype: :class:`ode.Body`

	"""
	body = ode.Body(world)

	if mass is not None:
		m = ode.Mass()
		m.setBoxTotal(mass, *size)
		body.setMass(m)
	elif density is not None:
		m = ode.Mass()
		m.setBox(density, *size)
		body.setMass(m)

	return body


def create_ode_sphere(world, radius, mass=None, density=None):
	"""Create an ODE body with sphere-like mass parameters.

	:param world:
	:type world: :class:`ode.World`
	:param radius:
	:type radius: float
	:param mass:
	:type mass: float or None
	:param density:
	:type density: float or None
	:return: sphere body
	:rtype: :class:`ode.Body`

	"""
	body = ode.Body(world)

	if mass is not None:
		m = ode.Mass()
		m.setSphereTotal(mass, radius)
		body.setMass(m)
	elif density is not None:
		m = ode.Mass()
		m.setSphere(density, radius)
		body.setMass(m)

	return body


def create_ode_capsule(world, length, radius, mass=None, density=None):
	"""Create an ODE body with capsule-like mass parameters.

	:param world:
	:type world: :class:`ode.World`
	:param length:
	:type length: float
	:param radius:
	:type radius: float
	:param mass:
	:type mass: float or None
	:param density:
	:type density: float or None
	:return: capsule body
	:rtype: :class:`ode.Body`

	"""
	capsule_direction = 3  # z-axis
	body = ode.Body(world)

	if mass is not None:
		m = ode.Mass()
		m.setCapsuleTotal(mass, capsule_direction, radius, length)
		body.setMass(m)
	elif density is not None:
		m = ode.Mass()
		m.setCapsule(density, capsule_direction, radius, length)
		body.setMass(m)

	# set parameters for drawing the body
	# TODO: delete this, because it is related to the original implementation
	body.shape = "capsule"
	body.length = length
	body.radius = radius

	return body


def create_ode_cylinder(world, length, radius, mass=None, density=None):
	"""Create an ODE body with cylinder-like mass parameters.

	:param world:
	:type world: :class:`ode.World`
	:param length:
	:type length: float
	:param radius:
	:type radius: float
	:param mass:
	:type mass: float or None
	:param density:
	:type density: float or None
	:return: cylinder body
	:rtype: :class:`ode.Body`

	"""
	cylinderDirection = 3  # Z-axis
	body = ode.Body(world)

	if mass is not None:
		m = ode.Mass()
		m.setCylinderTotal(mass, cylinderDirection, radius, length)
		body.setMass(m)
	elif density is not None:
		m = ode.Mass()
		m.setCylinder(density, cylinderDirection, radius, length)
		body.setMass(m)

	return body
