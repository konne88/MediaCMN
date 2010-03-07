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
from datetime import datetime

import indexer.filetags as filetags
import indexer.metatags as metatags
import indexer.musicip as musicip
import indexer.options as options
import share.index as index
from share.entries import File

def calc_md5_and_size(fullname):
	# python strings may include NUL bytes!!!
	# http://www.velocityreviews.com/forums/t357410-md5-from-python-different-then-md5-from-command-line.html
	f= open(fullname,mode='rb')
	d = f.read();
	size = len(d)

	return hashlib.md5(d).hexdigest(), size
	
def parse_file(db,fullname,path,filename,count):
	print 'Indexing file "'+filename+'"'
	print '\tPath:',path
	print '\tTime:',datetime.now().strftime("%H:%M:%S")
	
	name, ext = os.path.splitext(filename)
	
	if db.is_file_added(path,name,ext):
		print "\tAlready added to the database."
		return count	#count isn't incremented
		
	# calc the values
	md5hash, size        = calc_md5_and_size(fullname)
	fingerprint,puid,tags,online = musicip.generate_fingerprint_and_lookup_tags_if_online(fullname)
	tags.extend(filetags.guess_from_path_and_name(path,name))
	tags.extend(metatags.get_from_file(fullname,ext))
	
	# add values to db
	md5id         = db.add_md5(md5hash)
	puidid        = db.add_puid(puid)
	fingerprintid = db.add_fingerprint(fingerprint)
	fileid = db.add_file(File(path,name,ext,size,online,md5id,fingerprintid,puidid))
	db.add_tags_to_file(tags,fileid)
	
	# print values
	print '\tOnln:',online
	print '\tSize:',size/1024/1024,"mb"
	print '\tMd5 :',md5hash
	if fingerprint!=None:
		print '\tPrnt:',fingerprint[:25]+"..."+fingerprint[-25:]
	if puid!=None:
		print '\tPUID:',puid
	print '\tTags:',tags
	count+=1
	print '\tFile:',str(count)
	print "----------------------------------------------"
	return count

def examen_dir(db,dirname,count):
	for filename in os.listdir(dirname):
		fullname = os.path.join(dirname, filename)
		if os.path.isfile(fullname):
			count = parse_file(db,fullname,dirname,filename,count)			
		else:
			count = examen_dir(db,fullname,count)

	return count

def main(opts):
	try:
		print "----------------------------------------------"
		db = index.Index(opts.index,opts.user,opts.pw)

		if opts.drop:
			print "Dropping tables"
			db.drop_tables()
			print "----------------------------------------------"
			
		if opts.new:
			print "Creating tables"
			db.create_tables()
			print "----------------------------------------------"

		count = 0
		for s in opts.sources:
			if os.path.isfile(s):
				filename = os.path.split(s)
				count = parse_file(db,s,filename[0],filename[1],count)
			else:
				count = examen_dir(db,s,count)
		
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
	opts = options.IndexerOptions()
	opts.parse_cmdline_arguments(sys.argv)
	main(opts)
	
