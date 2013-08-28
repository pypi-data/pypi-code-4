import rtools

__all__ = ["install_all_cellnopt_dependencies"]

def install_all_cellnopt_dependencies(packages=None):
    """script to install all CellNOptR packages dependencies


    This is not complete but functional. So, we just need to add all relevant
    packages.

        >>> from cellnopt.admin import install_all_cellnopt_dependencies
        >>> install_all_cellnopt_dependencies()


    """
    pm = rtools.RPackageManager()
    installed_packages = pm.installed['Package']

    if packages == None:
        packages = ["Rsolnp", "snowfall", "igraph", "RUnit", "xtable"]

    for package in packages:
        if package not in installed_packages:
            print("Installing %s " % package)
            rtools.biocLite(package)
        else:
            print("%s already installed. skipped" % package)

install_all_cellnopt_dependencies()
