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

import _mysql_exceptions

from share.index import Index
from entries import Tag, FilePuidWithTags

class TaggerIndex(Index):
	def __init__(self,dbname,user,pw):
		super(TaggerIndex,self).__init__(dbname,user,pw)

	@staticmethod				
	def _create_file(res,i,fs):
		id = res[i][0]
		puid = res[i][1]
	
		ts = []
	
		while True:
			i = TaggerIndex._create_tag(res,i,ts)
			if len(res) == i or res[i][0] != id:
				break
			
		fs.append( FilePuidWithTags(id,puid,ts) )
		return i

	@staticmethod
	def _create_tag(res,i,ts):
		value = res[i][2]
		type = res[i][3]
		rating = res[i][4]
	
		if value != None:
			ts.append( Tag(value,type,rating) )
	
		return i+1

	@staticmethod
	def _create_files_from_flat_list(res):
		fs = []
		i = 0
		while i<len(res):
			i = TaggerIndex._create_file(res,i,fs)
	
		return fs
	
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
		
		fs = TaggerIndex._create_files_from_flat_list(res)
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

	def set_file_musicbrainzcon(self,fileid,val):
		self._cursor.execute(u'''UPDATE files SET musicbrainzcon = %s 
					 WHERE id = %s''',(val,fileid))

	def append_to_files_table(self):
		try:
			self._cursor.execute(u'''ALTER TABLE files 
						 ADD musicbrainzcon BOOL NOT NULL;''')
		except _mysql_exceptions.OperationalError as err:
			if err[0] != 1060:
				raise
			# if 1060 this means that the column was already added
