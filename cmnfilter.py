#!/usr/bin/env python

# MediaCMN - Tools to create a consistent music library.
# Copyright (C) 2009 Konstantin Weitz
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import sys
import os

import filter.index as index
import filter.options as options
from filter.merging import merge_files_by_flag_and_tags,    \
                           merge_files_by_md5,          \
                           merge_songs_by_properties,       \
                           MergeFile

def main(opts):
    try:
        opts.print_init()
        db = index.FilterIndex(opts.index_reference)
        # recreate all tables that have something to do with the filter,
        # so we don't have all the old stuff in the way
        db.drop_tables()
        db.create_tables()

        # a list of all the available mergefiles this is the main 
        # variable since it keeps track of what has been merged
        mfs = []
        # list of all mergefiles with the flag being None. 
        nullmfs = []

        # figure out which flags we need to load from the index
        flags = []
        for k,v in (('m','md5id'),('p','puidid'),('f','fingerprintid')):
            if opts.filter.find(k) != -1:
                flags.append(v)

        # get all music files from the index
        fileids = db.get_music_file_ids_md5_ordered()
        for fileid in fileids:
            mf = MergeFile(db.get_file(fileid, flags))
            mfs.append(mf)

        # variable holding merges for each step so we can print that
        count = 0
        # Apply all the needed filters
        for k,flag,f,t in (('m','md5id',merge_files_by_md5,"md5 hashes"),
                            ('f', 'fingerprintid', lambda a : 
                merge_files_by_flag_and_tags(a,opts.level,'fingerprintid'),
                "fingerprints"),
                ('p', 'puidid', lambda a : 
                merge_files_by_flag_and_tags(a,opts.level,'puidid'),
                "puids")
        ):
            if opts.filter.find(k) != -1:
                # don't filter all entries with the flag being None
                i=0
                while i<len(mfs):
                    if mfs[i].flags[flag] == None:
                        nullmfs.append(mfs[i])
                        del mfs[i]
                    else:
                        i=i+1
                # do the actual filtering
                print "Merging files with duplicate %s."%t
                count = len(mfs)
                mfs = f(mfs)
                print "%d succesful merges."%(count-len(mfs))
                opts.print_sep()

        # Merge with the leftout Files again
        mfs.extend(nullmfs)

        # Create songs and therefore also decide on one set of tags
        songs = []      
        for mf in mfs:
            songs.append(mf.to_song())
        
        # Merge files that have the same set of tags
        if opts.filter.find('t') != -1:
            print "Merging files with duplicate tags."
            count = len(songs)      
            songs = merge_songs_by_properties(songs)
            print "%d succesful merges."%(count-len(songs))
            opts.print_sep()

        # Write merged files into the database
        for s in songs:
            db.add_song(s)

        opts.print_done()
    except KeyboardInterrupt:
        opts.print_terminated()

if __name__ == "__main__":
    opts = options.FilterOptions()
    opts.parse_cmdline_arguments(sys.argv)
    main(opts)

