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

from file import create_files_from_flat_list

class db:
	def __init__(self,dbname,user,pw):
		self._db     = MySQLdb.connect(passwd=pw,user=user,db=dbname,use_unicode = True,charset='utf8')
		self._cursor = self._db.cursor()

	def get_files_with_tags_from_index(self,index):
		self._cursor.execute(u"""
			SELECT 
				f.id,
				f.path,
				f.name,
				f.extension,
				t.value,
				t.type,
				t.source
			FROM
				`"""+index+u"""`.files AS f
			LEFT JOIN
				`"""+index+u"""`.tags AS t
			ON
				f.id = t.file
			ORDER BY
				f.id
		""")
	
		res = self._cursor.fetchall()
		
		fs = create_files_from_flat_list(res)
		return fs
		
	def _copy_hash_table(self,index,name):
		self._cursor.execute(u"""
			CREATE TABLE IF NOT EXISTS 
				"""+name+u""" (
					id SERIAL, PRIMARY KEY(id),
					UNIQUE(value)
				)
			SELECT 
				* 
			FROM 
				`"""+index+u"""`."""+name+u""";
		""")
	
	def _copy_everything_except_for_files_from_index(self,index):
		self._copy_hash_table(index,u"md5s")
		self._copy_hash_table(index,u"fingerprints")
		self._copy_hash_table(index,u"puids")
		
		self._cursor.execute(u"""
			CREATE TABLE IF NOT EXISTS 
				tags (
					id SERIAL, PRIMARY KEY(id),
					FOREIGN KEY(file) REFERENCES files.id
				)
			SELECT
				*
			FROM
				`"""+index+u"""`.tags
		""")		
	
	def _create_files_table(self):
		self._cursor.execute(u"""
			CREATE TABLE IF NOT EXISTS files (
				id          SERIAL, PRIMARY KEY(id),
				path        VARCHAR(1024) CHARSET 'utf8' BINARY NOT NULL,
				name        VARCHAR(255) CHARSET 'utf8' BINARY NOT NULL,
				extension   VARCHAR(8) CHARSET 'utf8' BINARY NOT NULL,
				size        BIGINT UNSIGNED NOT NULL,
				online      BOOL,
				
				md5         BIGINT UNSIGNED NOT NULL, FOREIGN KEY (md5) REFERENCES md5s.id,
				fingerprint BIGINT UNSIGNED, FOREIGN KEY (fingerprint) REFERENCES fingerprints.id,
				puid        BIGINT UNSIGNED, FOREIGN KEY (puid) REFERENCES puids.id
			);
		""")
	
	def create_tables(self,index):
		self._copy_everything_except_for_files_from_index(index)
		self._create_files_table()
	
	def copy_file_from_index(self,id,newPath,newName,newExt,index):
		self._cursor.execute(u"""
			INSERT INTO files (
				id,path,name,extension,size,online,md5,fingerprint,puid
			) SELECT 
				id,%s,%s,%s,size,online,md5,fingerprint,puid
			FROM
				`"""+index+"""`.files
			WHERE
				id = %s;
		""",
			(newPath,newName,newExt,id)
		)
		
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
