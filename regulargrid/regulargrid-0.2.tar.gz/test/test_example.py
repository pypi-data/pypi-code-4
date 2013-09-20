import numpy

if True:
	# create a 3-dimensional cartesian grid:
	limits = [(0, 1), (0, 1), (0, 1)]
	x = numpy.linspace(0, 1, 8)
	y = numpy.linspace(0, 1, 9)
	z = numpy.linspace(0, 1, 10)

	Z, Y = numpy.meshgrid(z, y)
	X = numpy.array([[x]]).transpose()

	# our grid values
	values = X**2 + Y - Z

	from regulargrid.cartesiangrid import CartesianGrid
	# does linear interpolation
	grid = CartesianGrid(limits, values)

	# interpolate for one point
	print grid([0.1], [0.5], [0.3])
	# interpolate many
	print grid([0.1, 0.3], [0.5, 0.5], [0.3, 0.2])

