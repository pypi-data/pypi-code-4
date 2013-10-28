from setuptools import setup

setup(
    name='transporter',
    version='0.1',
    long_description=__doc__,
    packages=['transporter'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['tornado', 'watchdog'],
    entry_points = {
        'console_scripts': [
            'transporter-server = transporter.server:run_server',
            'transporter-client = transporter.client:run_client',
        ],
    }
)
