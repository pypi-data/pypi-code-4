import os
import os.path as path

def ensure_directory(filename):
    file_path = path.dirname(filename)
    if not path.exists(file_path):
        os.makedirs(file_path)