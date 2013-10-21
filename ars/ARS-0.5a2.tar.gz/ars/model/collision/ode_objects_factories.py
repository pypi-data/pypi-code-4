"""ODE objects factories i.e. functions that create ODE objects.

"""
import ode

#==============================================================================
# Environment
#==============================================================================


def create_ode_simple_space():
	"""Create an ODE geoms container (i.e. "space") of the simplest type.

	.. note::
		``ode.SimpleSpace()`` equals ``ode.Space(space_type=0)``.

	:return: ODE simple space
	:rtype: :class:`ode.SimpleSpace`

	"""
	return ode.SimpleSpace()


def create_ode_hash_space():
	"""Create a more sophisticated ODE geoms container (i.e. "space").

	.. note::
		``ode.HashSpace()`` equals ``ode.Space(space_type=1)``.

	:return: ODE hash space
	:rtype: :class:`ode.HashSpace`

	"""
	return ode.HashSpace()


def create_ode_joint_group():
	"""Create an ODE joint group.

	:return: ODE joint group
	:rtype: :class:`ode.JointGroup`

	"""
	return ode.JointGroup()

#==============================================================================
# Other shapes
#==============================================================================


def create_ode_plane(space, normal, dist):
	r"""Create an ODE plane (infinite) geom.

	The plane equation is

	.. math::

		n_0 \cdot x + n_1 \cdot y + n_2 \cdot z = dist

	where  ``normal = (n0, n1, n2)``.

	.. warning::
		This object can't be attached to a body.

	:param space:
	:type space: :class:`ode.Space`
	:param normal: vector normal to the plane
	:type normal: 3-sequence of floats
	:param dist: constant of the plane equation
	:type dist: float
	:return: ODE plane geom
	:rtype: :class:`ode.GeomPlane`

	"""
	return ode.GeomPlane(space, normal, dist)


def create_ode_ray(space, length):
	"""Create an ODE ray geom.

	:param space:
	:type space: :class:`ode.Space`
	:param length:
	:type length: float
	:return: ODE ray geom
	:rtype: :class:`ode.GeomRay`

	"""
	return ode.GeomRay(space, length)


def create_ode_trimesh(space, vertices, faces):
	"""Create an ODE trimesh geom.

	:param space:
	:type space: :class:`ode.Space`
	:param vertices:
	:type vertices: sequence of 3-sequences of floats
	:param faces:
	:type faces: sequence of 3-sequences of ints
	:return: ODE trimesh geom
	:rtype: :class:`ode.GeomTriMesh`

	"""
	tm_data = ode.TriMeshData()
	tm_data.build(vertices, faces)
	return ode.GeomTriMesh(tm_data, space)

#==============================================================================
# Basic Shapes
#==============================================================================


def create_ode_box(space, size):
	"""Create an ODE box geom.

	:param space:
	:type space: :class:`ode.Space`
	:param size:
	:type size: 3-sequence of floats
	:return: ODE box geom
	:rtype: :class:`ode.GeomBox`

	"""
	return ode.GeomBox(space, lengths=size)


def create_ode_sphere(space, radius):
	"""Create an ODE sphere geom.

	:param space:
	:type space: :class:`ode.Space`
	:param radius:
	:type radius: float
	:return: ODE sphere geom
	:rtype: :class:`ode.GeomSphere`

	"""
	return ode.GeomSphere(space, radius)


def create_ode_capsule(space, length, radius):
	"""Create an ODE capsule geom.

	.. note::
		In ``GeomCCylinder`` (same as ``GeomCapsule``)
		*CCylinder* means Capped Cylinder.

	.. warning::
		ODE's constructor parameter order is different:
		``radius`` first and then ``length``.

	:param space:
	:type space: :class:`ode.Space`
	:param length: of the cylindrical section i.e. caps are not included
	:type length: float
	:param radius:
	:type radius: float
	:return: ODE capsule geom
	:rtype: :class:`ode.GeomCCylinder`

	"""
	# FIXME: replace with GeomCapsule (in docstring too)
	return ode.GeomCCylinder(space, radius, length)


def create_ode_cylinder(space, length, radius):
	"""Create an ODE cylinder geom.

	.. warning::
		ODE's constructor parameter order is different:
		``radius`` first and then ``length``.

	:param space:
	:type space: :class:`ode.Space`
	:param length:
	:type length: float
	:param radius:
	:type radius: float
	:return: ODE cylinder geom
	:rtype: :class:`ode.GeomCylinder`

	"""
	return ode.GeomCylinder(space, radius, length)
