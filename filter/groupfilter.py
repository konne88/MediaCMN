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

from tags.tag import Tag
from tags.tagcomp import tag_similarity

# the idea of a group filter is the following
#
# a list of groups of files is passed to the filter_groups function
# it MAY then check if the tags of the files really support the 
# guess that files in the same group are the same
#
# the filter stores all files that need to be deleted in a list of
# deleteFile objects
# These objects hold the id of the file that is to be dropped and the 
# file-id that all tags of the dropped file are assinged to.

class FilterGroup:
	def __init__(self,value,files):
		self.value = value
		self.files = files
		
class FilterFile:
	def __init__(self,id,ts):
		self.id = id
		self.tags = ts

class DeleteFile:
	def __init__(self,id,newTagId):
		self.id = id
		self.newTagId = newTagId

def _create_group(res,i,gs):
	val = res[i][0]
	
	fs = []
	while True:
		i = _create_file(res,i,fs)
		if len(res) == i or res[i][0] != val:
			break
	
	# append the group only if it's value isn't NULL
	if val != None:
		gs.append( FilterGroup(val,fs) )
	
	return i

def _create_file(res,i,fs):
	id = res[i][1]
	
	ts = []
	while True:
		i = _create_tag(res,i,ts)
		if len(res) == i or res[i][1] != id:
			break
	
	fs.append( FilterFile(id,ts) )
	return i

def _create_tag(res,i,ts):
	value = res[i][2]
	type = res[i][3]
	source = res[i][4]
	
	if value != None:
		ts.append( Tag(value,type,source) )
	
	return i+1

def create_groups_from_flat_list(res):
	gs = []
	i = 0
	while i<len(res):
		i = _create_group(res,i,gs)
	
	return gs

def filter_unchecked(gs):
	dfs = []
	for g in gs:
		fs = g.files
		
		while len(fs) != 1:
			dfs.append( DeleteFile(fs[1].id,fs[0].id) )
			del fs[1]

	return dfs

def filter_check_groups_using_tags(gs,level):
	dfs = []
		
	# go througth all groups
	for g in gs:		
		fs = g.files
		i = 0
		# go througth all files in the group (iterator i)
				
		while i < len(fs):
			p = i+1
			# compare all files, after the current file, (iterator p)
			# to the current file
			while p < len(fs):
				# delete all files that are similar to the current file
				# because of the deletition we don't need
				# to increment in the iterator p				
				eq = tag_similarity(fs[i].tags,fs[p].tags)
				
				if eq > level:
					dfs.append( DeleteFile(fs[p].id,fs[i].id) )
					del fs[p]
				else:
					p+=1	
			i+=1
	
	return dfs

if __name__ == "__main__":
	print "Testing the results from group filtering checking with tags"
	print "-----------------------------------------------------------"
	print 
	print "filtering these files"
	print
	l = []
	l.append([0,1,u"Stir It Up","track",None])
	l.append([0,1,u"Bob Marley","artist",None])
	l.append([0,1,u"331056","duration",None])
	l.append([0,1,u"",None,None])
	l.append([0,1,u" Stir It Up",None,None])
	l.append([0,1,u"05 ","number",None])
	l.append([0,1,u"Bob Marley - 1994 - Legend","release",None])
	l.append([0,1,u"Bob Marley - Complete Discography From 1967 To 2002 [33 Full Albums] (Mp3 256Kbps)","artist",None])
	l.append([0,2,u"Stir It Up","track",None])
	l.append([0,2,u"Bob Marley","artist",None])
	l.append([0,2,u"336048","duration",None])
	l.append([0,2,u"",None,None])
	l.append([0,2,u" Stir It Up",None,None])
	l.append([0,2,u"08 ","number",None])
	l.append([0,2,u"Bob Marley - 1973 - Catch A Fire","release",None])
	l.append([0,2,u"Bob Marley - Complete Discography From 1967 To 2002 [33 Full Albums] (Mp3 256Kbps)","artist",None])
	l.append([0,3,u"Stir It Up","track",None])
	l.append([0,3,u"Bob Marley","artist",None])
	l.append([0,3,u"331056","duration",None])
	l.append([0,3,u"",None,None])
	l.append([0,3,u" Stir It Up",None,None])
	l.append([0,3,u"01 ","number",None])
	l.append([0,3,u"Bob Marley - 2002 - One Love, The Very Best Of","release",None])
	l.append([0,3,u"Bob Marley - Complete Discography From 1967 To 2002 [33 Full Albums] (Mp3 256Kbps)","artist",None])
	l.append([0,4,u"Stir It Up","track",None])
	l.append([0,4,u"Bob Marley","artist",None])
	l.append([0,4,u"329040","duration",None]) 
	l.append([0,4,u"",None,None])
	l.append([0,4,u" Stir It Up",None,None])
	l.append([0,4,u"03 ","number",None])
	l.append([0,4,u"Bob Marley - 1978 - Babylon By Bus","release",None])
	l.append([0,4,u"Bob Marley - Complete Discography From 1967 To 2002 [33 Full Albums] (Mp3 256Kbps)","artist",None])
	l.append([0,4,u"Stir It Up","track",None])
	l.append([0,4,u"Bob Marley","artist",None])
	l.append([0,4,u"329040","duration",None]) 
	l.append([0,4,u"",None,None])
	l.append([0,4,u" Stir It Up",None,None])
	l.append([0,4,u"03 ","number",None])
	l.append([0,4,u"Bob Marley - 1978 - Babylon By Bus","release",None])
	l.append([0,4,u"Bob Marley - Complete Discography From 1967 To 2002 [33 Full Albums] (Mp3 256Kbps)","artist",None])
	l.append([0,5,u"Stir It Up","track",None])
	l.append([0,5,u"Bob Marley","artist",None])
	l.append([0,5,u"03 ","number",None])
	l.append([0,5,u"Babylon By Bus","release",None])
	l.append([0,6,u"Come as you are","track",None])
	l.append([0,6,u"Roby Williams","artist",None])
	l.append([0,6,u"I have no clue","release",None])
	
	gs = create_groups_from_flat_list(l)
	
	for g in gs:
		print 'group: ',g.value
		for f in g.files:
			print '\tfile: ',f.id
			for t in f.tags:
				print '\t\t','"'+t.value+'"','-',t.type
	
	dfs = filter_check_groups_using_tags(gs,7)
	
	print
	print "these files would have been deleted:"
	print 
	
	for df in dfs:
		print df.id

