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
from filter.merging import MergeFile

# The problem of grouping songs
#
# well the first problem is that you should group the songs, so that it doesn't
# matter a which song you start or somthing like that. So it is very important, 
# that no song is worth more then another song for a reason that doesn't have to
# do with the song itsself. Let's assume
#
#        (a)
# 33%  /     \  66%
#    (b)-----(c)
#        66%
#  
# we could NOT go and say we start at b and group it only with, let's say;
# all songs that have a relation higher 50%. If we did so it would matter
# where we started and the result would be different starting at c.
#
# A fairly simple solution is to just go along the chain of high relations
# and group that way.
#
# But this leads to the following problem, that long chains can lead to
# totally different songs being grouped.
#
# There is this great song Wonderful World (WW) by Armstrong and Sam Cooke,
# some let's assume they were released in the following way, how would we 
# group the songs if only tags would matter?
# 
#  WW              66%      WW
#  Sam Cooke  (d) <---> (c) Sam Cooke
#  Album B     ^  \   /  ^  Album Mix
#              |   \ /33%|
#          33% |    x    | 66%
#              |   / \33%|
#  WW          v  /   \  v  WW
#  Armstrong  (a) <---> (b) Armstrong
#  Album A         66%      Album Mix
#
# Obviously the right grouping would be a,b and c,d but how is the computer
# supposed to know such a thing? If we replace the names by random letters
# how would we get the grouping right?
#
# Well we can state that the group a,b and c,d do make sense for a computer,
# since the elements of the group are strongly related (66%) among eachother.
# Interesting is that the groups a,d and b,c would not be stronly related,
# neither would be a,c and b,d. So if we knew that we would have to form
# two groups we could get the right result.
#
# This wouldn't work anymore if we removed d. Then there would be no difference
# between an a,b and c or an a and b,c grouping. So that case seems to be pretty
# unsolveable due to the lack of information and maybe a grouping of all of them
# would be the thing to do, or a grouping of none of them.
# 
# Let's introduce the average group similarity AGS.
# It is calculated by adding up all the connections that exist in a group
# and then dividing the result by the amount of relations.
#
# The a,b,c,d example above shows a relatively low AGS for grouping all songs.
# 
# AGS(a,b,c,d) = ( 3*33%+3*66% )/6 = 50%
#
# The less elements we put in a group the higher our AGS can be. I assume that
# would be 100% if there was a single element group since really the AGS is 
# representing how similar the elements of the group are, which is with one
# element 100%.
#
# In the example with only 3 elements our AGS would be rather high grouping all
# the items together.
#
# AGS(a,b,c) = ( 33%+2*66% )/3 = 55%
#
# With only two elements, the highest would be
#
# AGS(a,b) = 66%
#
# The total AGS tAGS, being the average AGS of all groups 
#
# 
# Well maybe be chaining isn't too bad. After all it is non discriminating,
# simple to implement and has relatively view realworld cases that I could think
# of it really failing to do its job.

def merge_by_md5(mfs):
	"""
	Merge all files that have the same md5 hash.
	`mfs` represents all files that need to be merged.
	Make sure those files are sorted by their md5 hash!
	"""
	if len(mfs)==0:
		return []
	else:
		mergefile = mfs[0]
		result = [mergefile]
		md5 = mfs[0].flags['md5id']

		for mf in mfs[1:]:
			if md5 != mf.flags['md5id']:
				mergefile = mf
				result.append(mergefile)
				md5 = mf.flags['md5id']
			mergefile.merge_with_mergefile(mf)
	return result

def tag_similarity(t1,t2):
	return 1

def find_tagwise_similar_files(mf,mfs,level):
	"""
	Finds files similar to the passed `mf`.
	`mfs` is a list of all files that will be compared to the tags of `mf`.
	If the similarity of the tags is > level, they count as similar.
	Return a tupple containing a list of similar files and a list of
	unsimilar files.
	The similar files will include `mf` for sure
	"""

	# this algorythm moves all similar entries from the mfs to the similar list
	similar = [mf]
	for s in similar:
		for i in xrange(len(mfs)):
			if tag_similarity(s,mfs[i]) > level:
				similar.append(mfs[i])
				del mfs[i]

	return similar,mfs

def merge_by_similar_tags(mfs,level):
	result = []
	while len(mfs)>0:
		mf = mfs[0]
		del mfs[0]
		similar,mfs = find_tagwise_similar_files(mf,mfs,level)
		for s in similar:
			mf.merge_with_mergefile(s)
		result.append(mf)
	return result

def merge_by_flag_and_tags(mfs,level,flag):
	"""
	Merge all files that have the same `flag` and similar tags.
	`mfs` represents all files that need to be merged.
	"""
	if len(mfs)==0:
		return []
	else:
		mfs.sort(lambda a,b : int(a.flags[flag]-b.flags[flag]))
		mergefile = mfs[0]
		result = []
		group = [mergefile]
		flagval = mfs[0].flags[flag]
		for mf in mfs[1:]:
			if flagval != mf.flags[flag]:
				# a group just ended here. Check for similarity				
				result.extend(merge_by_similar_tags(group,level))
				# a new group starts here
				mergefile = mf
				group = [mergefile]
				flagval = mf.flags[flag]
			else:
				group.append(mf)

		# here ends the very last group
		result.extend(merge_by_similar_tags(group,level))
	return result

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
			# don't filter all entries with the flag being None
			i=0
			while i<len(mfs):
				if mfs[i].flags[flag] == None:
					nullmfs.append(mfs[i])
					del mfs[i]
				else:
					i=i+1

			# do the actual filtering
			if opts.filter.find(k) != -1:
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

