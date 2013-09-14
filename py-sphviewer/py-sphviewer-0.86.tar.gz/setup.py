from distutils.core import setup

setup(name='py-sphviewer',
      version='0.86',
      author='Alejandro Benitez Llambay',
      author_email='alejandrobll@oac.uncor.edu',
      url='https://code.google.com/p/py-sphviewer/',
      description='Py-SPHViewer is a framework for rendering images using the smoothed particle hydrodynamics scheme.',
      license='GNU GPL v3',
      keywords="smoothed particle hydrodynamics render particles nbody galaxy formation dark matter sph cosmology movies",      
      packages=['sphviewer'],
      package_data={'sphviewer': ['*.c','*.txt']},
      requieres=['multiprocessing','matplotlib','scipy','numpy'],
      classifiers=[
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
            "Topic :: Scientific/Engineering :: Astronomy",
            "Topic :: Scientific/Engineering :: Visualization",
            ],
     )
