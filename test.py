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

from datastore import Datastore
from node import Node
from utils import generate_hash, walk_directory

DB_NAME = 'test.db'
if os.path.exists(DB_NAME):
    os.remove(DB_NAME)
ds = Datastore(DB_NAME)
ds.clear()

print 'Can a Node be added to the Datastore and increase the row count?'
node = Node('testdata/hello.txt')
ds.add_or_update_node(node)
assert(ds.num_items() == 1)
print 'PASSED\n'

print 'Does a file Node generate an expected hash?'
assert(generate_hash(node) == '60fde9c2310b0d4cad4dab8d126b04387efba289')
print 'PASSED\n'

print 'If we run the Node\'s update_info() method do we see valid attributes set on the Node?'
node.update_info(ds)
assert(node.hash == '60fde9c2310b0d4cad4dab8d126b04387efba289')
assert(node.bytes == 14)
assert(node.type == 'f')
assert(node.permissions > 0)
assert(len(node.created) == 19)
assert(len(node.modified) == 19)
assert(len(node.last_seen) == 19)
print 'PASSED\n'

print 'Can the Datastore add all the Nodes of a given directory?'
ds.add_all_nodes_from_dir('testdata')
assert(ds.num_items() == 9)
print 'PASSED\n'

print 'Can we get back Node info that should have been added automatically?'
node = ds.get_node('testdata/photos/1/a/ok.png')
assert(node.hash == 'd431a0d7f885444f4b16357fbcba071cc6904481')
print 'PASSED\n'

print 'Do directories have hashes propogated up from children?'
node_path = os.path.abspath('testdata/photos/1')
node = ds.get_node(node_path)
assert(node.hash == 'b2682c7416b2b43222ffab86127337ce75a09f6d')
print 'PASSED\n'
