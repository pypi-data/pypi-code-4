# -*- coding: utf-8 -*-

# imports
import os
import re
from datetime import datetime
import locale
import shutil
from mimetypes import guess_type
from zipfile import ZipFile
import json
import stat


class FileSystem(object):

    FILE_EXTENSIONS = ["png", "jpg", "jpeg", "bmp", "ps", "eps", "pdf", "txt", "xml", "py", "c", "cpp", "root", "pxlio"]
    BROWSER_EXTENSIONS = ["png", "jpg", "jpeg", "bmp", "pdf"]
    ADDITIONAL_MIMES = {"pxlio": "text/plain",
                        "root" : "text/plain"}

    def __init__(self):
        # allowed extensions
        self.allowed_extensions = FileSystem.FILE_EXTENSIONS

    def setup(self, basedir=None):
        if basedir==None:
            basedir = os.path.expanduser("~")
        if not os.path.isdir(basedir):
            raise Exception("Basedir ("+str(basedir)+") does not exist!")
        # the basedir
        self.basedir = os.path.join(basedir, ".vispa")
        if os.path.isdir(self.basedir):
            return "Basedir already exists"
        else: 
            os.makedirs(self.basedir, 0700)
            return "Basedir now exists"

    def get_mime_type(self, filepath):
        mime, encoding = guess_type(filepath)
        if mime is not None:
            return mime
        ext = filepath.split(".")[-1]
        if ext is not None and ext != "" and ext.lower() in FileSystem.ADDITIONAL_MIMES.keys():
            return FileSystem.ADDITIONAL_MIMES[ext]
        return None

    def check_file_extension(self, path, extensions=[]):
        if (len(extensions) == 0):
            return True
        for elem in extensions:
            elem = elem if elem.startswith(".") else "." + elem
            if path.lower().endswith(elem.lower()):
                return True
        return False

    def exists(self, path, type=None):
        # type may be 'f' or 'd'
        if path:
            path = os.path.expanduser(os.path.expandvars(path))
        # path exists physically?
        if not os.path.exists(path):
            return None
        # type correct?
        target_type = 'd' if os.path.isdir(path) else 'f'
        if not type:
            return target_type
        type = type.lower()
        if type not in ['f', 'd']:
            return None
        return target_type if target_type == type else None

    def get_file_list(self, path, deep=False, filter=[], reverse=False, hide_hidden=True, encode_json=False):
        filelist = []
        path_expand = os.path.expanduser(os.path.expandvars(path))
        try:
            for elem in os.listdir(path_expand):
                # hide hidden files?
                if elem.startswith('.') and hide_hidden:
                    continue

                # excluded by filters?
                match = False
                for filter_elem in filter:
                    if re.search(filter_elem, elem):
                        match = True
                if match != reverse:
                    continue

                fullpath = os.path.join(path_expand, elem)

                # get locales, mtime, etc
                locale.setlocale(locale.LC_ALL, '')
                stats = os.stat(fullpath)
                size = locale.format('%d', stats.st_size, grouping=True)
                mtime = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

                if stat.S_ISDIR(stats.st_mode):
                    filelist.append({'name': elem, 'type': 'd', 'parent': path, 'mtime': mtime, 'size': size, 'path': fullpath})
                    if deep:
                        filelist.extend(self.get_file_list(fullpath, deep, filter, reverse))
                else:
                    extension = elem.split('.')[-1]
                    filelist.append({'name': elem, 'type': 'f', 'parent': path, 'mtime': mtime, 'size': size, 'path': fullpath})
        except Exception, e:
            filelist.append({'warning': str(e)})

        # Determine the parent
        parentpath = path_expand[:-1] if path_expand.endswith(os.sep) and path_expand!=os.sep else path_expand
        parentpath = os.path.dirname(path_expand)
        data = {'filelist': filelist, 'parentpath': parentpath}
        if encode_json:
            return json.dumps(data)
        return data


    def get_suggestions(self, path, length=1, append_hidden=True, encode_json=False):
        suggestions = []
        source, filter = None, None
        # does the path exist?
        if os.path.exists(os.path.expanduser(os.path.expandvars(path))):
            # dir case
            if os.path.isdir(os.path.expanduser(os.path.expandvars(path))):
                if path.endswith('/'):
                    source = path
                else:
                    suggestions.append(path + os.sep)
                    return suggestions
            # file case
            else:
                return suggestions
        else:
            # try to estimate source and filter
            head, tail = os.path.split(path)
            if os.path.isdir(os.path.expanduser(os.path.expandvars(head))):
                source = head
                filter = tail

        # return empty suggestions when source is not set
        if not source:
            return suggestions

        files = os.listdir(os.path.expanduser(os.path.expandvars(source)))
        # resort?
        if append_hidden:
            files = sorted(map(lambda f: str(f), files), cmp=file_compare, key=str.lower)
        while (len(suggestions) < length or length == 0) and len(files):
            file = files.pop(0)
            if filter and not file.startswith(filter):
                continue
            suggestion = os.path.join(source, file)
            if not suggestion.endswith('/') and os.path.isdir(os.path.expanduser(os.path.expandvars(suggestion))):
                suggestion += '/'
            suggestions.append(suggestion)

        return suggestions if not encode_json else json.dumps(suggestions)

    def cut_slashs(self, path):
        path = path[1:] if path.startswith(os.sep) else path
        if path == "":
            return path
        path = path[:-1] if path.endswith(os.sep) else path
        return path

    def create_folder(self, path, name):
        # folder with the same name existent?
        fullpath = os.path.expanduser(os.path.expandvars(os.path.join(path, name)))
        if os.path.isdir(fullpath):
            raise Exception("Name already in use!")
        try:
            os.mkdir(fullpath)
        except Exception as e:
            #raise Exception("You don't have the permission to create this folder!")
            raise Exception(str(e))

    def create_file(self, path, name):
        # file with the same name existent?
        fullpath = os.path.expanduser(os.path.expandvars(os.path.join(path, name)))
        if os.path.exists(fullpath):
            raise Exception("Name already in use!")
        try:
            f = file(fullpath, "w")
            f.close()
        except Exception as e:
            raise Exception(str(e))
        

    def rename_folder(self, path, name):
        # file or folder
        if not os.path.isdir(path):
            raise Exception("Renaming file with folder function!")

        # folder with the same name existent?
        path = path if not path.endswith(os.sep) else path[:-1]
        fullpath = os.path.join(os.sep.join(path.split(os.sep)[:-1]), name)
        if os.path.exists(fullpath):
            raise Exception("Name already in use!")

        os.renames(path, fullpath)

    def rename_file(self, path, name):
        # file or folder
        if os.path.isdir(path):
            raise Exception("Renaming folder with file function!")

        # file with the same name existent?
        fullpath = os.path.join(os.sep.join(path.split(os.sep)[:-1]), name)
        if os.path.exists(fullpath):
            raise Exception("Name already in use!")

        os.renames(path, fullpath)

    def remove(self, path):
        if isinstance(path, list):
            for p in path:
                self.remove(p)
            return True

        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

    def compress(self, path, paths, name):
        # paths has to be a list of strings
        paths = paths if isinstance(paths, list) else [paths]

        path = path if not path.endswith(os.sep) else path[:-1]

        fullpath = os.path.join(path, "%s.zip" % name)

        if os.path.exists(fullpath):
            raise Exception("Name already in use!")

        archive = ZipFile(fullpath, "w")

        path = path if path.startswith(os.sep) else path
        for p in paths:
            if p is None or p == "":
                continue
            p = p if p.startswith(os.sep) else os.sep + path
            if os.path.isdir(p):
                for elem in os.listdir(p):
                    fullp = os.path.join(p, elem)
                    if os.path.isdir(fullp):
                        paths.append(fullp)
                    else:
                        ap = fullp[len(path):] if fullp.startswith(path) else fullp
                        archive.write(fullp, ap)

            ap = p[len(path):] if p.startswith(path) else p
            archive.write(p, ap)

        archive.close()

    def paste(self, path, target, cut):
        if isinstance(target, list):
            for p in target:
                self.paste(path, p, cut)
            return True

        fulltarget = os.path.join(path, target.split(os.sep)[-1])

        if os.path.exists(fulltarget):
            raise Exception("Name already in use!")

        if os.path.isdir(target):
            shutil.copytree(target, fulltarget)
            if cut:
                shutil.rmtree(target)
        else:
            shutil.copy2(target, path)
            if cut:
                os.remove(target)

    def save_file_content(self, path, content, force=True):
        path = os.path.expandvars(os.path.expanduser(path))
        # check if file already exists
        if os.path.exists(path) and not force:
            return False
        out = open(path, "wb")
        out.write(content)
        out.close()
        return True

    def get_file_content(self, path):
        path = os.path.expandvars(os.path.expanduser(path))
        f = open(path, "r")
        content = f.read()
        f.close()
        return content

    def get_mtime(self, path):
        path = os.path.expandvars(os.path.expanduser(path))
        return os.path.getmtime(path)

    def is_browser_file(self, path):
        extension = path.split(".")[-1]
        return extension in FileSystem.BROWSER_EXTENSIONS

    def handle_file_name_collision(self, name, path):
        # collision?
        files = os.listdir(path)
        if name not in files:
            return name

        # when this line is reached, there is a collision!

        # cut the file extension
        extension = name.split(".")[-1]
        prename = None
        if name == extension:
            extension = ""
            prename = name
        else:
            prename = name.split("." + extension)[0]

        # has the name already a counter at its end?
        hasCounter = False
        preprename = None
        counter = prename.split("_")[-1]

        if counter != prename:
            try:
                counter = int(counter)
                hasCounter = True
                preprename = "_".join(prename.split("_")[:-1])
            except:
                pass

        if hasCounter:
            # increment and try again
            counter += 1
            newname = "%s_%d%s" % (preprename, counter, "" if extension == "" else "." + extension)
        else:
            newname = "%s_1%s" % (prename, "" if extension == "" else "." + extension)

        # return
        return self.handle_file_name_collision(newname, path)


def string_compare(a, b):
    if a == b:
        return 0
    elif a > b:
        return 1
    else:
        return -1

def file_compare(a, b):
    if not a.startswith('.') and not b.startswith('.'):
        return string_compare(a, b)
    elif a.startswith('.') and b.startswith('.'):
        return string_compare(a, b)
    elif a.startswith('.') and not b.startswith('.'):
        return 1
    elif not a.startswith('.') and b.startswith('.'):
        return -1
