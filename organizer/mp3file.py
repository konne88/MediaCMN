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

import os
from subprocess import *

from mutagen.easyid3 import EasyID3
import mutagen.easyid3 as easyid3 

def is_file_mp3(fullname):
	argv = [u"file",fullname]
	# the file cmd prints the filename and adds the filetype after a ':'
	finfo = Popen(argv, stdout=PIPE).communicate()[0].split(':',1)
	
	return len(finfo) == 2 and finfo[1].find("MP3 encoding") != -1

def transform_to_mp3(fullname,tempname):
	try:
		os.remove(tempname)
	except OSError:
		pass # temp file doesn't exist

	argv = [u"ffmpeg",u"-i",fullname,u'-ab','128k',tempname]
	Popen(argv, stdout=PIPE,stderr=PIPE).communicate()

def set_file_id3_tags(fullname,infos):
	# delete the old version tags
	easyid3.delete(fullname, delete_v1=True, delete_v2=True)
	
	mapping = {
		u'track':u'title',
		u'release':u'album',
		u'artist':u'artist',
		u'tracknumber':u'tracknumber',
		u'genre':u'genre',
		u'date':u'date'
	}
	
	# set the mp3 metatags
	meta = EasyID3()
	
	for k in infos:
		try:
			meta[mapping[k]] = infos[k]
		except KeyError:
			pass
	
	meta.save(fullname)

