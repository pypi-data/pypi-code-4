from setuptools import setup

setup(
    name = "rpi-xmpp",
    version="0.0.1",
    scripts = ['rpi-xmpp/rpi-xmpp.py'],
    description = "Sending XMPP messages from RaspberryPi GPIO events",
    url = "https://github.com/diresi/rpi-xmpp",
    author = "Christoph Rissner",
    author_email = "diresi@gmx.net",
    license = "LGPLv3+",
    install_requires = ["RPIO", "sleekxmpp"],
    keywords = ["raspberry", "raspberry pi", "gpio", "xmpp"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Topic :: Utilities",
        "Topic :: Software Development",
        "Topic :: Home Automation",
        "Topic :: System :: Hardware",
        "Intended Audience :: Developers",
        ("License :: OSI Approved :: "
                "GNU Lesser General Public License v3 or later (LGPLv3+)"),
        "License :: Other/Proprietary License",
    ],
)

