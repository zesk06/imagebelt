#!/bin/env python
# encoding: utf-8

"""An image management library
"""
from __future__ import print_function

import argparse
import os
import glob
import multiprocessing
from PIL import Image

__version__ = '0.0.3'


def main():
    """The main
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('folder', help='The folder to thumbnailize')
    args = parser.parse_args()

    file_list = [os.path.join(args.folder, in_file)
                 for in_file in glob.glob('%s/**/*.jpg' % args.folder)]

    pool = multiprocessing.Pool()
    pool.map(thumbnail, file_list)


def thumbnail(image_file, max_size=1200):
    """thumbnailize an image_file
    """
    size = max_size, max_size
    back_file = os.path.splitext(image_file)[0] + '.backup'
    outfile = os.path.splitext(image_file)[0] + '.jpg'
    if not os.path.exists(back_file):
        try:
            my_image = Image.open(image_file)
            # shrink only if size if bigger
            if max(my_image.size) <= max_size:
                print('smaller than requested %s' % image_file)
                return
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
    main()
