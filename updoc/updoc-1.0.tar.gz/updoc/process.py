import shutil
import os
import tarfile
import tempfile
import uuid
import zipfile
from django.conf import settings
from updoc.models import UploadDoc

__author__ = 'flanker'


def open_with_dir(dst_path):
    if not os.path.isdir(os.path.dirname(dst_path)):
        os.makedirs(os.path.dirname(dst_path))
    return open(dst_path, 'wb')


def get_tempfile(uploaded_file):
    temp_file = tempfile.NamedTemporaryFile()
    for chunk in uploaded_file.chunks():
        temp_file.write(chunk)
    temp_file.seek(0)
    return temp_file


def copy_to_path(in_fd, dst_path):
    with open_with_dir(dst_path) as out_fd:
        data = in_fd.read(4096)
        while data:
            out_fd.write(data)
            data = in_fd.read(4096)


def process_new_file(uploaded_file, request):
    """takes a UploadedFile object and returns a saved UploadDoc object

    """
    obj = UploadDoc()
    obj.user = request.user if request.user.is_authenticated() else None
    obj.uid = str(uuid.uuid1())
    basename = os.path.basename(uploaded_file.name)
    root = os.path.join(settings.MEDIA_ROOT, 'docs', obj.uid[0:2], obj.uid)
    obj.path = root
    try:
        obj.name = basename
        root += '/'

        if basename[-7:] in ('.tar.gz', '.tar.xz') or basename[-8:] == '.tar.bz2' or \
                basename[-4:] in ('.tar', '.tbz', '.tgz', '.txz'):
            temp_file = get_tempfile(uploaded_file)
            tar_file = tarfile.open(name=basename, mode='r:*', fileobj=temp_file)
            names = filter(lambda name_: os.path.join(obj.uid, name_).startswith(obj.uid), tar_file.getnames())
            common_prefix = '/'.join(os.path.commonprefix([name_.split('/') for name_ in names]))
            common_prefix_len = len(common_prefix)
            for member in tar_file.getmembers():
                if not os.path.join(obj.uid, member.name).startswith(obj.uid):
                    continue
                dst_path = root + member.name[common_prefix_len:]
                if member.isdir():
                    os.makedirs(dst_path, exist_ok=True)
                elif member.issym():
                    if not os.path.join(obj.uid, member.linkname).startswith(obj.uid):
                        continue
                    os.symlink(root + member.linkname[common_prefix_len:], dst_path)
                elif member.isfile():
                    copy_to_path(tar_file.extractfile(member), dst_path)
            tar_file.close()
            temp_file.close()
        elif basename[-4:] == '.zip':
            temp_file = get_tempfile(uploaded_file)
            zip_file = zipfile.ZipFile(temp_file, mode='r')
            uid = obj.uid
            names = list(filter(lambda zip_: os.path.join(uid, zip_.filename).startswith(uid), zip_file.infolist()))
            common_prefix = '/'.join(os.path.commonprefix([obj_.filename.split('/') for obj_ in names]))
            common_prefix_len = len(common_prefix)
            for obj_ in names:
                if obj_.filename[-1:] == '/':
                    continue
                copy_to_path(zip_file.open(obj_.filename), root + obj_.filename[common_prefix_len:])
            zip_file.close()
            temp_file.close()
        else:
            with open_with_dir(os.path.join(root, basename)) as out_fd:
                for chunk in uploaded_file.chunks():
                    out_fd.write(chunk)
        obj.save()
    except Exception as e:
        shutil.rmtree(root)
        raise e
    return obj
