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
from filter.merging import merge_by_flag_and_tags, merge_by_md5, MergeFile

def main(opts):
	try:
		opts.print_init()
		db = index.FilterIndex(opts.index,opts.user,opts.pw)
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
			mfs.append(MergeFile(db.get_file(
				fileid, flags
			)))

		# Apply all the needed filters
		for k,flag,f,t in (('m','md5id',merge_by_md5,"md5 hashes"),
                            ('f', 'fingerprintid', lambda a : 
				merge_by_flag_and_tags(a,opts.level,'fingerprintid'),
				"fingerprints"),
			    ('p', 'puidid', lambda a : 
				merge_by_flag_and_tags(a,opts.level,'puidid'),
				"puids")
		):
			if opts.filter.find(k) != -1:
				# don't filter all entries with the flag being None
				i=0
				while i<len(mfs):
					print mfs[i].flags
					if mfs[i].flags[flag] == None:
						nullmfs.append(mfs[i])
						del mfs[i]
					else:
						i=i+1
				# do the actual filtering
				print "Merging files with duplicate %s."%t			
				mfs = f(mfs)
				opts.print_sep()

		# Merge with the leftout Files again
		mfs.extend(nullmfs)
		
		# Write merged files into the database
		for mf in mfs:
			db.add_song(mf.to_song())

		opts.print_done()
	except KeyboardInterrupt:
		opts.print_terminated()

if __name__ == "__main__":
	opts = options.FilterOptions()
	opts.parse_cmdline_arguments(sys.argv)
	main(opts)



#	if opts.filter.find('c') != -1:
#			print "Removing non existant file entries"
#			x = 0
#			files = db.get_all_file_index_connections()
#			for f in files:
#				fn = os.path.join(f.path,f.name+f.ext)
#				if not os.path.exists(fn):
#					print '\t',fn
#					db.remove_file(f.id)
#					x+=1
#			print x, "files removed"
#			print "----------------------------------------------"
#			print "Cleaning tags"
#			db.clean_tags()
#			print "----------------------------------------------"
#			print "Cleaning md5s"
#			db.clean_md5s()
#			print "----------------------------------------------"
#			print "Cleaning fingerprints"
#			db.clean_fingerprints()
#			print "----------------------------------------------"
#			print "Cleaning puids"
#			db.clean_puids()
#			print "----------------------------------------------"

#def get_matching_puid_tags(f):
#	fts = f.tags
#	if f.puid != None:
#		ptss = _get_puid_tags(f.puid)
#		if ptss == None:
#			return None			
#
#		bestSim = 0                 # best similarity
#		bestTags = []
#		for pts in ptss:
#			sim = tag_similarity(fts,pts)
#			if sim >= bestSim:
#				bestTags = pts
#				bestSim = sim
#				
#		if bestSim >= matchLevel:
#			if bestTags != []:
#				# at this point we got the best matching tags
#				return FileIdWithTags(f.id,bestTags)
#		
#		print '\tNo appropriate tags found for track on musicbrainz'
#	else:
#		print '\tNo puid exists for file'
#
	# at this point we couldn't find any tags for the file#
	# we just leave the old tags
#	return FileIdWithTags(f.id,fts)

