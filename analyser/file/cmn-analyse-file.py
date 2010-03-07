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

import hashlib

import index
import options

def calc_md5_and_size(fullname):
	# python strings may include NUL bytes!!!
	# http://www.velocityreviews.com/forums/t357410-md5-from-python-different-then-md5-from-command-line.html
	f= open(fullname,mode='rb')
	d = f.read();
	size = len(d)

	return hashlib.md5(d).hexdigest(), size

def main(opts):
	try:
		opts.print_init()

		db = index.AnalyserIndex(opts.index,opts.user,opts.pw)
		index.create_file_info_table_if_nessesary('md5s')
		index.create_file_info_table_if_nessesary('sizes')

		fs = db.get_files()
		md5s = []
		sizes = []
		for f in fs:
			opts.print_analyse_file(f)]

			r = calc_md5_and_size(f[1]);			

			md5s.append((f[0],r[0]))
			sizes.append((f[0],r[1]))
			
		db.write_file_info('md5s',md5s)
		db.write_file_info('sizes',sizes)
		
		opts.print_done()
		
	except KeyboardInterrupt:
		opts.print_terminated()

if __name__ == "__main__":
	opts = options.AnalyserOptions("CMN File Analyser",
		"Calculates the md5 hash and size of each file.")
	opts.parse_cmdline_arguments(sys.argv)
	main(opts)
	
