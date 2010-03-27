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
from entries import FileIndexConnectionWithTags, Tag
from filter.entries import Song

class OrganizerIndex(Index):
	def __init__(self,dbname,user,pw):
		super(OrganizerIndex,self).__init__(dbname,user,pw)

	def get_song_ids(self):
		self._cursor.execute(u"""
			SELECT 
				id
			FROM
				songs
			""")
		ids = self._cursor.fetchall()
		simpleids = []
		for id_ in ids:
			simpleids.append(id_[0])
		return simpleids

	def get_song_with_sourcefiles(self,id_):
		song = self.get_song(id_)
		files = []
		flags = ('duration','musictype')
		for source in song.sources:
			file_ = self.get_file_without_tags(source,flags)
			files.append(file_)
		return song, files

	def get_song(self,id_):
		"""Get all songs from the index."""
		self._cursor.execute(u'''
			SELECT 
				id, artist, `release`, track, date, tracknumber,
				genre, label, s.fileid AS fileid,
				musictype, copyid, duration
			FROM
				songs
			LEFT JOIN
				song_sources AS s
			ON
				id = s.songid
			WHERE
				id = %s;
			''',id_)
		res = self._cursor.fetchall()
		if len(res) == 0:
			return None
		# now we need to transform the flat db structure
		# into an object oriented model
		song = Song(res[0][0],None,[])
		song.artist = res[0][1]
		song.release = res[0][2]
		song.track = res[0][3]
		song.date = res[0][4]
		song.tracknumber = res[0][5]
		song.genre = res[0][6]
		song.label = res[0][7]

		# get the sources
		for row in res:
			song.sources.append(row[8])
		
		return song
















#### obsolte ####
















	
	@staticmethod
	def _create_file(res,i,fs):
		id   = res[i][0]
		path = res[i][1]
		name = res[i][2]
		ext  = res[i][3]
		
		ts = []
		while True:
			i = OrganizerIndex._create_tag(res,i,ts)
			if len(res) == i or id!=res[i][0]:
				break
	
		fs.append( FileIndexConnectionWithTags(id,path,name,ext,ts) )
		return i

	@staticmethod
	def _create_tag(res,i,ts):
		value = res[i][4]
		type = res[i][5]
		source = res[i][6]
	
		if value != None:
			ts.append( Tag(value,type,source) )
	
		return i+1
		
	@staticmethod
	def _create_files_from_flat_list(res):
		fs = []
		i = 0
		while i<len(res):
			i = OrganizerIndex._create_file(res,i,fs)
	
		return fs

	def get_all_files_with_tags_from_index(self,index):
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
		
		fs = OrganizerIndex._create_files_from_flat_list(res)
		return fs
	
	def copy_every_table_except_for_files_from_index(self,index):
		self.copy_md5s_table_from_index(index)
		self.copy_fingerprints_table_from_index(index)
		self.copy_puids_table_from_index(index)
		self.copy_tags_table_from_index(index)
	
	def copy_file_from_index_with_new_fullname(self,id,newPath,newName,newExt,index):
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
		
