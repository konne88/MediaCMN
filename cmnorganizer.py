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

import organizer.organizerdb as organizerdb
from organizer.file import get_new_relativename, get_file_infos, create_nonexistant_dirs
from organizer.mp3file import is_file_mp3, transform_to_mp3, set_file_id3_tags
from db.identifiernames import is_valid_identifier_name

def usage():
	print """
Usage: organizer [OPTIONS] TARGET

The library is created in the TARGET directory
All songs copied into the library are converted to MP3!

You can use the following OPTIONs.
  -d --drop        Drops all entries from the new index target before copies are made
                   Only to use with the copy parameter
  -f --filename    Defines how filenames, for each entry in the index, are created
                   All occurances of the following %_ char
                   are replaced by their value
                   
                   %t     The track name
                   %r     The release name
                   %a     The artist's name
                   %n     The tracknumber in the release
                          (if one digit, '0' is prepended)
                   %d     The duration of the song
                   %%     Is replaced by a '%' character
                   
                   Default is, extension is added automatically
                   %a/%r/%n-%t
  -h --help        Shows the help (what you currently see)
  -i --index       The index used.
  -l --level       Only tags with a rating highter then the level will be used
  -n --new         Creates a new index with all the files that were stored on the filesystem.
                   All files keep the id they had before so you can see which
                   files were skipped.
                   Use with -d to remove entries from the new index first
                   (default is 0.3) 0 is the lowest
  -p --password    The password needed to acces the database
  -r --restriction What restrictions exist for valid filenames. Pass
                   0      If the library is saved on a UNIX filesystem
                          just like ext3. 
                          '/' and NUL 
                          are removed from filenames
                   1      If the library is saved on a WINDOWS filesystem
                          just like ntfs,fat32. 
                          '/' '\\' ':' '*' '?' '"' '<' '>' '|' and NUL
                          are removed from filenames
                   (default is 0)
  -u --user        The username to acces the database (default is root)
"""


def copy_file_to_target(db,ft,target,name,minRating,strict,index):
	infos = get_file_infos(ft.tags,minRating)
	fullname = ft.fullname
	
	print '\t',ft.fullname
	
	if not os.path.exists(fullname):
		print "\tFile doesn't exist"
		return
	
	if not is_file_mp3(fullname):
		print "\tNeeds to be converted to mp3"
		tempname = u'/tmp/cmn-organizer-'+unicode(os.getpid())+u'.mp3'
		transform_to_mp3(fullname,tempname)
		
		if not os.path.exists(tempname):
			print "\tCouldn't be converted to mp3"
			return
		fullname = tempname
	
	newRelativename = get_new_relativename(target,name,infos,strict)
	
	if newRelativename == None:
		print "Generation of a new filename failed"
		print infos
		return
	
	newFullname = os.path.join(target,newRelativename)
	print '\t',newFullname
	if os.path.exists(newFullname):
		print "\tFile can't be copied to the destination, it already exists."
		return
	create_nonexistant_dirs(target,newRelativename)
	shutil.copyfile(fullname,newFullname)
	
	set_file_id3_tags(newFullname,infos)
	
	pathSplit = os.path.split(newFullname)
	fileSplit = os.path.splitext(pathSplit[1])
	db.copy_file_from_index(ft.id,pathSplit[0],fileSplit[0],fileSplit[1],index)
	
def main(argv):
	user = "root"
	pw = ""
	base="cmn_index"
	name = "%a/%r/%n-%t"
	target = ""
	level = 0.3
	strict = 0
	newIndex = ""
	drop = False
	quit = False
	
	try:
		opts, unusedOps = getopt.getopt(argv, "df:hi:l:n:p:r:u:", ["drop","filename=","help","index=","level=","new=","password=","restriction=","user="]) 
		if len(unusedOps) != 1:
			print "You must pass exactly one TARGET for the organizer to create the library in."
			quit = True
		else:
			target = os.path.abspath(unusedOps[0])
			if not os.path.isdir(target):
				print "Target is not a directory"
				quit = True
			
	except getopt.GetoptError, e:
		print str(e)
		quit = True

	for opt, arg in opts:
		if opt in ("-d", "--drop"):
			drop = True
		elif opt in ("-f", "--filename"):
			name = arg
		elif opt in ("-h", "--help"):
			quit = True
		elif opt in ("-i", "--index"):
			base = arg.replace('`','``')
			if not is_valid_identifier_name(base):
				print "Invalid index name"
				quit = True	
		elif opt in ("-l","--level"):
			try:
				level = float(arg)
			except:
				print "Passed level param is not a float."
				quit = True
		elif opt in ("-n", "--new"):
			newIndex = arg.replace('`','``')
			if not is_valid_identifier_name(newIndex):
				print "Invalid new index name"
				quit = True	
		elif opt in ("-u", "--user"):
			user = arg
		elif opt in ("-r","--restriction"):
			try:
				strict = int(arg)
			except:
				print "Passed restriction param is not an integer."
				quit = True
		elif opt in ("-p", "--password"):
			pw = arg
	
	if newIndex == "" and drop == True:
		print "Option drop can't be used without creating a new index."
		quit=True
	
	if quit == True:
		usage()
		sys.exit(2)
	
	db = organizerdb.db(newIndex,user,pw)
		
	if drop:
		print "Dropping new index tables"
		db.drop_tables()
		print "----------------------------------------------"
	if newIndex != "":
		print "Creating new index `"+newIndex+"`"
		db.create_tables(base)
		print "----------------------------------------------"
	
	try:
		fts = db.get_files_with_tags_from_index(base)
		for ft in fts:
			print 'Organizing file "'+unicode(ft.id)+'":'
			copy_file_to_target(db,ft,target,name,level,strict,base)
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
	main(sys.argv[1:])

