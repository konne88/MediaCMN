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

import getopt, sys
import os

import filter.index as index
from db.identifiernames import is_valid_identifier_name

def usage():
	print """
Usage: filter [OPTIONS]

You can use the following OPTIONs.
  -c --copy        Copies all tables from the index to the copy target
                   Which is then used as the index. 
                   If this options is used the index will not be altered
                   Use with -d to remove entries from the target index first
  -d --drop        Drops all entries from the copy target before copies are made
                   Only to use with the copy parameter
  -f --filter      Pass a string containing the following filter options (default is '')
                   s  remove all files that are not playable
                   m  remove all files with a douplicate md5 hash
                   f  remove all files with a douplicate fingerprint (if tags support equality)
                   p  remove all files with a douplicate puid (if tags support equality)
                   c  remove all entries referencing non existant files
                      as well as unused tags and hashes
  -h --help        Shows the help (what you currently see)
  -i --index       The index used. If copy is used it is used as source index only 
                   And is not modified afterwards
                   (default is cmn_index)
  -l --level       The fingerprint and puid filters only delete duplicates if the files tags match
                   to a heighter level then the pass one. (default is 0 which is the lowest)
  -p --password    The password needed to acces the database
  -u --user        The username to acces the database (default is root)
"""

def main(argv):
	filter = ""
	user = "root"
	pw = ""
	indexdb = "cmn_index"
	target = ""
	drop = False
	level = 0.0
	quit = False
	
	try:
		opts, sources = getopt.getopt(argv, "c:df:hi:l:p:u:", ["copy=","drop","filter=","help","index=","level=","password=","user="]) 
	except getopt.GetoptError, e:
		print str(e)
		quit = True

	for opt, arg in opts:
		if opt in ("-c", "--copy"):
			target = arg.replace('`','``')
			if not is_valid_identifier_name(target):
				print "Invalid target name"
				quit = True
		elif opt in ("-d", "--drop"):
			drop = True
		elif opt in ("-f", "--filter"):
			filter = arg
		elif opt in ("-h", "--help"):
			quit = True
		elif opt in ("-i", "--index"):
			indexdb = arg.replace('`','``')
			if not is_valid_identifier_name(indexdb):
				print "Invalid index name"
				quit = True
		elif opt in ("-l","--level"):
			try:
				level = float(arg)
			except:
				print "Passed level param is not a float."
				quit = True
		elif opt in ("-p", "--password"):
			pw = arg
		elif opt in ("-u", "--user"):
			user = arg

	if target == "" and drop == True:
		print "Option drop can't be used without the copy option."
		quit=True
			
	if quit == True:
		usage()
		sys.exit(2)
		
	try:
		print "----------------------------------------------"
		
		base = ""
		if target == "":
			base = indexdb
		else:
			base = target
		
		db = index.FilterIndex(base,user,pw)
	
		if drop:
			print "Dropping tables"
			db.drop_tables()
			print "----------------------------------------------"
		if target != "":
			print "Copying files from index `"+indexdb+"` to target `"+base+"`"
			db.copy_tables_from_index(indexdb)
			print "----------------------------------------------"
		
		if filter.find('s') != -1:
			print "Removing all files that are not playable"
			db.filter_by_playable()
			print "----------------------------------------------"
		if filter.find('m') != -1:
			print "Removing all files with duplicate md5 hashes"
			db.filter_by_md5()
			print "----------------------------------------------"
		if filter.find('f') != -1:
			print "Removing all files with duplicate fingerprints"
			if level > 0:
				print "Except for files without tag similarity"
			db.filter_by_fingerprint(level)
			print "----------------------------------------------"
		if filter.find('p') != -1:
			print "Removing all files with duplicate puids"
			if level > 0:
				print "Except for files without tag similarity"
			db.filter_by_puid(level)
			print "----------------------------------------------"
		if filter.find('c') != -1:
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

		print "Filter done"
		print "----------------------------------------------"
		
	except KeyboardInterrupt:
		print
		print
		print "----------------------------------------------"
		print "Filter terminated."
		print "----------------------------------------------"

if __name__ == "__main__":
	main(sys.argv[1:])

