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

from share.entries import *

class Song(object):
	def __init__(self,id_,copyid,sources):
		self.id = id_
		self.copyid = copyid
		self.sources = sources
		self.duration = None
		self.artist = None
		self.release = None
		self.track = None
		self.date = None
		self.tracknumber = None
		self.genre = None
		self.label = None
		self.musictype = 'other'


class FileGroup(object):
	def __init__(self,value,files):
		self.value = value
		self.files = files

class MergeFiles(object):
	def __init__(self,stayFileId,oldFileId):
		self.stayFileId = stayFileId
		self.oldFileId = oldFileId

class FileIndexConnection(object):
	def __init__(self,id,path,name,ext):
		self.id = id
		self.path = path
		self.name = name
		self.ext = ext

