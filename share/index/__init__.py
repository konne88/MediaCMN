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

# how to use mysqldb
# http://mysql-python.sourceforge.net/MySQLdb.html
# http://www.python.org/dev/peps/pep-0249/

import sqlite3
from share.entries import IndexedFile, TagGroup, FileTag
import os

class IndexReference(object):
	def __init__(self,path):
		self.path = path

class _SqliteCursorWrapper(sqlite3.Cursor):
	"""This is a wrapper class for sqlite cursors, cause this class
	needs ? instead of %s
	"""
	def __init__(self,db):
		self._c = db.cursor()

	def execute(self,query,values=()):
		query = query.replace('%s','?')
		return self._c.execute(query,values)

	def fetchall(self):
		f = self._c.fetchall()
		return f
		

	def fetchone(self):
		return self._c.fetchone()

	@property
	def lastrowid(self):
		return self._c.lastrowid

class Index(object):
	"""Represents the index where all information is stored."""

	def __init__(self,reference):
		"""Loads an index
		Loads a sqlite database using a path specified in the `reference`
		"""

		self._db = sqlite3.connect(reference.path)
		self._cursor = _SqliteCursorWrapper(self._db)

	def __del__(self):
		"Writes changes to the database file once not needed anymore."
		self._db.commit()

	@staticmethod
	def drop_content(reference):
		try: 
			os.remove(reference.path)
		except OSError:
			pass
		
	def add_file(self,file_):
		"""Add a file including all it's tags and flags to the index."""
		qt = u'INSERT INTO files ( path,name,ext'
		qb = u') VALUES ( %s,%s,%s'	
		vals = [file_.path,file_.name,file_.ext]
		for flag,value in file_.flags.iteritems():
			qt+=u','+flag
			qb+=u',%s'
			vals.append(value)
		q = qt+qb+u");"
		self._cursor.execute(q,vals)
		file_.id = self._cursor.lastrowid
		self.add_tag_groups(file_.taggroups)
		return file_.id

	def is_file_added(self,path,name,ext):
		"""Checks if a file has already been added to the index."""                
		self._cursor.execute(u"""
                        SELECT
                            path,name,ext
                        FROM
                                files
                        WHERE
                                path = %s AND
				name = %s AND
                                ext  = %s;
                """,
                        (path,name,ext)
                )
                return self._cursor.fetchone() != None

	def add_tag_groups(self,taggroups):
		"""Uses `add_tag_group` for each element of the passed list."""		
		for group in taggroups:
			self.add_tag_group(group)
		
	def add_tag_group(self,taggroup):
		"""Adds the passed group and it's child tags to the index."""
		self._cursor.execute(u'''
			INSERT INTO taggroups (
				fileid
			) VALUES (
				%s
			);
		''',
			(taggroup.fileid,)
		)
		taggroup.id = self._cursor.lastrowid
		self.add_tags(taggroup.tags)
		return taggroup.id

	def add_tags(self,tags):
		"""Uses `add_tag` for each element of the passed list."""
		for tag in tags:
			self.add_tag(tag)

	def add_tag(self,tag):
		"""Inserts a single tag into the index."""
		self._cursor.execute(u'''
			INSERT INTO tags (
				groupid,value,type,source
			) VALUES (
				%s,%s,%s,%s
			);
		''',
			(tag.groupid,tag.value,tag.type,tag.source)
		)
		tag.id = self._cursor.lastrowid
		return tag.id


	def _add_hash(self,value,table):
		# check if the hash is already added
		# if so return the entries id
		
		self._cursor.execute(u"""
			SELECT 
				id 
			FROM 
				"""+table+u"""
			WHERE
				value = %s;
		""",
			(value,)
		)
		
		res = self._cursor.fetchone()
		if res != None:
			return res[0]
		
		# if the hash isn't added yet
		# add it and return the generated id
		self._cursor.execute(u"""
			INSERT INTO """+table+u""" (
				value
			) VALUES (
				%s
			);
		""",
			(value,)
		)

		return self._cursor.lastrowid

	def add_md5(self,md5):
		return self._add_hash(md5,u"md5s")
	
	def add_puid(self,puid):
		if puid == None:
			return None
		return self._add_hash(puid,u"puids")
		
	def add_fingerprint(self,fingerprint):
		if fingerprint == None:
			return None
		return self._add_hash(fingerprint,u"fingerprints")

	def get_file_ids(self):
		self._cursor.execute(u"""
			SELECT 
				id
			FROM
				files
			""")
		ids = self._cursor.fetchall()
		simpleids = []
		for id_ in ids:
			simpleids.append(id_[0])
		return simpleids

	def get_file_without_tags(self,fileid,flags):
		q = u'''
			SELECT 
				s.id AS id,
				s.path AS path,
				s.name AS name,
				s.ext AS ext
		'''
		for flag in flags:
			if flag=='puid':
				q += u',p.value AS puid'
			elif flag=='md5':
				q += u',m.value AS md5'
			elif flag=='fingerprint':
				q += u',f.value AS fingerprint'
			else:
				q += u','+flag
		q += u'''\nFROM
				files AS s
			LEFT OUTER JOIN
				puids AS p
			ON
				s.puidid = p.id
			LEFT OUTER JOIN
				md5s AS m
			ON
				s.md5id = m.id
			LEFT OUTER JOIN
				fingerprints AS f
			ON
				s.fingerprintid = f.id
			WHERE
				s.id = %s;
		'''
		self._cursor.execute(q,(fileid,))
		res = self._cursor.fetchall()
		if res==():
			return None
		# now we need to transform the flat db structure
		# into an object oriented medel
		file_ = IndexedFile(res[0][0],res[0][1],res[0][2],res[0][3])
		i = 4
		for flag in flags:
			file_.flags[flag] = res[0][i]
			i=i+1
		return file_
	
	def get_file_taggroups(self,fileid):
		self._cursor.execute(u'''
			SELECT 
				g.id AS groupid,
				t.source AS source,
				t.id AS tagid,
				t.value AS value,
				t.type AS type
			FROM
				taggroups AS g, tags AS t
			WHERE
				g.fileid = %s AND
				t.groupid = g.id
			ORDER BY
				g.id;
		''',(fileid,))
		res = self._cursor.fetchall()

		if res==None:
			return None
		# creates an object oriented view of  
		# the flat relational view we get out of the database
		groups = []
		i = 0
		while i<len(res):
			groupid = res[i][0]
			group = TagGroup(groupid,fileid)
			while i<len(res) and res[i][0] == groupid:
				source = res[i][1]
				id_ = res[i][2]
				value = res[i][3]
				type_ = res[i][4]
				group.tags.append( FileTag(id_,value,type_,source,groupid) )
				i=i+1
			groups.append(group)
		return groups

	def get_file(self,fileid,flags):
		file_ = self.get_file_without_tags(fileid,flags)
		file_.taggroups = self.get_file_taggroups(fileid)

		return file_

	def _create_files_table(self):
		self._cursor.execute(u'''
			CREATE TABLE IF NOT EXISTS files (
				id          INTEGER PRIMARY KEY,

				path        VARCHAR NOT NULL,
				name        VARCHAR(255) NOT NULL,
				ext         VARCHAR(8) NOT NULL,
			
				size        INTEGER UNSIGNED NOT NULL,
				duration    INTEGER UNSIGNED,

				musicip_online  BOOL NOT NULL,
				musictype       VARCHAR(5),

				md5id         INTEGER UNSIGNED NOT NULL,
				fingerprintid INTEGER UNSIGNED,
				puidid        INTEGER UNSIGNED
			);
		''');
		
	def _create_md5s_table(self):
		self._cursor.execute(u"""
			CREATE TABLE IF NOT EXISTS md5s (
				id          INTEGER PRIMARY KEY,
				value       CHAR(32) UNIQUE NOT NULL
			);
		""")
	
	def _create_puids_table(self):
		self._cursor.execute(u"""
			CREATE TABLE IF NOT EXISTS puids (
				id          INTEGER PRIMARY KEY,
				value       CHAR(36) UNIQUE NOT NULL
			);
		""") 
		
	def _create_fingerprints_table(self):
		# the len of the value is fixed.
		# we have to use varchar cause char only
		# holds data up to 255 Byte
		self._cursor.execute(u"""
			CREATE TABLE IF NOT EXISTS fingerprints (
				id          INTEGER PRIMARY KEY,
				value       VARCHAR(756) UNIQUE NOT NULL
			);
		""") 
		
	def _create_taggroups_table(self):
		# the len of the value is fixed.
		# we have to use varchar cause char only
		# holds data up to 255 Byte
		self._cursor.execute(u"""
			CREATE TABLE IF NOT EXISTS taggroups (
				id          INTEGER PRIMARY KEY,
				fileid      INTEGER UNSIGNED NOT NULL
			);
		""") 
		
	def _create_tags_table(self):
		self._cursor.execute(u"""
			CREATE TABLE IF NOT EXISTS tags (
				id          INTEGER PRIMARY KEY,
				value       VARCHAR(255) NOT NULL,
				type        VARCHAR(10),
				source      VARCHAR(11),
				groupid     INTEGER UNSIGNED NOT NULL
			);
		""")

	def create_tables(self):
		"""Creates all needed tabels in the index."""
		self._create_files_table()
		self._create_taggroups_table()
		self._create_tags_table()
		self._create_md5s_table()
		self._create_puids_table()
		self._create_fingerprints_table()


























	#### OBSOLETE ####
		
	def _copy_hash_table_from_index(self,index,name):
		self._cursor.execute(u"""CREATE TABLE IF NOT EXISTS 
				"""+name+u""" (
					id SERIAL, PRIMARY KEY(id),
					UNIQUE(value)
				)
			SELECT 
				* 
			FROM 
				`"""+index+u"""`."""+name+u""";
		""")
	
	def _copy_md5s_table_from_index(self,index):
		self._copy_hash_table_from_index(index,u"md5s")
		
	def _copy_fingerprints_table_from_index(self,index):
		self._copy_hash_table_from_index(index,u"fingerprints")
		
	def _copy_puids_table_from_index(self,index):
		self._copy_hash_table_from_index(index,u"puids")
	
	def _copy_files_table_from_index(self,index):
		self._cursor.execute(u"""
			CREATE TABLE IF NOT EXISTS 
				files (
					id SERIAL, PRIMARY KEY(id),
					FOREIGN KEY (md5id) REFERENCES md5s.id,
					FOREIGN KEY (fingerprintid) REFERENCES fingerprints.id,
					FOREIGN KEY (puidid) REFERENCES puids.id
				)
			SELECT
				*
			FROM 
				`"""+index+u"""`.files;
		""")
		
	def _copy_tags_table_from_index(self,index):
		self._cursor.execute(u"""
			CREATE TABLE IF NOT EXISTS 
				taggroups (
					id SERIAL, PRIMARY KEY(id),
					FOREIGN KEY(fileid) REFERENCES files.id
				)
			SELECT
				*
			FROM
				`"""+index+u"""`.taggroups
		""")

	def _copy_tags_table_from_index(self,index):
		self._cursor.execute(u"""
			CREATE TABLE IF NOT EXISTS 
				tags (
					id SERIAL, PRIMARY KEY(id),
					FOREIGN KEY(groupid) REFERENCES taggroups.id
				)
			SELECT
				*
			FROM
				`"""+index+u"""`.tags
		""")

	def copy_tables_from_index(self,index):
		"""Copies all tables from `index` to the current index."""
		self._copy_md5s_table_from_index(index)
		self._copy_fingerprints_table_from_index(index)
		self._copy_puids_table_from_index(index)
		self._copy_files_table_from_index(index)
		self._copy_taggroups_table_from_index(index)
		self._copy_tags_table_from_index(index)
		
	def drop_tables(self):
		pass

	def add_tag_to_file(self,tag):
		self._cursor.execute(u'''
			INSERT INTO tags (
				file,value,type,source
			) VALUES (
				%s,%s,%s,%s
			);
		''',
			(fileid,value,type,source)
		)
	
	def add_tags_to_file(self,tags,fileid):
		if tags != []:
			q = u"""
				INSERT INTO tags (
					file,value,type,source
				) VALUES 
			"""
			vals = []
			for tag in tags:
				q+=u"(%s,%s,%s,%s),"
		
				vals.append(fileid)
				vals.append(tag.value)
				vals.append(tag.type)
				vals.append(tag.source)
			
			q = q[0:-1]+u";"
	
			self._cursor.execute(q,vals)
		
