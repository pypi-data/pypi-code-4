import boto

from PIL import Image
import tempfile

def resize_image_folder(bucket, key_prefix, pil_size):
    """ This function resizes all the images in a folder """
    con = boto.connect_s3()
    b = con.get_bucket(bucket)
    for key in b.list(key_prefix):
        key = b.get_key(key.name)
        print(key)
        if 'image' not in key.content_type:
            continue
        size = key.get_metadata('size')
        if size == str(pil_size):
            continue
        with tempfile.TemporaryFile() as big, tempfile.TemporaryFile() as small:
            print('resizing')
            # download file and resize
            key.get_contents_to_file(big)
            big.flush()
            big.seek(0)
            img = Image.open(big)
            img.thumbnail(pil_size, Image.ANTIALIAS)

            img.save(small, img.format)
            small.flush()
            small.seek(0)
            key.set_metadata('size', str(pil_size))
            key.set_contents_from_file(small, headers={'Content-Type': key.content_type})
