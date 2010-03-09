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

from share.options import IndexOptions
import os.path

class IndexerOptions(IndexOptions):
	def __init__(self):
		super(IndexerOptions,self).__init__()
		self.sources = []

		self._appname="Indexer"
		self._appargs+="[SOURCE...]"
		self._appdesc=("Index all files that are passed as a SOURCE or\n"
			"lay in a directory that is passed as a SOURCE\n"
			"the index is saved in a mysql database")

	def _handle_unused_args(self,args):
		for a in args:
			self.sources.append(os.path.abspath(a))
		return None
		
	def _set_option_value(self,opt,val):
		q = None
		r = super(IndexerOptions,self)._set_option_value(opt,val)
		if r != None:
			q = r
		return q

