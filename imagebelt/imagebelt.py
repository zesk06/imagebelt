#!/bin/env python
# encoding: utf-8

"""An image management library
"""
import argparse
import os
import glob
import multiprocessing
from PIL import Image


def thumbnail(image_file, max_size=1200):
    """thumbnailize an image_file
    """
    size = max_size, max_size
    back_file = os.path.splitext(image_file)[0] + '.backup'
    outfile = os.path.splitext(image_file)[0] + '.jpg'
    if not os.path.exists(back_file):
        try:
            my_image = Image.open(image_file)
            print('backup to %s' % back_file)
            my_image.save(back_file, 'JPEG')
            my_image.thumbnail(size)
            my_image.save(outfile, 'JPEG')
            print('thumbnailize to %s' % outfile)
        except IOError:
            print('cannot create thumbnail for %s' % image_file)
        return
    print('already a backup file %s' % back_file)


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('folder', help='The folder to thumbnailize')
    ARGS = PARSER.parse_args()

    file_list = [os.path.join(ARGS.folder, in_file)
                 for in_file in glob.glob('%s/**/*.jpg' % ARGS.folder)]

    POOL = multiprocessing.Pool()
    POOL.map(thumbnail, file_list)
