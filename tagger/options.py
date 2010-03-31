f# MediaCMN - Tools to create a consistent music library.
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

from share.options import CopyIndexOptions
from share.options import check

class TaggerOptions(CopyIndexOptions):
	def __init__(self):
		super(TaggerOptions,self).__init__()
		self.level = 0.0
		
		self._opts.append(('level','l',"NUMBER",
			"tags found using the puid of the file,\n"
			"are only assigned to the file, if the new tags are similar to the old ones.\n"
			"NUMBER is a value between 0 and 1. if 0 is passed, it doesn't matter,\n"
			"whether old or new tgs are similar. the closer the value is to 1 the\n"
			"more the old and the new tags need to be similar.",
			self.level))
					
		self._appdesc=("Filter an index, and save the result in this one,\n"
			"or in a new index.")

	def _set_option_value(self,opt,val):
		q = None
		if opt == 'level':
			v = check.make_float_between_zero_and_one(val)
		  	if v == None:
		  		print "The level argument is not a number between 0 and 1"
		  		q = 1
		  	else:
			  	self.level = val
		else:
			r = super(TaggerOptions,self)._set_option_value(opt,val)
			if r != None:
				q = r
		return q

