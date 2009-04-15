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
import tagger.options as options

def main(opts):
	try:
		print "----------------------------------------------"

		db = None
		if opts.targetIndex == None:
			db = index.TaggerIndex(opts.index,opts.user,opts.pw)
		else:
			db = index.TaggerIndex(opts.targetIndex,opts.user,opts.pw)
			if opts.drop:
				print "Dropping target tables"
				db.drop_tables()
				print "----------------------------------------------"	
			print "Copying files from index `"+opts.index+"` to target `"+opts.targetIndex+"`"
			db.copy_tables_from_index(opts.index)
			print "----------------------------------------------"

		print "Caching database entries"
		fs = db.get_files_with_tags_and_puid()
		newtagfiles = []
		for f in fs:
			print 'Searching tags on musicbrainz for file',f.id,'with puid',f.puid
			print '\tOld Tags:',f.tags
			fts = get_matching_puid_tags(f,opts.level)
			print '\tNew Tags:',fts.tags
			newtagfiles.append( fts )
			print "----------------------------------------------"
			
		print "Writing new tags to index"		
		db.update_all_tags(newtagfiles)
		print "----------------------------------------------"

		print "Tagger done"
		print "----------------------------------------------"
		
	except KeyboardInterrupt:
		print
		print
		print "----------------------------------------------"
		print "Tagger terminated."
		print "----------------------------------------------"

if __name__ == "__main__":
	opts = options.TaggerOptions()
	opts.parse_cmdline_arguments(sys.argv)
	main(opts)
	
