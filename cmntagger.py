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

import getopt
import sys
import os

from tagger.updatetags import get_matching_puid_tags
import tagger.taggerdb as taggerdb
from db.identifiernames import is_valid_identifier_name

def usage():
	print """
Usage: tagger [OPTIONS]

You can use the following OPTIONs.
  -c --copy        Copies all tables from the index to the copy target
                   Which is then used as the index. 
                   If this options is used the index will not be altered
                   Use with -d to remove entries from the target index first
  -d --drop        Drops all entries from the copy target before copies are made
                   Only to use with the copy parameter
  -h --help        Shows the help (what you currently see)
  -i --index       The index used. If copy is used it is used as source index only 
                   And is not modified afterwards
                   (default is cmn_index)
  -l --level       The found tags are only assigned to a file, if the similarity to
                   the original tags is of a heighter level then the pass one. 
                   (default is 0 which is the lowest)
  -p --password    The password needed to acces the database
  -u --user        The username to acces the database (default is root)
"""

def main(argv):
	user = "root"
	pw = ""
	index = "cmn_index"
	target = ""
	drop = False
	level = 0.0
	quit = False
	
	try:
		opts, sources = getopt.getopt(argv, "c:dhi:-l:p:u:", ["copy=","drop","help","index=","level=","password=","user="]) 
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
		elif opt in ("-h", "--help"):
			quit = True
		elif opt in ("-i", "--index"):
			index = arg.replace('`','``')
			if not is_valid_identifier_name(index):
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
		quit = True
			
	if quit == True:
		usage()
		sys.exit(2)
		
	try:
		print "----------------------------------------------"
		
		base = ""
		if target == "":
			base = index
		else:
			base = target
		
		db = taggerdb.db(base,user,pw)
	
		if drop:
			print "Dropping tables"
			db.drop_tables()
			print "----------------------------------------------"
		if target != "":
			print "Copying files from index `"+index+"` to target `"+base+"`"
			db.copy_tables_from_index(index)
			print "----------------------------------------------"
		
		print "Caching database entries"
		fs = db.get_files_with_tags_and_puid()
		newtagfiles = []
		for f in fs:
			print 'Searching tags on musicbrainz for file',f.id,'with puid',f.puid
			print '\tOld Tags:',f.tags
			fts = get_matching_puid_tags(f,level)
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
	main(sys.argv[1:])

