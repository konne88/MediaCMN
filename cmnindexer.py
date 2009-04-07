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
import md5 

import indexer.filetags as filetags
import indexer.metatags as metatags
import indexer.indexdb as indexdb
import indexer.musicip as musicip
from db.identifiernames import is_valid_identifier_name
from datetime import datetime

def calc_md5_and_size(fullname):
	# python strings may include NUL bytes!!!
	# http://www.velocityreviews.com/forums/t357410-md5-from-python-different-then-md5-from-command-line.html
	f= open(fullname,mode='rb')
	d = f.read();
	size = len(d)
	return md5.new(d).hexdigest(), size
	
def parse_file(db,fullname,path,filename):
	print 'Indexing file "'+filename+'"'
	print '\tPath:',path
	t = datetime.now()
	print '\tTime:',t.strftime("%H:%M:%S")
	name, extension = os.path.splitext(filename)
	
	if db.is_file_added(path,name,extension):
		print "\tAlready added to the database."
		return
	
	# calc the values
	md5hash, size        = calc_md5_and_size(fullname)
	fingerprint,puid,tgs,online = musicip.generate_fingerprint_and_lookup_tags_if_online(fullname)
	tgs.extend(filetags.guess_from_path_and_name(path,name))
	tgs.extend(metatags.get_from_file_metadata(fullname,extension))
	
	# add values to db
	md5id         = db.add_md5(md5hash)
	puidid        = db.add_puid(puid)
	fingerprintid = db.add_fingerprint(fingerprint)
	fileid        = db.add_file(path,name,extension,size,online,md5id,fingerprintid,puidid)
	db.add_tags(tgs,fileid)

	# print values
	print '\tOnln:',online
	print '\tSize:',size/1024/1024,"mb"
	print '\tMd5 :',md5hash
	if fingerprint!=None:
		print '\tPrnt:',fingerprint[:25]+"..."+fingerprint[-25:]
	if puid!=None:
		print '\tPUID:',puid
	print '\tTags:',tgs

def examen_dir(db,dirname,count):
	for filename in os.listdir(dirname):
		fullname = os.path.join(dirname, filename)
		if os.path.isfile(fullname):
			parse_file(db,fullname,dirname,filename)
			count=count+1
			print '\tFile:',str(count)
			print "----------------------------------------------"			
		else:
			count = examen_dir(db,fullname,count)

	return count

def usage():
	print """
Usage: indexer [OPTIONS] SOURCES ...

All files found, recursively, in the SOURCES are added to the database.

You can use the following OPTIONs.
  -d --drop        Drops all database entries
  -h --help        Shows the help (what you currently see)
  -i --index       The mysql database used to store the index (default is cmn_index)
  -n --new         Creates the tables in the database
                   Use with -d to remove old entries first
  -p --password    The password needed to acces the database
  -u --user        The username to acces the database (default is root)
"""

def main(argv):
	drop = False
	create = False
	user = "root"
	pw = ""
	base="cmn_index"
	quit = False
	
	try:
		opts, sources = getopt.getopt(argv, "dhi:np:u:", ["drop","help","index=","new","password=","user="]) 
	except getopt.GetoptError, e:
		print str(e)
		quit = True

	for opt, arg in opts:
		if opt in ("-d", "--drop"):
			drop = True
		elif opt in ("-h", "--help"):
			quit = True
		elif opt in ("-i", "--index"):
			base = arg.replace('`','``')
			if not is_valid_identifier_name(base):
				print "Invalid index name"
				quit = True			
		elif opt in ("-n", "--new"):
			create = True
		elif opt in ("-p", "--password"):
			pw = arg
		elif opt in ("-u", "--user"):
			user = arg
	
	if quit == True:
		usage()
		sys.exit(2)
	
	try:
		print "----------------------------------------------"
		db = indexdb.db(base,user,pw)
	
		if drop:
			print "Dropping tables"
			db.drop_tables()
			print "----------------------------------------------"
			
		if create:
			print "Creating tables"
			db.create_tables()
			print "----------------------------------------------"
	
		if sources != []:
			count = 0
			for source in sources:
				source = os.path.abspath(source)
				if os.path.isfile(source):
					filename = os.path.split(source)
					print filename				
					parse_file(db,source,filename[0],filename[1])
				else:
					count = examen_dir(db,source,count)
			
			print "Indexer done."
			print "All files lying in the given directories and subdirectories are indexed."
			print "----------------------------------------------"
			
	except KeyboardInterrupt:
		print
		print
		print "----------------------------------------------"
		print "Indexer terminated."
		print "You can continue adding files to the index the next time you issue this command."
		print "----------------------------------------------"

if __name__ == "__main__":
	main(sys.argv[1:])

