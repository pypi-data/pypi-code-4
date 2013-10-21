"""Runs the simplest simulation ever: a falling ball impacts the floor.

"""
from ars.app import Program


class FallingBall(Program):

	def create_sim_objects(self):
		# radius, center, mass
		self.sim.add_sphere(0.5, (2, 3, 2), mass=1)
