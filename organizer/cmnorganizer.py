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

import getopt, sys
import os
import shutil

import organizer.index as index
from organizer.file import get_new_relativename, get_file_infos, create_nonexistant_dirs
from organizer.mp3file import is_file_mp3, transform_to_mp3, set_file_id3_tags
import organizer.options as options

def copy_file_to_target(db,ft,opts):
	infos = get_file_infos(ft.tags,opts.level)
	fullname = os.path.join(ft.path,ft.name+ft.ext)
	
	print '\t',fullname
	
	if not os.path.exists(fullname):
		print "\tFile doesn't exist"
		return
	
	if not is_file_mp3(fullname):
		return
		
		# TODO
		# Add mp3 conversion
		
		print "\tNeeds to be converted to mp3"
		tempname = u'/tmp/cmn-organizer-'+unicode(os.getpid())+u'.mp3'
		transform_to_mp3(fullname,tempname)
		
		if not os.path.exists(tempname):
			print "\tCouldn't be converted to mp3"
			return
		fullname = tempname
	
	newRelativename = get_new_relativename(opts.target,opts.filepattern,infos,opts.restrictions)
	
	if newRelativename == None:
		print "Generation of a new filename failed"
		print infos
		return
	
	newFullname = os.path.join(opts.target,newRelativename)
	print '\t',newFullname
	if os.path.exists(newFullname):
		print "\tFile can't be copied to the destination, it already exists."
		return
	create_nonexistant_dirs(opts.target,newRelativename)
	shutil.copyfile(fullname,newFullname)
	
	set_file_id3_tags(newFullname,infos)
	
	pathSplit = os.path.split(newFullname)
	fileSplit = os.path.splitext(pathSplit[1])
	
	if opts.newIndex != None:
		db.copy_file_from_index_with_new_fullname(ft.id,pathSplit[0],fileSplit[0],fileSplit[1],opts.index)
	
def main(opts):
	db = None
	
	if opts.newIndex != None:
		db = index.OrganizerIndex(opts.newIndex,opts.user,opts.pw)
		if opts.drop:
			print "Dropping new index tables"
			db.drop_tables()
			print "----------------------------------------------"
		print "Creating new index `"+opts.newIndex+"`"
		db.copy_every_table_except_for_files_from_index(opts.index)
		db.create_files_table()
		print "----------------------------------------------"
	else:
		# connect with no database if newIndex is not specified	
		db = index.OrganizerIndex('',opts.user,opts.pw)
		
	try:
		fts = db.get_all_files_with_tags_from_index(opts.index)
		for ft in fts:
			print 'Organizing file "'+unicode(ft.id)+'":'
			copy_file_to_target(db,ft,opts)
		print "----------------------------------------------"
		
		print "Organizer done."
		print "----------------------------------------------"
			
	except KeyboardInterrupt:
		print
		print
		print "----------------------------------------------"
		print "Organizer terminated."
		print "----------------------------------------------"

if __name__ == "__main__":
	opts = options.OrganizerOptions()
	opts.parse_cmdline_arguments(sys.argv)
	main(opts)

