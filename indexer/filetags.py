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

import re		#regex
import os.path

from tags.tag import Tag

# each tag consists of a type and a value and a source
# if no type is specified None is used
# source is where we got the tag
# use the following value for
def guess_from_path_and_name(path,name):
	res = []
		
	# split with '-' if it exists
	if name.count('-') > 0:
		fields = name.split('-')
		for field in fields:
			res.append(Tag(field,None,'filename'))
	
	# if '-' wasn't a seperator, we check if '_' is seperator
	# it only is if there are '_' and ' ' combined in the string
	# cause who would use '_' as ' ' if he uses ' ' too.
	elif name.count('_') > 0 and name.count(' ') > 0:
		fields = name.split('_')
		for field in fields:
			res.append(Tag(field,None,'filename'))
	
	# if there is no seperator, we use the full name as track		
	else:
		res.append(Tag(name,'track','filename'))

	# we mark all the fields that are a number only as 'number'
	r = re.compile('^\d{1,2}$')
	for field in res:
		if r.sub('',field.value)=='':
			field.type = 'tracknumber'
			break
	
	# now we search for a tracknumber that is most of the times
	# simply stored, seperated by a ' ' from the trackname
	# or another field
	r = re.compile('^\d{1,2}\s')
	for field in res:
		e = r.match(field.value)
		if e != None:
			res.append(Tag(e.group(),'tracknumber','filename'))
			field.value = r.sub('',field.value)
			break

	# delete all entries that look like md5 hashes 
	r = re.compile('^[0-9A-Fa-f]{32}$')
	if len(res)==1 and r.match(res[0].value) != None:
		del res[0]
	
	# now get tags from the directory name
	# if there are at least two sub directories, 
	# the first parent will be the release
	# and the grandparent will be the artist
	
	path, reldir = os.path.split(path)
	artdir = os.path.basename(path)
	
	if reldir != "" and artdir != "":
		res.append(Tag(reldir,'release','path'))
		res.append(Tag(artdir,'artist','path'))
	
	return res
	
if __name__ == "__main__":
	print "Testing the extraction of tags from a filename."
	print "-----------------------------------------------"
	print 
	s = (["/a/artist/release","01 Meer Sein"],
	["/artist/release","03-less_than_jake-overrated_(everything_is)"],
	["/a","13 the song_album"],
	["/","my_song"],
	["","10 All We Are"],
	["","10 kleine Nazis"],
	["","56251e9680e11aaa39714a4b0cbe7443"],
	["","abinullacht"])
	
	for i in s:
		print os.path.join(i[0],i[1])
		print guess_from_path_and_name(i[0],i[1])
		print
