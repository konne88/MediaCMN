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
    """
    Represents a filesystem file that lies indexed in the database.
    `id` is the id the file got in the database index.
    `path` is the path to the file in the filesystem
    `name` is the actual name of the file without extension or path
    `ext`  is the extension of the file including the '.'
    `flags` stores some information about the file. Modules can
    define for their selfs what to add here.
    `taggroups` are groups of tags that can be associated with this file.
    All tags in a taggroup should either be all valid or all wrong.
    """

    def __init__(self,id,path,name,ext):
        """Creates a new file."""
        self.taggroups = []
        self.id = id
        self.path = path
        self.name = name
        self.ext = ext
        self.flags = {}

    @property
    def id(self):
        """Returns the id"""
        return self._id

    @id.setter
    def id(self, value):
        """
        Sets the id and makes sure all things stored in here that
        reference the id will be updated.
        """
        self._id = value
        for group in self.taggroups:
            group.fileid = self._id

    def get_fullname(self):
        """Returns the fullname of the file the index entry represents."""
        return os.path.join(self.path,self.name+self.ext)

    def __repr__(self):
        """Return printable representation"""
        return self.get_fullname()

class TagGroup(object):
    """All tags in a taggroup should either be all valid or all wrong.
    Holds a list of `FileTag`s and an `IndexFile`s id it is assigned to.
    """
    def __init__(self,id,fileid):
        """Creates a new `TagGroup`."""
        self.tags = []
        self.id = id
        self.fileid = fileid
        
    @property
    def id(self):
        """Return the id."""
        return self._id

    @id.setter
    def id(self, value):
        """
        Sets the id and makes sure all things stored in here that
        reference the id will be updated.
        """
        self._id = value
        for tag in self.tags:
            tag.groupid = self._id

    def __repr__(self):
        """Return printable representation."""
        return str(self.tags)

class FileTag(object):
    """
    A tag storing where it came from `source`, the `type` of tag it is,
    The id of the group it belongs too and a custom value.
    """
    def __init__(self,id,value,type,source,groupid):
        """Creates a new `FileTag`."""
        self.id = id
        self.source = source
        self.value = value.strip()
        self.type = type
        self.groupid = groupid

    def __repr__(self):
        """Return printable representation."""
        return str((self.value,self.type))

