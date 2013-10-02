#####################################################################
# zopyx.authoring
# (C) 2011, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

import os
import tempfile
import hashlib
import zipfile
import shutil
import util
import PIL.Image

def replaceImages(docx_filename):
    """ This method creates a new DOCX file containing minimized
        versions of the original images (at least for images larger 
        than 128x128px.
    """
      
    # temporary directory for holding the original (large-scale) images
    image_original_dir = tempfile.mkdtemp()

    # unzip DOCX file first
    tmpdir = tempfile.mkdtemp()
    ZF = zipfile.ZipFile(docx_filename)
    files_in_zip = ZF.namelist()[::]
    for name in ZF.namelist():
        basedir = os.path.dirname(name)
        destdir = os.path.join(tmpdir, basedir)
        destpath = os.path.join(tmpdir, name)
        if not os.path.exists(destdir):
            os.makedirs(destdir)
        file(destpath, 'wb').write(ZF.read(name))
    ZF.close()
    

    # process images
    hash2image= dict()
    imgdir = os.path.join(tmpdir, 'word', 'media')
    if os.path.exists(imgdir):

        for imgname in os.listdir(imgdir):
            fullimgname = os.path.join(imgdir, imgname)

            ext = os.path.splitext(fullimgname)[1].lower()

            if not ext in ('.png', '.jpg', '.gif'):
                print 'Can not handle %s files (%s) - REMOVED' % (ext, imgname)
                files_in_zip.remove(fullimgname.replace(tmpdir + '/', ''))
                os.unlink(fullimgname)
                continue

            pil_img = PIL.Image.open(fullimgname)
            if pil_img.size[0] < 128 and pil_img.size[1] < 128:
                continue

            # preserve original image
            shutil.copy(fullimgname, image_original_dir)

            # rescale image
            pil_img.thumbnail((100,100))

            # and replace original image with thumbnail        
            os.unlink(fullimgname)
            pil_img.save(fullimgname, quality=25)

            # store hash of thumbnail image with a reference to the original image
            md5 = hashlib.md5(file(fullimgname, 'rb').read()).hexdigest()
            hash2image[md5] = os.path.join(image_original_dir, imgname)

    # Create new .docx file with minimized images
    docx_zip_name = tempfile.mktemp(suffix='.docx')
    docx_zip = zipfile.ZipFile(docx_zip_name, 'w')
    for name in files_in_zip:
        docx_zip.writestr(name, file(os.path.join(tmpdir, name), 'rb').read())
    docx_zip.close()
    util.safe_unlink(tmpdir)
    return docx_zip_name, hash2image, image_original_dir 
