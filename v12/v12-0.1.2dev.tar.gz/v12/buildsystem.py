#TODO: add _delayed_files class attribute and remove processing status class, change returns to simple true/false
#TODO: remove ManifestDataUtil remove_orphans call and push it into the actual util to handle
#TODO: add in RoutesUtil into the build process
#TODO: implement execute either here or in utils

import os
import types
import fnmatch
import re

from v12 import env, FileManifest
from utils import shell


class ProcessingStatus:
    SUCCESS = 0
    MISMATCH = 1
    DELAY = 2


_is_build_running = False


def build():
    global _is_build_running

    if "pre_run" in env.v12_config["build"]:
        shell(_format_command(env.v12_config["build"]["pre_run"]))

    _is_build_running = True

    old_manifest_map = FileManifest.clear()

    for root in env.v12_config["build"]["directories"]:
        if root["path"][0] == "/":
            root["path"] = root["path"][1:]
        root["path"] = os.path.join(env.project_path, root["path"])
    build_roots = [fnmatch.translate(root["path"]) for root in env.v12_config["build"]["directories"]]

    delayed_files = []
    build_directories = "directory" in env.v12_config["compile"]

    for build_dir in env.v12_config["build"]["directories"]:
        excludes = list(build_roots)
        if "exclude_regex" in build_dir:
            excludes.extend(build_dir["exclude_regex"])
        if "exclude" in build_dir:
            excludes.extend([fnmatch.translate(os.path.join(build_dir["path"], exclude_path)) for exclude_path in
                             build_dir["exclude"]])

        excludes_pattern = r"|".join(excludes)

        for root, dirs, files in os.walk(build_dir["path"]):
            if build_directories:
                if process(root) == ProcessingStatus.DELAY:
                    delayed_files.append(root)

            if "recursive" in build_dir and not build_dir["recursive"]:
                dirs[:] = []

            dirs[:] = [os.path.join(root, d) for d in dirs]
            if excludes_pattern:
                dirs[:] = [d for d in dirs if not re.match(excludes_pattern, d)]

            for file in [os.path.join(root, f) for f in files]:
                if process(file) == ProcessingStatus.DELAY:
                    delayed_files.append(file)

    for file in delayed_files:
        process(file)

    FileManifest.remove_orphans(old_manifest_map)

    _is_build_running = False

    if "post_run" in env.v12_config["build"]:
        shell(_format_command(env.v12_config["build"]["post_run"]))


def process(path, remove_source=False):
    """
    Intelligently compiles a file or directory based on the project compile configuration
    """
    process_keys = []
    extensions = os.path.basename(path)[1:].split(".")[1:]

    if extensions:
        for i in range(len(extensions)):
            process_keys.append(".".join(extensions[i:]))
    elif os.path.isdir(path):
        process_keys.append("directory")

    for process_key in process_keys:
        if process_key in env.v12_config["process"]:
            ext_config = env.v12_config["process"][process_key]
            if isinstance(ext_config, types.DictType):
                process_status = _parse_process_config(path, ext_config, remove_source)
                if process_status != ProcessingStatus.MISMATCH:
                    return process_status
            elif isinstance(ext_config, types.ListType):
                for process_config in env.v12_config["process"][process_key]:
                    process_status = _parse_process_config(path, process_config, remove_source)
                    if process_status != ProcessingStatus.MISMATCH:
                        return process_status


def _parse_process_config(filepath, process_config, remove_source):
    if "dev" in process_config and env.dev:
        for config_option in process_config["dev"]:
            process_config[config_option] = process_config["dev"][config_option]

    if "no_operation" in process_config and process_config["no_operation"]:
        return ProcessingStatus.SUCCESS

    if "delay" in process_config and _is_build_running:
        return ProcessingStatus.DELAY

    filepath = os.path.abspath(filepath)

    if "includes_pattern" not in process_config:
        includes = []
        if "include" in process_config:
            includes.extend([fnmatch.translate(pattern) for pattern in process_config["include"]])
        if "include_regex" in process_config:
            includes.extend(process_config["include_regex"])
        if "include_name" in process_config:
            includes.extend([fnmatch.translate(os.path.dirname(filepath) + "/" + pattern) for pattern in
                             process_config["include_name"]])
        if "include_name_regex" in process_config:
            includes.extend([os.path.dirname(filepath) + "/" + pattern for pattern in
                             process_config["include_name_regex"]])
        process_config["includes_pattern"] = r"|".join(includes)

    if "excludes_pattern" not in process_config:
        excludes = []
        if "exclude" in process_config:
            excludes.extend([fnmatch.translate(pattern) for pattern in process_config["exclude"]])
        if "exclude_regex" in process_config:
            excludes.extend(process_config["exclude_regex"])
        if "exclude_name" in process_config:
            excludes.extend([fnmatch.translate(os.path.dirname(filepath) + "/" + pattern) for pattern in
                             process_config["exclude_name"]])
        if "exclude_name_regex" in process_config:
            excludes.extend([os.path.dirname(filepath) + "/" + pattern for pattern in
                             process_config["exclude_name"]])
        process_config["excludes_pattern"] = r"|".join(excludes)

    if not process_config["includes_pattern"] or re.match(process_config["includes_pattern"], filepath):
        if not process_config["excludes_pattern"] or not re.match(process_config["excludes_pattern"], filepath):
            if "command" in process_config:
                shell(_format_command(process_config["command"], filepath))
            elif "task" in process_config:
                task = process_config["task"]["name"]
                args = process_config["task"]["args"]

                if isinstance(args, types.DictType):
                    for arg_name in args:
                        args[arg_name] = _substitute_config_variables(args[arg_name], filepath)
                    execute(task, **args)
                elif isinstance(args, types.ListType):
                    args[:] = [_substitute_config_variables(arg, filepath) for arg in args]
                    execute(task, *args)

            if remove_source:
                os.remove(filepath)
            return ProcessingStatus.SUCCESS

    return ProcessingStatus.MISMATCH


def _format_command(command, filepath=""):
    if command[-(len(os.linesep)):] == os.linesep:
        command = command[:-(len(os.linesep))]
    command = command.replace(os.linesep, " && ")

    return _substitute_config_variables(command, filepath)


def _substitute_config_variables(config_string, filepath=""):
    #define variables to help with substitutions
    filename = os.path.basename(filepath)
    full_ext = filename[filename[1:].find(".") + 1:]
    filename_base = filename[:-len(full_ext)]
    base_ext = os.path.splitext(full_ext[1:])[1]
    file_dir = os.path.dirname(filepath) or "."

    #perform substitutions
    config_string = config_string.replace("$FILEPATHNOEXT", file_dir + "/" + filename_base + "." + base_ext)
    config_string = config_string.replace("$FILEPATHNOFULLEXT", file_dir + "/" + filename_base)
    config_string = config_string.replace("$FILEPATH", filepath)
    config_string = config_string.replace("$FILENAMEBASE", filename_base)
    config_string = config_string.replace("$FILENAME", filename)
    config_string = config_string.replace("$BASEEXT", base_ext)
    config_string = config_string.replace("$EXT", os.path.splitext(filename)[1][1:])
    config_string = config_string.replace("$FULLEXT", full_ext[1:])
    config_string = config_string.replace("$FILEDIR", file_dir)
    config_string = config_string.replace("$PROJECTPATH", env.project_path)
    return config_string


def execute(task_name):
    return

