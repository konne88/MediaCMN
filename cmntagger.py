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

from tagger.musicbrainz import get_puid_tags
import tagger.index as index
import share.options as options

def main(opts):
	try:
		opts.print_init()
		db = index.TaggerIndex(opts.index,opts.user,opts.pw)
		db.append_to_files_table()

		print "Caching database entries"
		fileids = db.get_file_ids_if_puid_and_not_online()

		for fileid in fileids:
			online = False
			file_ = db.get_file_without_tags(fileid,('puid',))
			puid = file_.flags['puid']			
			print "Searching tags on musicbrainz for file",fileid,'with puid',puid
			taggroups = get_puid_tags(puid)
			if taggroups != None:
				online = True
				print '\tTags:',taggroups
				for taggroup in taggroups:					
					taggroup.fileid = file_.id
				db.add_tag_groups(taggroups)
				print "Added new tags to index."
			else:
				print "Service not online."
			db.set_file_musicbrainz_online(fileid,online)
			opts.print_sep()
			
		opts.print_done()
	except KeyboardInterrupt:
		opts.print_terminated()

if __name__ == "__main__":
	opts = options.CommonCmnOptions("MusicBrainz Tagger",
		"Searches for music tags online using their puid.")
	opts.parse_cmdline_arguments(sys.argv)
	main(opts)
	
