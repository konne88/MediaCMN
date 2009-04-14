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

from share.entries.tagcomp import tag_similarity
from entries import Tag, MergeFiles

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

def filter_unchecked(gs):
	dfs = []
	for g in gs:
		fs = g.files
		
		while len(fs) != 1:
			dfs.append( MergeFiles(fs[0].id,fs[1].id) )
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
					dfs.append( MergeFiles(fs[i].id,fs[p].id) )
					del fs[p]
				else:
					p+=1	
			i+=1
	
	return dfs

