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

import MySQLdb

class db:
	def __init__(self,dbname,user,pw):
		self._db     = MySQLdb.connect(passwd=pw,user=user,db=dbname,use_unicode = True,charset='utf8')
		self._cursor = self._db.cursor()

	def add_tags(self,tags,fileid):
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

		return self._db.insert_id()

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
			
	def add_file(self,path,name,extension,size,online,md5id,fingerprintid,puidid):
		self._cursor.execute(u"""
			INSERT INTO files (
				path,name,extension,size,online,md5,fingerprint,puid
			) VALUES (
				%s,%s,%s,%s,%s,%s,%s,%s
			);
		""",
			(path,name,extension,size,online,md5id,fingerprintid,puidid)
		)
		return self._db.insert_id()

	def is_file_added(self,path,name,extension):
		self._cursor.execute(u"""
			SELECT 
				path,name,extension 
			FROM 
				files
			WHERE
				path      = %s AND
				name      = %s AND
				extension = %s;
		""",
			(path,name,extension)
		)
	
		return self._cursor.fetchone() != None

	def create_tables(self):
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
		self._cursor.execute(u"""
			CREATE TABLE IF NOT EXISTS md5s (
				id          SERIAL, PRIMARY KEY(id),
				value       CHAR(32) CHARSET 'latin1' BINARY UNIQUE NOT NULL
			);
		""")
		self._cursor.execute(u"""
			CREATE TABLE IF NOT EXISTS puids (
				id          SERIAL, PRIMARY KEY(id),
				value       CHAR(36) CHARSET 'latin1' BINARY UNIQUE NOT NULL
			);
		""") 
		# the len of the value is fixed.
		# we have to use varchar cause char only
		# holds data up to 255 Byte
		self._cursor.execute(u"""
			CREATE TABLE IF NOT EXISTS fingerprints (
				id          SERIAL, PRIMARY KEY(id),
				value       VARCHAR(756) CHARSET 'latin1' BINARY UNIQUE NOT NULL
			);
		""") 
		self._cursor.execute(u"""
			CREATE TABLE IF NOT EXISTS tags (
				id          SERIAL, PRIMARY KEY(id),
				file        BIGINT UNSIGNED NOT NULL, FOREIGN KEY (file) REFERENCES files.id,
				value       VARCHAR(255) CHARSET 'utf8' NOT NULL,
				type        ENUM (
					'artist',
					'release',
					'track',
					'duration',
					'date',
					'tracknumber',
					'genre',
					'label'
				) CHARSET 'utf8',
				source      ENUM (
					'metadata',
					'filename',
					'path',
					'musicbrainz',
					'musicip'			
				) CHARSET 'utf8'
			);
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

