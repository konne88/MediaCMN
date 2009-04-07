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

from musicbrainz import get_puid_tags
from tags.tag import Tag
from tags.tagcomp import tag_similarity

class TaggerFile:
	def __init__(self,id,puid,tags):
		self.id = id
		self.puid = puid
		self.tags = tags

class NewTagFile:
	def __init__(self,id,tags):
		self.id = id
		self.tags = tags

def _create_file(res,i,fs):
	id = res[i][0]
	puid = res[i][1]
	
	ts = []
	
	while True:
		i = _create_tag(res,i,ts)
		if len(res) == i or res[i][0] != id:
			break
			
	fs.append( TaggerFile(id,puid,ts) )
	return i

def _create_tag(res,i,ts):
	value = res[i][2]
	type = res[i][3]
	rating = res[i][4]
	
	if value != None:
		ts.append( Tag(value,type,rating) )
	
	return i+1

def create_files_from_flat_list(res):
	fs = []
	i = 0
	while i<len(res):
		i = _create_file(res,i,fs)
	
	return fs

def get_matching_puid_tags(f,matchLevel):
	fts = f.tags
	if f.puid != None:
		ptss = get_puid_tags(f.puid)
		bestSim = 0                 # best similarity
		bestTags = []
		for pts in ptss:
			sim = tag_similarity(fts,pts)
			if sim >= bestSim:
				bestTags = pts
				bestSim = sim
				
		if bestSim >= matchLevel:
			if bestTags != []:
				# at this point we got the best matching tags
				return NewTagFile(f.id,bestTags)
		
		print '\tNo appropriate tags found for track on musicbrainz'
	else:
		print '\tNo puid exists for file'

	# at this point we couldn't find any tags for the file
	# we just leave the old tags
	return NewTagFile(f.id,fts)

