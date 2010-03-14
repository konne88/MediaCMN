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

# how to use mysqldb
# http://mysql-python.sourceforge.net/MySQLdb.html
# http://www.python.org/dev/peps/pep-0249/

from entries import Song

class MergeFile(object):
	def __init__(self,file_ = None):
		self.taggroups = []
		self.sourcefiles = []
		self.flags = {}
		if file_ != None:
			self.add_source(file_)

	def add_source(self,file_):
		self.sourcefiles.append(file_.id)
		self.taggroups.extend(file_.taggroups)
		self.flags = file_.flags

	def to_song(self):
		song = Song(None,self.sourcefiles[0],self.sourcefiles)
		song.duration = 1337
		song.musictype = 'other'

		return song

	def merge_with_mergefile(self,mf):
		if self.flags != mf.flags:
			print "*********************************************************"
			print "*********************************************************"
			print "*********************************************************"
			print "*********************************************************"
			print "*********************************************************"
			print "*********************************************************"
			print "*********************************************************"
			print "*********************************************************"
			print
			print "ALERT! YOU ARE ABOUT TO ADD FILES WITH DIFFERENT FLAGS!!!"
			print
			print "*********************************************************"
			print "*********************************************************"
			print "*********************************************************"
			print "*********************************************************"
			print "*********************************************************"
			print "*********************************************************"
			print "*********************************************************"
		self.sourcefiles.extend(mf.sourcefiles)
		self.taggroups.extend(mf.taggroups)

