#!/usr/bin/env python

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

import getopt, sys
import os
import shutil

import organizer.index as index
import organizer.options as options
from organizer.file import get_new_filename,    \
			   get_copyfile,    \
			   copy_file_to_target

def check_sources(files):
	# print sources
	for f in files:
		print "\tSource  :",f
		if not os.path.exists(f.get_fullname()):
			print "Source doesn't exist"
			return False
	return True
	
def main(opts):
	try:
		opts.print_init()
		db = index.OrganizerIndex(opts.index_reference)
		ids = db.get_song_ids()
		for id_ in ids:
			print u"Organizing file",id_,u":"
			song,files = db.get_song_with_sourcefiles(id_)
			if check_sources(files):
				# generate new filename
				filename = get_new_filename(song, opts.target,
					opts.filepattern, opts.restrictions)
				if filename == None:
					print "Generation of a new filename failed."
				else:
					# find the source to copy from
					copyfile = get_copyfile(files)
					copyname = copyfile.get_fullname()
					print "\tCopyfile:",copyfile
					print "\tFilename:",filename
					# copy and do all files transformations
					ismp3 = copyfile.flags['musictype'] == 'mp3'
					if ismp3 == False:
						print "\tNeeds to be converted to mp3."
					copy_file_to_target(filename,copyname,ismp3,song);
			opts.print_sep()

		opts.print_done()
	except KeyboardInterrupt:
		opts.print_terminated()

if __name__ == "__main__":
	opts = options.OrganizerOptions()
	opts.parse_cmdline_arguments(sys.argv)
	main(opts)

