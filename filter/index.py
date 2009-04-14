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

from share.index import Index
from entries import Tag, FileGroup, FileIdWithTags, FileIndexConnection
from groupfilter import filter_check_groups_using_tags, filter_unchecked

# how filtering the db works
#
# there is a table of all files
# tables of hashes 
# and a table for tags 
#
# a filter first uses the function _get_files_with_tags_grouped_by_column 
# to get the id's of all files grouped by the passed name of the column in the db.
# each file contains all of it's tags too
#
# the list of groups, files and tags is passed to the groupfilter.filter function
# this function returns a list of all files that need to be deleted
#
# this list is passed to the _delete_files_and_move_their_tags function

class FilterIndex(Index):
	def __init__(self,dbname,user,pw):
		super(FilterIndex,self).__init__(dbname,user,pw)

	@staticmethod
	def _create_group(res,i,gs):
		val = res[i][0]
	
		fs = []
		while True:
			i = FilterIndex._create_file(res,i,fs)
			if len(res) == i or res[i][0] != val:
				break
	
		# append the group only if it's value isn't NULL
		if val != None:
			gs.append( FileGroup(val,fs) )
	
		return i
	
	@staticmethod
	def _create_file(res,i,fs):
		id = res[i][1]
	
		ts = []
		while True:
			i = FilterIndex._create_tag(res,i,ts)
			if len(res) == i or res[i][1] != id:
				break
	
		fs.append( FileIdWithTags(id,ts) )
		return i
	
	@staticmethod
	def _create_tag(res,i,ts):
		value = res[i][2]
		type = res[i][3]
		source = res[i][4]
	
		if value != None:
			ts.append( Tag(value,type,source) )
	
		return i+1

	@staticmethod
	def _create_groups_from_flat_list(res):
		gs = []
		i = 0
		while i<len(res):
			i = FilterIndex._create_group(res,i,gs)
	
		return gs

	def _get_files_with_tags_grouped_by_column(self,column):
		self._cursor.execute(u"""
			SELECT 
				f."""+column+u""" AS value,
				f.id AS file,
				t.value,
				t.type,
				t.source
			FROM
				files AS f
			LEFT JOIN
				tags AS t
			ON
				f.id = t.file
			ORDER BY
				f."""+column+u""", f.id;
		""")

		res = self._cursor.fetchall()
		
		return FilterIndex._create_groups_from_flat_list(res)
		
	def _merge_file_tags_and_delete_old_file(self,dfs):
		for df in dfs:
			self._cursor.execute(u"""
				DELETE FROM 
					files 
				WHERE 
					id=%s;
			""",
				(df.oldFileId,)
			)
			
			self._cursor.execute(u"""
				UPDATE
					tags
				SET 
					file=%s
				WHERE
					file=%s;
			""",
				(df.stayFileId , df.oldFileId)
			)

	def _filter_by_column(self,column,checkTagsLevel):
		gs = self._get_files_with_tags_grouped_by_column(column)

		dfs = []
		if checkTagsLevel > 0:
			dfs = filter_check_groups_using_tags(gs,checkTagsLevel)
		else:
			dfs = filter_unchecked(gs)
		
		self._merge_file_tags_and_delete_old_file(dfs)

	def filter_by_puid(self,level):
		self._filter_by_column(u"puid",level)
		
	def filter_by_fingerprint(self,level):
		self._filter_by_column(u"fingerprint",level)

	def filter_by_md5(self):
		self._filter_by_column(u"md5",0)

	def filter_by_playable(self):
		self._cursor.execute(u"""
			DELETE FROM
				files
			WHERE
				fingerprint IS NULL;	
		""")
	
	def _clean_hashes(self,name):
		# remove all hashes of the given name that have no file assigned to it	
		self._cursor.execute(u"""
			DELETE FROM
				m
			USING			
				md5s AS m 
			LEFT JOIN 
				files AS f 
			ON
				m.id = f.md5 
			WHERE 
				f.id IS NULL;
		""")

	def clean_puids(self):
		self._clean_hashes("puids")	
	
	def clean_fingerprints(self):
		self._clean_hashes("fingerprints")
		
	def clean_md5s(self):
		self._clean_hashes("md5s")

	def clean_tags(self):
		# remove all tags that have no file assigned with it
		self._cursor.execute(u"""
			DELETE FROM
				t
			USING			
				tags AS t 
			LEFT JOIN 
				files AS f 
			ON
				t.file = f.id 
			WHERE
				f.id IS NULL;
		""")
	
	def get_all_file_index_connections(self):
		self._cursor.execute(u"""
			SELECT 
				id,path,name,extension
			FROM 
				files;
		""")
		
		fs = []
		res = self._cursor.fetchall()		
		for f in res:
			fs.append(FileIndexConnection(f[0],f[1],f[2],f[3]))
			
		return fs
		

if __name__ == "__main__":
	print "Testing the results from group filtering checking with tags"
	print "-----------------------------------------------------------"
	print 
	print "filtering these files"
	print
	l = []
	l.append([0,1,u"Stir It Up","track",None])
	l.append([0,1,u"Bob Marley","artist",None])
	l.append([0,1,u"331056","duration",None])
	l.append([0,1,u"",None,None])
	l.append([0,1,u" Stir It Up",None,None])
	l.append([0,1,u"05 ","number",None])
	l.append([0,1,u"Bob Marley - 1994 - Legend","release",None])
	l.append([0,1,u"Bob Marley - Complete Discography From 1967 To 2002 [33 Full Albums] (Mp3 256Kbps)","artist",None])
	l.append([0,2,u"Stir It Up","track",None])
	l.append([0,2,u"Bob Marley","artist",None])
	l.append([0,2,u"336048","duration",None])
	l.append([0,2,u"",None,None])
	l.append([0,2,u" Stir It Up",None,None])
	l.append([0,2,u"08 ","number",None])
	l.append([0,2,u"Bob Marley - 1973 - Catch A Fire","release",None])
	l.append([0,2,u"Bob Marley - Complete Discography From 1967 To 2002 [33 Full Albums] (Mp3 256Kbps)","artist",None])
	l.append([0,3,u"Stir It Up","track",None])
	l.append([0,3,u"Bob Marley","artist",None])
	l.append([0,3,u"331056","duration",None])
	l.append([0,3,u"",None,None])
	l.append([0,3,u" Stir It Up",None,None])
	l.append([0,3,u"01 ","number",None])
	l.append([0,3,u"Bob Marley - 2002 - One Love, The Very Best Of","release",None])
	l.append([0,3,u"Bob Marley - Complete Discography From 1967 To 2002 [33 Full Albums] (Mp3 256Kbps)","artist",None])
	l.append([0,4,u"Stir It Up","track",None])
	l.append([0,4,u"Bob Marley","artist",None])
	l.append([0,4,u"329040","duration",None]) 
	l.append([0,4,u"",None,None])
	l.append([0,4,u" Stir It Up",None,None])
	l.append([0,4,u"03 ","number",None])
	l.append([0,4,u"Bob Marley - 1978 - Babylon By Bus","release",None])
	l.append([0,4,u"Bob Marley - Complete Discography From 1967 To 2002 [33 Full Albums] (Mp3 256Kbps)","artist",None])
	l.append([0,4,u"Stir It Up","track",None])
	l.append([0,4,u"Bob Marley","artist",None])
	l.append([0,4,u"329040","duration",None]) 
	l.append([0,4,u"",None,None])
	l.append([0,4,u" Stir It Up",None,None])
	l.append([0,4,u"03 ","number",None])
	l.append([0,4,u"Bob Marley - 1978 - Babylon By Bus","release",None])
	l.append([0,4,u"Bob Marley - Complete Discography From 1967 To 2002 [33 Full Albums] (Mp3 256Kbps)","artist",None])
	l.append([0,5,u"Stir It Up","track",None])
	l.append([0,5,u"Bob Marley","artist",None])
	l.append([0,5,u"03 ","number",None])
	l.append([0,5,u"Babylon By Bus","release",None])
	l.append([0,6,u"Come as you are","track",None])
	l.append([0,6,u"Roby Williams","artist",None])
	l.append([0,6,u"I have no clue","release",None])
	
	gs = create_groups_from_flat_list(l)
	
	for g in gs:
		print 'group: ',g.value
		for f in g.files:
			print '\tfile: ',f.id
			for t in f.tags:
				print '\t\t','"'+t.value+'"','-',t.type
	
	dfs = filter_check_groups_using_tags(gs,0.5)
	
	print
	print "these files would have been deleted:"
	print 
	
	for df in dfs:
		print df.oldFileId

