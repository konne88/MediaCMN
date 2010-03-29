# MediaCMN - Tools to create a consistent music library
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

class IndexedFile(object):
	def __init__(self,id,path,name,ext):
		self.taggroups = []
		self.id = id
		self.path = path
		self.name = name
		self.ext = ext
		self.flags = {}

	@property
    	def id(self):
        	return self._id

	@id.setter
	def id(self, value):
		self._id = value
		for group in self.taggroups:
			group.fileid = self._id

	def get_fullname(self):
		return os.path.join(self.path,self.name+self.ext)

	def __repr__(self):
		return self.get_fullname()

class TagGroup(object):
	def __init__(self,id,fileid):
		self.tags = []
		self.id = id
		self.fileid = fileid
		
	@property
    	def id(self):
        	return self._id

	@id.setter
	def id(self, value):
		self._id = value
		for tag in self.tags:
			tag.groupid = self._id

	def __repr__(self):
		return str(self.tags)

class FileTag(object):
	def __init__(self,id,value,type,source,groupid):
		self.id = id
		self.source = source
		self.value = value.strip()
		self.type = type
		self.groupid = groupid

	def __repr__(self):
		return str((self.value,self.type))

