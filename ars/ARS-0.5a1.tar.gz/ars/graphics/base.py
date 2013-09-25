from abc import ABCMeta, abstractmethod


class Entity(object):

	"""Renderable and movable object.

	It has position and orientation. The underlying object is :attr:`actor`,
	which connects to the real entity handled by the graphics library in use.

	"""

	__metaclass__ = ABCMeta

	adapter = None

	@abstractmethod
	def __init__(self, pos, rot):
		self._position = pos
		self._rotation = rot
		self._actor = None

	def set_pose(self, pos, rot):
		self._position = pos
		self._rotation = rot
		self.adapter._update_pose(self._actor, pos, rot)

	@property
	def actor(self):
		return self._actor


class Axes(Entity):

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, pos=(0, 0, 0), rot=None, cylinder_radius=0.05):
		super(Axes, self).__init__(pos, rot)


class Body(Entity):

	"""Entity representing a defined body with a given color."""

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, center, rot):  # TODO: rename 'center' to 'pos'
		super(Body, self).__init__(center, rot)
		self._color = None

	@abstractmethod
	def get_color(self):
		return self._color

	@abstractmethod
	def set_color(self, color):
		self._color = color


class Box(Body):

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, size, pos, rot=None):
		super(Box, self).__init__(pos, rot)


class Cone(Body):

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, height, radius, center, rot=None, resolution=100):
		"""Constructor.

		:param resolution: it is the circumferential number of facets
		:type resolution: int

		"""
		super(Cone, self).__init__(center, rot)


class Sphere(Body):

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, radius, center, rot=None, phi_resolution=50,
                 theta_resolution=50):
		"""Constructor.

		:param phi_resolution: resolution in the latitude (phi) direction
		:type phi_resolution: int
		:param theta_resolution: resolution in the longitude (theta) direction
		:type theta_resolution: int

		"""
		super(Sphere, self).__init__(center, rot)


class Cylinder(Body):

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, length, radius, center, rot=None, resolution=10):
		super(Cylinder, self).__init__(center, rot)


class Capsule(Body):

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, length, radius, center, rot=None, resolution=10):
		super(Capsule, self).__init__(center, rot)


class Trimesh(Body):

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, vertices, faces, pos=None, rot=None):
		super(Trimesh, self).__init__(pos, rot)


class Engine(object):

	"""
	Abstract class. Not coupled (at all) with VTK or any other graphics library

	"""

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, *args, **kwargs):
		self.timer_count = 0
		self.on_idle_parent_callback = None
		self.on_reset_parent_callback = None
		self.on_key_press_parent_callback = None
		self._window_started = False

	@abstractmethod
	def add_object(self, obj):
		"""Add ``obj`` to the visualization controlled by this adapter.

		:param obj:
		:type obj: :class:`Body`

		"""
		pass

	@abstractmethod
	def remove_object(self, obj):
		"""Remove ``obj`` from the visualization controlled by this adapter.

		:param obj:
		:type obj: :class:`Body`

		"""
		pass

	def add_objects_list(self, obj_list):
		for obj in obj_list:
			self.add_object(obj)

	@abstractmethod
	def start_window(
            self, on_idle_callback, on_reset_callback, on_key_press_callback):
		pass

	@abstractmethod
	def restart_window(self):
		pass

	@abstractmethod
	def finalize_window(self):
		"""Finalize window and remove/clear associated resources."""
		pass

	@abstractmethod
	def _timer_callback(self, obj, event):
		pass

	@abstractmethod
	def _key_press_callback(self, obj, event):
		pass

	@abstractmethod
	def reset(self):
		pass

	@classmethod
	def _update_pose(cls, obj, pos, rot):
		# Raising an exception efectively makes this definition be that of
		# an abstract method (i.e. calling it directly raises an exception),
		# except that it not requires the subclass to implement it if it is
		# not used. We would like to use @classmethod AND @abstractmethod,
		# but until Python 3.3 that doesn't work correctly.
		# http://docs.python.org/3/library/abc.html
		raise NotImplementedError()


class ScreenshotRecorder(object):

	__metaclass__ = ABCMeta

	file_extension = None  # e.g. 'png'

	def __init__(self, base_filename):
		self.base_filename = base_filename
		self.last_write_time = None
		self.period = None

	@abstractmethod
	def write(self, index, time):
		"""Write render-window's currently displayed image to a file.

		The image format (thus the file extension too) to use must be defined
		by the implementation.

		Image's filename is determined by :meth:`calc_filename`.

		:param index: image's index to use for filename calculation
		:type index: int
		:param time:
		:type time:

		"""
		pass

	def calc_filename(self, index=1):
		"""Calculate a filename using ``index`` for a new image.

		:param index: image's index to use for filename calculation
		:type index: int
		:return: image's filename
		:rtype: str

		"""
		return '%s%d.%s' % (self.base_filename, index, self.file_extension)
