What MediaCMN is
===============================

MediaCMN provides tools to create a consistent music library.
In detail these tools:
Index all audio files of certain directories,
Find duplicate files,
Tag the files using musicbrainz,
Organize the audio files in a filesystem.

If you run into problems
===============================

Send bugs and help requests to 
konnew@gmx.de

I'll be very happy to help you, even if you are new to linux. 
Since the project is still relatively small bugs should be fixed 
at most a week after they are reported.

Quickstart
===============================

Read INSTALL.txt for information on the librarys you need.

Open a terminal.
Each line starting with '>' means, 'type into commandline'

Change to the directory of the extracted source.

> cd /where/you/put/it

Copy cmnfingerprinter to /usr/bin/ or /usr/local/bin/
You need to be root to do so

> sudo cp cmnfingerprinter /usr/local/bin/

Create a mysql database to store the index.

Start mysql prompt:

> mysql

Create the database by typing

> CREATE DATABASE cmn_index;

The next step is to index the files you want to use.
This takes very long, on my kind of old pc about 4 seconds per file,
so if you want to test MediaCMN try using a small directory of about 
20 files to begin with.

> ./cmnindexer.py -dn /path/to/your/music/files/ /and/another/one/ /or/directly/the/file/to/index.ext

Now find duplicate entries, executing

> ./cmnfilter.py -f smfpc

Now find tags on musicbrainz

> ./cmntagger.py

Finally organize the library, storing it on a harddrive

> ./cmnorganizer.py -r 1 /path/to/the/new/library/

How it works
===============================

Indexing
--------

First of all, the indexer is used to index all files of 
certain directories. This tool stores the following information
about the audio-file in a mysql database.

filename
filesize
md5-hash
music-dns fingerprint
music-dns puid
tags (extracted from filename, metadata and musicdns service)

Filtering
---------

After indexing the files a filter may be run that deletes all 
duplicate entries from the database. To do so it compares md5 hash,
puids, fingerprints and tags.

Tagging
-------

Once duplicated files are removed, the musicbrainz library is used 
to consistently tag the files.

Organizing
----------

Finally the organizer is used to copy all files that are still in 
the index into a filesystem based library. 
Doing so all audio-files are converted to mp3 using ffmpeg.

Keep in mind
===============================

 * Make sure you are online while running the commands, otherwise 
   indexing and tagging may fail.

 * If you don't know what to do, use the command with the -h flag
   or ask for help
   
A word on stability
===============================

The tools were tested with 30.000 files in multiple directories on
several harddrives. The files were mostly mp3's (also a couple of wma's),
desktop.ini's, cover images and maybe some movies. The library included tons
of duplicates so that it shrunk to about 6000 files after running all tools.
The tool did a pretty good job, as far as I can see, but it might not work 
that well with other audio-file formats.

Digging deeper
===============================

Read the source!!! Start with the main files for the tools, the ones you execute,
and see what they include.
The source doesn't follow any code style rules, since I'm pretty new to python.

