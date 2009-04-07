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

import MySQLdb
from groupfilter import filter_check_groups_using_tags
from groupfilter import filter_unchecked
from groupfilter import create_groups_from_flat_list

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

class db:
	def __init__(self,dbname,user,pw):
		self._db     = MySQLdb.connect(passwd=pw,user=user,db=dbname,use_unicode = True,charset='utf8')
		self._cursor = self._db.cursor()

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
		
		gs = create_groups_from_flat_list(res)
		return gs
		
	def _delete_files_and_move_their_tags(self,dfs):
		for df in dfs:
			self._cursor.execute(u"""
				DELETE FROM 
					files 
				WHERE 
					id=%s;
			""",
				(df.id,)
			)
			
			self._cursor.execute(u"""
				UPDATE
					tags
				SET 
					file=%s
				WHERE
					file=%s;
			""",
				(df.newTagId , df.id)
			)

	def _filter_by_column(self,column,checkTagsLevel):
		gs = self._get_files_with_tags_grouped_by_column(column)

		dfs = []
		if checkTagsLevel > 0:
			dfs = filter_check_groups_using_tags(gs,checkTagsLevel)
		else:
			dfs = filter_unchecked(gs)
		
		self._delete_files_and_move_their_tags(dfs)


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
		
	def _copy_hash_table(self,index,name):
		self._cursor.execute(u"""
			CREATE TABLE IF NOT EXISTS 
				"""+name+u""" (
					PRIMARY KEY(id),
					UNIQUE(value)
				)
			SELECT 
				* 
			FROM 
				`"""+index+u"""`."""+name+u""";
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
	
	def clean_puids(self):
		self._clean_hashes("puids")	
	
	def clean_fingerprints(self):
		self._clean_hashes("fingerprints")
		
	def clean_md5s(self):
		self._clean_hashes("md5s")

	def get_all_files(self):
		self._cursor.execute(u"""
			SELECT 
				id,path,name,extension
			FROM 
				files;
		""")
		
		return self._cursor.fetchall()
		
	def remove_file(self,fileid):	
		# delete file
		self._cursor.execute(u"""
			DELETE files FROM 
				files  
			WHERE 
				id = %s;
		""",
			(fileid,)
		)

	def copy_tables_from_index(self,index):
		self._copy_hash_table(index,u"md5s")
		self._copy_hash_table(index,u"fingerprints")
		self._copy_hash_table(index,u"puids")
		
		self._cursor.execute(u"""
			CREATE TABLE IF NOT EXISTS 
				files (
					PRIMARY KEY(id),
					FOREIGN KEY (md5) REFERENCES md5s.id,
					FOREIGN KEY (fingerprint) REFERENCES fingerprints.id,
					FOREIGN KEY (puid) REFERENCES puids.id
				)
			SELECT
				*
			FROM 
				`"""+index+u"""`.files;
		""")
		self._cursor.execute(u"""
			CREATE TABLE IF NOT EXISTS 
				tags (
					PRIMARY KEY(id),
					FOREIGN KEY(file) REFERENCES files.id
				)
			SELECT
				*
			FROM
				`"""+index+u"""`.tags
		""")

	def drop_tables(self):
		self._cursor.execute(u"""
			DROP TABLE IF EXISTS 
				files,
				md5s,
				fingerprints,
				puids,
				tags
			;
		""")

