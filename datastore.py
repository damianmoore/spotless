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
import sqlite3
from hashlib import sha1

from node import Node
from utils import walk_directory


class Datastore():
    '''
    Contains all information regarding a filesystem directory tree. The data
    is stored in an SQLite database with each file and directory's
    information stored as a row in the 'nodes' table. Methods of this class
    that return data generally return types of class 'Node'.
    '''

    def __init__(self, dbpath='datastore.db'):
        self.connection = sqlite3.connect(dbpath)
        self.cursor = self.connection.cursor()
        try:
            self.cursor.execute('SELECT * FROM node LIMIT 1')
        except sqlite3.OperationalError:
            self.cursor.execute('CREATE TABLE node(path text unique, hash text, bytes smallint, type char(1), permissions smallint, created text, modified text, last_seen text, level smallint);')
            self.cursor.execute('CREATE INDEX node_path_idx ON node (path);')

    def add_or_update_node(self, node):
        '''
        Adds a Node to the database or updates it if it has already been added.
        You should have run update_info() on your Node before adding it.
        '''
        node_info = (
            node.path,
            node.hash,
            node.bytes,
            node.type,
            node.permissions,
            node.created,
            node.modified,
            node.last_seen,
            node.level,
        )
        self.cursor.execute('SELECT * FROM node WHERE path=?', (node.path,))
        if not self.cursor.fetchone():
            self.cursor.execute('''INSERT INTO node VALUES
                (?,?,?,?,?,?,?,?,?)
            ''', node_info)
        else:
            node_info = [n for n in node_info] + [node.path,]
            self.cursor.execute('''UPDATE node SET
                path=?, hash=?, bytes=?, type=?, permissions=?, created=?, modified=?, last_seen=?, level=?
            WHERE path=?''', node_info)

    def add_all_nodes_from_dir(self, path):
        path = os.path.abspath(path)
        for path in walk_directory(path):
            node = Node(path)
            node.update_info(self)
            self.add_or_update_node(node)
        self.update_dir_hashes()

    def get_node(self, path):
        path = os.path.abspath(path)
        self.cursor.execute('SELECT * FROM node WHERE path=?', (path,))
        row = self.cursor.fetchone()
        if row:
            node = Node(path)
            node.set_info_from_list(row)
            return node
        else:
            raise IOError('Path \'%s\' not in database.' % path)

    def update_dir_hashes(self):
        for dir_row in list(self.cursor.execute('SELECT path FROM node WHERE type=\'d\' ORDER BY level DESC')): #TODO: something better than converting to list
            dir_path = dir_row[0]
            node = self.get_node(dir_path)
            hash_list = []
            for child_row in self.cursor.execute('SELECT path, hash FROM node WHERE path LIKE \'%s%%\' ORDER BY path' % dir_path):
                child_path = child_row[0]
                child_hash = child_row[1]
                if child_path != dir_path:
                    hash_list.append('%s:%s' % (child_path, child_hash))
            hash_string = ';'.join(hash_list)
            node.hash = sha1(hash_string).hexdigest()
            self.add_or_update_node(node)

    def get_all_nodes(self):
        '''
        Generator that returns an iterator of all nodes
        '''
        for row in self.cursor.execute('SELECT * FROM node'):
            yield Node(row[0]).set_info_from_list(row)

    def num_items(self):
        self.cursor.execute('SELECT COUNT(path) FROM node')
        num = int(self.cursor.fetchone()[0])
        return num

    def clear(self):
        '''
        Removes all nodes from the database
        '''
        self.cursor.execute('DELETE FROM node')

    def __del__(self):
        self.connection.commit()
        self.cursor.close()

