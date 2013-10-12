from setuptools import setup
setup(
    name = "sclc",
    version = "0.2.0",
    py_modules = ["simple_command_launcher_column"],
    description = "PySide Widget for executing a list of external system commands",
    author = "Oliver Kurz",
    author_email = "o.kurz@gmx.de",
    url = "https://www.gitorious.org/sclc",
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    long_description = """\
PySide Widget showing a list of external system commands to execute and show a
window with output, success or failure of the call. Each command supplied in a
constructor list is assigned to a button with a corresponding label.
    """
)
