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
from share.options import check
import os.path

class OrganizerOptions(IndexOptions):
	def __init__(self):
		super(OrganizerOptions,self).__init__()
		self.target = None
		self.filepattern = '%a/%r/%n-%t'
		self.restrictions = 0
		self._appname = "Organizer"
		
		self._opts.append(('filepattern','f',"PATTERN",
			"the PATTERN defines which rules are applied in order to build\n"
			"the filenames of the files added to the library\n"
			"all occurances of the following %, character combinations\n"
			"are replaced by their value\n"
			"%t  the track name\n"
			"%r  the release name\n"
			"%a  the artist's name\n"
			"%n  the tracknumber in the release\n"
			"    if tracknumber is 0-9, 0 is prepended\n"
			"%d  the duration of the song\n"
			"%%  is replaced by a '%' character\n"
			"file extension (.mp3) is added automatically",
			self.filepattern))

		self._opts.append(('restrictions','r',"INTEGER",
			"sets the restrictions that exist for valid filenames.\n"
			"INTEGBER can be any of the following:\n"
            "0    to use if the library is saved on a UNIX filesystem\n"
            "     just like ext3. the characters\n"
            "     / and NUL\n"
            "     are removed from filenames\n"
            ">=1  to use if the library is saved on a WINDOWS filesystem\n"
            "     just like ntfs,fat32. the characters\n"
            "     / \\ : * ? \" < > | and NUL\n"
            "     are removed from filenames",
            self.restrictions))

		self._appargs+="TARGET"
		self._appdesc=("Organize the files in the index in a library\n"
			"which is created on the filesystem in the TARGET directory.\n"
			"All songs copied into the library are converted to MP3!")

	def _handle_unused_args(self,args):
		q = None
		if len(args) == 1:
			self.target = os.path.abspath(args[0])
			if not os.path.isdir(self.target):
				print "TARGET is not a directory"
				q = 1
		else:
			print "You must specify exactly one TARGET for the library to be saved in."
			q = 1
		return q
		
	def _set_option_value(self,opt,val):
		q = None
		if opt == 'restrictions':
			v = check.make_positive_int(val)
			if v == None:
				print "Passed restriction param is not an integer."
				quit = 1
			else:
				self.restrictions = v
		elif opt == 'filepattern':
			self.filepattern = val
		else:
			r = super(OrganizerOptions,self)._set_option_value(opt,val)
			if r != None:
				q = r
								
		return q

