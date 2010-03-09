#!/usr/bin/env python

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

import sys
import os

import filter.index as index
import filter.options as options

def main(opts):
	try:
		opts.print_init()
		db = None
		if opts.targetIndex == None:
			db = index.FilterIndex(opts.index,opts.user,opts.pw)
		else:
			db = index.FilterIndex(opts.targetIndex,opts.user,opts.pw)
			if opts.drop:
				print "Dropping target tables"
				db.drop_tables()
				print "----------------------------------------------"	
			print "Copying files from index `"+opts.index+"` to target `"+opts.targetIndex+"`"
			db.copy_tables_from_index(opts.index)
			print "----------------------------------------------"
	
		if opts.filter.find('s') != -1:
			print "Removing all files that are not playable"
			db.filter_by_playable()
			print "----------------------------------------------"
		if opts.filter.find('m') != -1:
			print "Removing all files with duplicate md5 hashes"
			db.filter_by_md5()
			print "----------------------------------------------"
		if opts.filter.find('f') != -1:
			print "Removing all files with duplicate fingerprints"
			if opts.level > 0:
				print "Except for files without tag similarity"
			db.filter_by_fingerprint(opts.level)
			print "----------------------------------------------"
		if opts.filter.find('p') != -1:
			print "Removing all files with duplicate puids"
			if opts.level > 0:
				print "Except for files without tag similarity"
			db.filter_by_puid(opts.level)
			print "----------------------------------------------"
		if opts.filter.find('c') != -1:
			print "Removing non existant file entries"
			x = 0
			files = db.get_all_file_index_connections()
			for f in files:
				fn = os.path.join(f.path,f.name+f.ext)
				if not os.path.exists(fn):
					print '\t',fn
					db.remove_file(f.id)
					x+=1
			print x, "files removed"
			print "----------------------------------------------"
			print "Cleaning tags"
			db.clean_tags()
			print "----------------------------------------------"
			print "Cleaning md5s"
			db.clean_md5s()
			print "----------------------------------------------"
			print "Cleaning fingerprints"
			db.clean_fingerprints()
			print "----------------------------------------------"
			print "Cleaning puids"
			db.clean_puids()
			print "----------------------------------------------"

		opts.print_done()
	except KeyboardInterrupt:
		opts.print_terminated()

if __name__ == "__main__":
	opts = options.FilterOptions()
	opts.parse_cmdline_arguments(sys.argv)
	main(opts)

