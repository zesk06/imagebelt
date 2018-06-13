#!/bin/env python
# encoding: utf-8

"""An image management library
"""
from __future__ import print_function

import argparse
import os
import glob
import json
import logging
import multiprocessing
import subprocess

from path import Path

from PIL import Image


logging.basicConfig()
logging.root.setLevel(logging.INFO)


def main():
    """The main
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="goes to verbose", default=False
    )
    subparsers = parser.add_subparsers(dest="subcommand")

    reduce_parser = subparsers.add_parser("reduce", help="to reduce image")
    reduce_parser.add_argument("folder", help="The folder to thumbnailize")
    reduce_parser.set_defaults(func=reduce_f)

    metadata_parser = subparsers.add_parser("db", help="read metadata from JSON")
    metadata_parser.add_argument("json", help="the json file")
    metadata_parser.set_defaults(func=json_to_image)

    args = parser.parse_args()
    if args.verbose:
        logging.root.setLevel(logging.DEBUG)
        logging.info("Going to verbose")
    logging.debug(args)
    if not hasattr(args, "func"):
        parser.print_usage()
        exit(1)

    args.func(args)


def json_to_image(args):
    """Transfer json metadata to image EXIF data"""
    json_path = Path(args.json)
    with open(json_path, "r") as json_f:
        json_obj = json.load(json_f)
    parent_dir = json_path.parent
    for media in json_obj["media"]:
        print(parent_dir / media["title"])
        img_path = parent_dir / media["title"]
        title = media["description"]
        description = media["description"]
        tags = media["tags"]
        comments = [
            "%s:%s" % (com["author"], com["comment"]) for com in media["comments"]
        ]
        lat_lon = None
        if "geoInfo" in media and media["geoInfo"]:
            latitude = media["geoInfo"]["latitude_"]
            longitude = media["geoInfo"]["longitude_"]
            lat_lon = (latitude, longitude)
        exiftool(
            img_path,
            title=title,
            description=description,
            tags=tags,
            comments=comments,
            lat_lon=lat_lon,
        )


def exiftool(
    image_path, title, description=None, tags=None, comments=None, lat_lon=None
):
    """Change image metadata using exiftool"""
    cmd = ["exiftool", f"{image_path}"]
    if title:
        cmd += [f'-Title="{title}"']
    if description:
        cmd += [f'-Description="{description}"']
        cmd += [f'-ImageDescription="{description}"']
    if comments:

        cmd += ['-UserComment="%s"' % ".".join(comments)]
        cmd += ['-XPComment="%s"' % ".".join(comments)]
    if tags:
        for tag in [tag.strip() for tag in tags]:
            cmd += [f'-Subject="{tag}"']
            cmd += [f'-HierarchicalSubject="{tag}"']
            cmd += [f'-Keywords="{tag}"']
    if lat_lon:
        cmd += ['-GPSLatitude="%s"' % lat_lon[0], '-GPSLongitude="%s"' % lat_lon[1]]
    # to change date:
    # -alldates="20100101 080000" -filemodifydate="20100101 080000"
    logging.debug("calling %s", cmd)
    subprocess.call(
        cmd, cwd=image_path.parent, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )


def reduce_f(args):
    """reduce images within a folder"""
    file_list = [
        os.path.join(args.folder, in_file)
        for in_file in glob.glob("%s/*.jpg" % args.folder)
    ]
    pool = multiprocessing.Pool()
    pool.map(thumbnail, file_list)


def thumbnail(image_file, max_size=1200):
    """thumbnailize an image_file
    """
    size = max_size, max_size
    back_file = os.path.splitext(image_file)[0] + ".backup"
    outfile = os.path.splitext(image_file)[0] + ".jpg"
    if not os.path.exists(back_file):
        try:
            my_image = Image.open(image_file)
            # shrink only if size if bigger
            if max(my_image.size) <= max_size:
                print(f"smaller than requested {image_file}")
                return
            print(f"back to {back_file}")
            my_image.save(back_file, "JPEG")
            my_image.thumbnail(size)
            my_image.save(outfile, "JPEG")
            print(f"thmb to {outfile}" % outfile)
        except IOError:
            print(f"cannot create thumbnail for {image_file}")
        return
    print(f"already a backup file {back_file}")


if __name__ == "__main__":
    main()
