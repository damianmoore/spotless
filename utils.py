# Copyright 2012 Damian Moore
#
# This file is part of Spotless.
#
# Spotless is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Spotless is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.


import os
from datetime import datetime
import hashlib


def hash_file(fh, algorithm, blocksize=65536):
    buf = fh.read(blocksize)
    while len(buf) > 0:
        algorithm.update(buf)
        buf = fh.read(blocksize)
    return algorithm.hexdigest()


def format_time_iso(date):
    return datetime.strftime(date, '%Y-%m-%d %H:%M:%S')


def format_filesize(num):
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')


def walk_directory(path, files_only=False):
    '''
    Generator that walks a directory tree yeilding the paths of child dirs
    and files.
    '''
    root_path = os.path.abspath(path)
    for root, dirs, files in os.walk(root_path):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.exists(file_path) and not os.path.islink(file_path): # Don't try symlinks etc.
                yield file_path
        for dir in dirs:
            if not files_only:
                dir_path = os.path.join(root, dir)
                yield dir_path


def generate_hash(node):
    if node.type == 'd':
        pass
    else:
        return hash_file(file(node.path, 'r'), hashlib.sha1())
