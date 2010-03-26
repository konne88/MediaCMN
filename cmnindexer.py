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
from datetime import datetime
from subprocess import *

import indexer.filetags as filetags
import indexer.metatags as metatags
import indexer.musicip as musicip
import indexer.options as options
import share.index as index
from share.entries import IndexedFile

def calc_md5_and_size(fullname):
	# python strings may include NUL bytes!!!
	# http://www.velocityreviews.com/forums/t357410-md5-from-python-different-then-md5-from-command-line.html
	f= open(fullname,mode='rb')
	d = f.read()
	size = len(d)

	return hashlib.md5(d).hexdigest(), size

def is_file_mp3(fullname):
	argv = [u"file",u"-b",fullname]
	finfo = Popen(argv, stdout=PIPE).communicate()[0]

	return finfo.find(u"MP3 encoding") != -1 or finfo.find(u"MPEG ADTS") != -1

def parse_file(db,fullname,path,filename,count):
	print "Indexing file '%s'" % filename
	print '\tPath:',path
	print '\tTime:',datetime.now().strftime("%H:%M:%S")
	
	name, ext = os.path.splitext(filename)
	
	if db.is_file_added(path,name,ext):
		print "Already added to the database."
		return count	#count isn't incremented
	
	# calc the values
	md5hash, size        = calc_md5_and_size(fullname)
	fingerprint,puid,taggroups,online,playable,duration = musicip.generate_fingerprint_and_lookup_tags_if_online(fullname)
	taggroups.extend(filetags.guess_from_path_and_name(path,name))
	taggroups.extend(metatags.get_from_file(fullname,ext))
	musictype = None
	if playable:
		if is_file_mp3(fullname):
			musictype = 'mp3'
		else:
			musictype = 'other'
	
	# print what we found
	print '\tPlay:',playable
	print '\tType:',musictype
	print '\tOnln:',online
	print '\tSize:',size/1024/1024,"mb"
	print '\tMd5 :',md5hash
	if fingerprint!=None:
		print '\tPrnt:',fingerprint[:25]+"..."+fingerprint[-25:]
	if puid!=None:
		print '\tPUID:',puid
	print '\tTags:',taggroups

	# add values to db
	md5id         = db.add_md5(md5hash)
	puidid        = db.add_puid(puid)
	fingerprintid = db.add_fingerprint(fingerprint)
	
	f = IndexedFile(None,path,name,ext)
	f.flags['size'] = size
	f.flags['puidid'] = puidid
	f.flags['md5id'] = md5id
	f.flags['fingerprintid'] = fingerprintid
	f.flags['musictype'] = musictype
	f.flags['musicip_online'] = online
	f.flags['duration'] = duration
	f.taggroups = taggroups
	db.add_file(f)
	
	count+=1
	print 'Added succesfully with id %s.'%str(count)
	opts.print_sep()
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
		opts.print_init()
		db = index.Index(opts.index,opts.user,opts.pw)

		if opts.drop:
			print "Dropping tables"
			db.drop_tables()
			opts.print_sep()
			
		print "Creating tables"
		db.create_tables()
		opts.print_sep()

		count = 0
		for s in opts.sources:
			if os.path.isfile(s):
				filename = os.path.split(s)
				count = parse_file(db,s,filename[0],filename[1],count)
			else:
				count = examen_dir(db,s,count)
		
		opts.print_done()
	except KeyboardInterrupt:
		opts.print_terminated()

if __name__ == "__main__":
	opts = options.IndexerOptions()
	opts.parse_cmdline_arguments(sys.argv)
	main(opts)
	
