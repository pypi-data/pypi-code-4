import os
import jinja2
import shutil


__all__ = ['handle_project']


def copy(src, dst):
    """Copy file or directory from src to dst"""
    if os.path.isfile(src):
        shutil.copy(src, dst)
    elif os.path.isdir(src):
        shutil.copytree(src, dst)
    return dst

def expand_template(template_content, template_data):
    """Expand template using jinja2 template engine"""
    return jinja2.Template(template_content).render(template_data)

def maybe_rename(src, template_data):
    """Rename file or directory if it's name contains expandable variables
    Here we use Jinja2 {{%s}} syntax.

    :return: bool. `True` if rename happend, `False` otherwise.
    """

    new_path = expand_vars_in_file_name(src, template_data)
    if new_path != src:
        shutil.move(src, new_path)
        return True
    return False

def expand_vars_in_file(filepath, template_data):
    """Expand variables in file"""
    with open(filepath) as fp:
        file_contents = expand_template(fp.read(), template_data)
    with open(filepath, 'w') as f:
        f.write(file_contents)

def expand_vars_in_file_name(filepath, template_data):
    """Expand variables in file/directory path"""
    return expand_template(filepath, template_data)

def handle_project(src, dst, template_data):
    """Main templet library function, does all the work.

    First copy template directory to current working path, renaming it
    to `PROJECT_NAME`.
    Then expand variables in directories names.
    And in the end, expand variables in files names and it's content.
    """

    copy(src, dst)
    for root, dirs, files in os.walk(dst):
        for d in dirs:
            dirpath = os.path.join(root, d)
            maybe_rename(dirpath, template_data)

        for f in files:
            filepath = os.path.join(root, f)
            if os.path.isfile(filepath):
                expand_vars_in_file(filepath, template_data)
            maybe_rename(filepath, template_data)

