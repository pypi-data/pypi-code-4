from utils import *
from v12 import env
import os
import re
import shutil


class MetaPackageManager(MetaDataFileUtil):
    _persisted_data = {}
    _PACKAGE_NAME_REGEX = re.compile("^(.*?)(\s*(!|<|>|=)=.*)?$")

    @property
    def PIP_DIRECTORY(cls):
        return os.path.join(env.project_path, "lib/packages")

    @property
    def _DATA_FILE(cls):
        return os.path.join(cls.PIP_DIRECTORY, "package_manifest.json")

    @persisted_data_modifier
    def install(cls, requirement_text, explicit=True):
        if env.dev:
            virtualenv("pip install " + requirement_text)
            return

        package_name = cls._PACKAGE_NAME_REGEX.match(requirement_text).group(1)
        dep_count = 0
        if package_name in cls._persisted_data:
            if cls._persisted_data[package_name]["locked"]:
                print "Install canceled: " + package_name + " is locked, unlock to uninstall or upgrade."
                return
            dep_count = cls._persisted_data[package_name]["dep_count"]
            explicit = explicit or cls._persisted_data[package_name]["explicit"]
            cls.uninstall(package_name, ignore_deps=True)

        (_, prev_dirs, _) = os.walk(cls.PIP_DIRECTORY).next()
        virtualenv("pip install --no-deps --exists-action w -t " + cls.PIP_DIRECTORY + " \"" + requirement_text + "\"")
        (_, post_dirs, _) = os.walk(cls.PIP_DIRECTORY).next()

        requires_path = ""
        for new_dir in set(post_dirs) - set(prev_dirs):
            if os.path.splitext(new_dir)[1] == ".egg-info":
                cls._persisted_data[package_name] = {"egg-info": new_dir}
                requires_path = os.path.join(cls.PIP_DIRECTORY, new_dir + "/requires.txt")
                break

        cls._persisted_data[package_name]["explicit"] = explicit
        cls._persisted_data[package_name]["dep_count"] = dep_count
        cls._persisted_data[package_name]["locked"] = False

        virtualenv("pip uninstall " + package_name, ignore_errors=True)

        if os.path.exists(requires_path):
            for requirement in open(requires_path):
                requirement = requirement.rstrip("\n")
                req_package_name = cls._PACKAGE_NAME_REGEX.match(requirement).group(1)

                if req_package_name not in cls._persisted_data or not cls._persisted_data[req_package_name]["locked"]:
                    cls.install(requirement, explicit=False)
                    cls._persisted_data[req_package_name]["dep_count"] += 1

    @persisted_data_modifier
    def uninstall(cls, package_name, ignore_deps=False):
        """
        Uninstalls a package in the PIP Directory
        """
        if env.dev:
            virtualenv("pip uninstall " + package_name, ignore_errors=True)
            return

        if package_name in cls._persisted_data:
            if cls._persisted_data[package_name]["locked"]:
                print "Uninstall canceled: " + package_name + " is locked, unlock to uninstall or upgrade."
                return

            if not ignore_deps and cls._persisted_data[package_name]["dep_count"] > 0:
                print "Uninstall canceled: " + package_name + " is depended on by another package." + \
                      "Use 'ignore_deps=True' to ignore dependencies."
                return

            cwd = os.getcwd()
            os.chdir(os.path.join(cls.PIP_DIRECTORY, cls._persisted_data[package_name]["egg-info"]))

            with open("top_level.txt") as top_level_file:
                top_level_dirs = top_level_file.read().splitlines()

            requirements = []
            if os.path.exists("requires.txt"):
                with open("requires.txt") as requires_file:
                    requirements = requires_file.read().splitlines()

            for line in open("installed-files.txt"):
                filepath = line.rstrip("\n")
                if os.path.exists(filepath):
                    if os.path.isdir(filepath):
                        shutil.rmtree(os.path.abspath(filepath))
                    else:
                        os.remove(filepath)

            for top_level_dir in top_level_dirs:
                if os.path.exists("../" + top_level_dir):
                    shutil.rmtree("../" + top_level_dir)

            del cls._persisted_data[package_name]

            os.chdir(cwd)

            for requirement in requirements:
                req_package_name = cls._PACKAGE_NAME_REGEX.match(requirement).group(1)
                if req_package_name in cls._persisted_data:
                    package_data = cls._persisted_data[req_package_name]
                    package_data["dep_count"] -= 1
                    if package_data["dep_count"] == 0 and not package_data["explicit"] and not package_data["locked"]:
                        cls.uninstall(req_package_name)

    @persisted_data_modifier
    def lock(cls, package_name):
        cls._persisted_data[package_name]["locked"] = True

    @persisted_data_modifier
    def unlock(cls, package_name):
        cls._persisted_data[package_name]["locked"] = False

class PackageManager(object): __metaclass__ = MetaPackageManager