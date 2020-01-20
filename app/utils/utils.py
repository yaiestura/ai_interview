import os
import glob

from app import app



# Folders


def empty_folder(directory):
    content = glob.glob(directory)
    for f in content:
        os.remove(f)

def is_folder_empty(directory):
    return True if (not os.listdir(directory)) else False


# Files


def allowed_file(filename, extensions):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in extensions:
        return True
    else:
        return False

def allowed_filesize(filesize, limit):

    if int(filesize) <= limit:
        return True
    else:
        return False