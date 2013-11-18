import setuptools
import setuptools.extension

try:
    import Cython.Distutils
except ImportError:
    cmdclass = {}
    suffix = ".cpp"
else:
    cmdclass = {"build_ext": Cython.Distutils.build_ext}
    suffix = ".pyx"

ext_modules = [
    setuptools.extension.Extension(
        "bdaq.wrapper",
        map(
            lambda path: path + suffix,
            ["bdaq/wrapper"]),
        include_dirs=[],
        undef_macros=["NDEBUG"],
        define_macros=[],
        libraries=["biodaq"],
        extra_compile_args=[
            "-std=gnu++0x",
            "-Werror",
            "-Wno-uninitialized",
            "-Wno-write-strings"],
        language="c++")]
requires = []

setuptools.setup(
    name="pybdaq",
    version="0.0.3",
    packages=setuptools.find_packages(),
    cmdclass=cmdclass,
    ext_modules=ext_modules,
    install_requires=requires,
    author="Angaza Design",
    author_email="bcs@angazadesign.com",
    description="data acquisition hardware (DAQ) SDK wrapper",
    license="MIT",
    keywords="daq wrapper library bionic advantech usb",
    url="https://github.com/angaza/pybdaq",
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Cython",
        "Programming Language :: Python :: 2.7",
        "Operating System :: POSIX :: Linux",
        "Topic :: Utilities",
        "Topic :: System :: Hardware",
        "Topic :: Software Development :: Libraries"])
