spotless
========

Two-way directory synchronization (Work in progress)


Work done:
----------

*   Scanning a directory tree, creating an SQLite database containing all files and directories with associated meta-info.
*   Generating hashes for each file, then propagating the hashes of all children up to each directory parent.


Work remaining:
---------------

*   Compare datastores of two directories, transferring files that have changed in the right direction.
*   Configuration files for each synchronisation with local and remote datastores for each.
*   Detect deletions that happen between syncs so they can propagate.
*   Detect directories that have moved and just send those move events rather than re-transferring whole directories like rsync does - This is where hashing of files and directories becomes useful.
*   Use librsync to transfer partial file changes to and from remote machines over SSH.
*   Fast updating of filesystem datastore based on update times so full read of all files is not needed.
*   More advanced configuration settings such as directories to exclude and where to store cache/temporary data.
*   Create a daemon that monitors filesystem events (inotify etc.) to sync file changes immediately.
