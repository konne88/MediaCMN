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

import os.path
import os
import shutil

from entries import Tag
from share.entries.tagcomp import find_best_tag_of_type

def get_file_infos(tags,minRating):
	# parse the tags
	infos = {
		u'track':None,
		u'release':None,
		u'artist':None,
		u'tracknumber':None,
		u'duration':None,
		u'date':None,
		u'genre':None
	}
	
	# save the tag values into the infos dict
	for k in infos:
		tag = find_best_tag_of_type(tags,k,minRating)
		if tag != None:
			v = tag.value
			if v == "":
				v = None
			infos[k] = v

	return infos

def get_new_relativename(target,name,infos,strict):
	#define what s.th. is named if it's empty
	defaults = {
		u'track':u'Unknown Track',
		u'release':u'Unknown Release',
		u'artist':u'Unknown Artist',
		u'duration':u'0',
		u'tracknumber':u'0',
		u'date':u'Unknown Date',
		u'genre':u'Unknown Genre'
	}

	# replace info dict values with their defaults etc
	# basically make them human readable and sortable
	for k in infos:
		# set defaults
		if infos[k] == None:
			infos[k] = defaults[k]
			
		# remove the directory seperators, 
		# so that names can't change directory structure
		
		infos[k] = infos[k].replace(u'/',u'-')
		
		# make tracknumber 2 digits
		if k == u'tracknumber':
			if len(infos[k]) == 1:
				infos[k] = u"0"+infos[k]
	
	# create the filename from the template string
	reps = {
		u't':infos[u'track'],
		u'r':infos[u'release'],
		u'a':infos[u'artist'],
		u'n':infos[u'tracknumber'],
		u'd':infos[u'duration'],
		u'%':u'%'
	}
	
	relativename = u""
	lastCharWasPercent = False
	for c in name:
		if c == '%':
			lastCharWasPercent = True
			continue
			
		if lastCharWasPercent == True:
			try:
				relativename += reps[c]
			except KeyError:
				relativename += u'%'+c				
		else:
			relativename += c
		
		lastCharWasPercent = False
	
	# remove illegal chars from the filename ('/' was removed earlier)
	nogoes = None
	if strict >= 1:
		nogoes = (u'\0',u'\\',u':',u'*',u'?',u'"',u'<',u'>',u'|')
	else:
		nogoes = (u'\0',)
	
	for n in nogoes:
		relativename = relativename.replace(n,u'-')
	
	# check if the lenghts of directories and filenames are right,
	# 220 is to low of a value allowing for the extension
	# http://en.wikipedia.org/wiki/Comparison_of_file_systems#cite_note-note-12-8
	pathParts = relativename.split('/')
	for p in pathParts:
		if len(p) > 220:
			p = p[0:220]
	relativename = '/'.join(pathParts)
	
	# check if file exists and if so ...
	ext = ".mp3"
	
	# ... don't do anything, if duplicate files should be skiped
		
	# ... to use if duplicate files should be renamed
	#x = 1
	#while True:
	#	if os.path.exists(os.path.join(target,relativename+ext)):
	#		ext = " (exists "+unicode(x)+").mp3"
	#		++x
	#	else:
	#		break
	
	return relativename+ext

def create_nonexistant_dirs(target,relativename):
	# create all the directories the file lies in	
	path = os.path.dirname(relativename)
	pathParts = path.split('/')
	usedParts = target
	for p in pathParts:
		usedParts = os.path.join(usedParts,p)
		
		if not os.path.isdir(usedParts):
			os.mkdir(usedParts)

