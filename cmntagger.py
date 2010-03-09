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

import sys
import os

from tagger.musicbrainz import get_matching_puid_tags
import tagger.index as index
import share.options as options

def main(opts):
	try:
		opts.print_init()
		db = index.TaggerIndex(opts.index,opts.user,opts.pw)
		db.append_to_files_table()

		print "Caching database entries"
		files = db.get_files_with_tags_and_puid()

		newtagfiles = []
		for f in files:
			print 'Searching tags on musicbrainz for file',f.id,'with puid',f.puid
			online = False			

			if f.puid != None:
				print '\tOld Tags:',f.tags
				fts = get_matching_puid_tags(f,0.5)
				if fts != None:
					online = True

				print '\tNew Tags:',fts.tags
				newtagfiles.append( fts )
			print "----------------------------------------------"
			db.set_file_musicbrainzcon(f.id,online)
			
		print "Writing new tags to index"
		db.update_all_tags(newtagfiles)
		opts.print_done()
	except KeyboardInterrupt:
		opts.print_terminated()

if __name__ == "__main__":
	opts = options.CommonCmnOptions("MusicBrainz Tagger",
		"Searches for music tags online using their puid.")
	opts.parse_cmdline_arguments(sys.argv)
	main(opts)
	
