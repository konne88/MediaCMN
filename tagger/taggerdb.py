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

from tags.tag import Tag
from updatetags import create_files_from_flat_list

class db:
	def __init__(self,dbname,user,pw):
		self._db     = MySQLdb.connect(passwd=pw,user=user,db=dbname,use_unicode = True,charset='utf8')
		self._cursor = self._db.cursor()

	def get_files_with_tags_and_puid(self):
		self._cursor.execute(u"""
			SELECT 
				f.id,
				p.value AS puid,
				t.value,
				t.type,
				t.source
			FROM
				files AS f
			LEFT JOIN
				puids AS p
			ON
				f.puid = p.id
			JOIN
				tags AS t
			ON
				f.id = t.file
			ORDER BY
				f.id;
		""")

		res = self._cursor.fetchall()
		
		fs = create_files_from_flat_list(res)
		return fs

	def update_all_tags(self,tfs):
		self._cursor.execute(u"TRUNCATE TABLE tags;")
		
		if tfs == []:
			return
		
		q = u"""
			INSERT INTO tags (
				file,value,type,source
			) VALUES 
		"""
		vals = []
		
		for f in tfs:
			for t in f.tags:
				q+=u"(%s,%s,%s,%s),"
				vals.append(f.id)
				vals.append(t.value)
				vals.append(t.type)
				vals.append(t.source)
		
		# remove last ','
		q = q[0:-1]+u";"
		
		self._cursor.execute(q,vals)

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
					id SERIAL, PRIMARY KEY(id),
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

