# About

archeck is a program that keeps track of all files in a directory (an
"archive"), making sure that every time the archeck is run that the
archive contains at least all the files it had last time archeck was run
on it. If any new files are added, archeck will start keeping track of
those in the same way.

I personally use it for backup verification. I have an "archive"
directory on my system which contains files that should never change
(pictures, music, stuff I wrote, backups of other smaller, frequently
changing directories...).  Anything that is put into the archive should
always remain there intact and never change or get lost. I wrote archeck
to enforce that and make sure my backups of my archive never lose
anything.

# Installation

You'll need Python 2.3 or higher (http://www.python.org) installed to
run it. Once you have that just copy archeck.py to wherever you like and
it should work. It might work on Windows too (I've never tested it
though).

# Usage

First, create an empty file which will be the archeck data file. You can
put this file anywhere you want.

Next, you can run archeck (at the command line) for the first time to
add stuff to that data file like this:

```
% archeck -r /path/to/archive/directory -d /path/to/data/file/just/created
```

It will spit out something like this:

```
archeck started at 2006-09-01 10:11:16
ADDED: b727678872225b9c680e766c809b9bf1: ['/music/song.mp3']
ADDED: f9dcc1b3b58c95fddfbc2989ea3361d5: ['/pics/zmachine_1024_768.jpg']
ADDED: e58d666df0d6cc6e87a7e48440d637e9: ['/text.txt']
ADDED: 5f4eb3810a3d9ed0e2ae992c423fea99: ['/music/mp3file.mp3']
4 file(s) were ADDED to the archive
0 file(s) were MISSING from the archive
SUCCESS: All files accounted for.
Data file saved to /tmp/datafile
archeck finished at 2006-09-01 10:11:16
```

If you look at that data file now you'll see some stuff in it.

Now to verify the archive, just run archeck the same way at any time:

```
% archeck -r /path/to/archive/directory -d /path/to/data/file/just/created
archeck started at 2006-09-01 10:11:45
0 file(s) were ADDED to the archive
0 file(s) were MISSING from the archive
SUCCESS: All files accounted for.
Data file saved to /tmp/datafile
archeck finished at 2006-09-01 10:11:45
```

If all files were accounted for it will display the SUCCESS message
above and save the new data file. If anything is missing (gone or
changed) however:

```
archeck started at 2006-09-01 10:12:28
ADDED: fecc3bc52df068273d9f2f544af9a3df: ['/text.txt']
MISSING: b727678872225b9c680e766c809b9bf1: ['/music/song.mp3']
MISSING: e58d666df0d6cc6e87a7e48440d637e9: ['/text.txt']
1 file(s) were ADDED to the archive
2 file(s) were MISSING from the archive
FAILURE: Some files were missing.
archeck finished at 2006-09-01 10:12:28
```

In this example I altered the 'text.txt' file and deleted 'song.mp3'.
Notice that it did not save a new datafile.

If the changes above were intentional, you can make archeck write out a
new datafile in the event of a failure like this with the -f option:

```
% archeck.py -r /tmp/archive -d /tmp/datafile -f /tmp/datafile.fail
archeck started at 2006-09-01 10:14:09
ADDED: fecc3bc52df068273d9f2f544af9a3df: ['/text.txt']
MISSING: b727678872225b9c680e766c809b9bf1: ['/music/song.mp3']
MISSING: e58d666df0d6cc6e87a7e48440d637e9: ['/text.txt']
1 file(s) were ADDED to the archive
2 file(s) were MISSING from the archive
FAILURE: Some files were missing.
Data file saved to /tmp/datafile.fail
archeck finished at 2006-09-01 10:14:09
```

Now if you approve of these changes and want archeck to proceed
normally, just copy the the fail datafile to the normal one and re-run:

```
% mv /tmp/datafile.fail /tmp/datafile
% archeck -r /tmp/archive -d /tmp/datafile -f /tmp/datafile.fail
archeck started at 2006-09-01 10:15:11
0 file(s) were ADDED to the archive
0 file(s) were MISSING from the archive
SUCCESS: All files accounted for.
Data file saved to /tmp/datafile
archeck finished at 2006-09-01 10:15:11
```

And if you want the log output above written to a log file, you can do
that with the -l option.

# Copyright and License

Copyright (C) 2006-2017 Steve Benson

archeck was written by Steve Benson.

archeck is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free
Software Foundation; either version 3, or (at your option) any later
version.

archeck is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
this program; see the file LICENSE.  If not, see <http://www.gnu.org/licenses/>.
