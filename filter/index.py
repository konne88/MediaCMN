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
from share.entries import FileTag, TagGroup
#from groupfilter import filter_check_groups_using_tags, filter_unchecked

class FilterIndex(Index):
	def __init__(self,dbname,user,pw):
		super(FilterIndex,self).__init__(dbname,user,pw)

	def drop_tables(self):
		self._cursor.execute(u'''DROP TABLE IF EXISTS 
			songs, 
			song_sources;
		''')

	def _create_songs_table(self):
		self._cursor.execute(u'''
			CREATE TABLE IF NOT EXISTS songs (
				id          SERIAL, PRIMARY KEY(id),
				copyid      BIGINT UNSIGNED NOT NULL, FOREIGN KEY (copyid) REFERENCES files.id,
				
				duration    INT UNSIGNED NOT NULL,
				artist      VARCHAR(255) CHARSET 'utf8',
				`release`   VARCHAR(255) CHARSET 'utf8',
				track       VARCHAR(255) CHARSET 'utf8',
				date        VARCHAR(255) CHARSET 'utf8',
				tracknumber VARCHAR(255) CHARSET 'utf8',
				genre       VARCHAR(255) CHARSET 'utf8',
				label       VARCHAR(255) CHARSET 'utf8',

				musictype   ENUM (
					'mp3',
					'other'
				) CHARSET 'utf8' NOT NULL
			);
		''')

	def _create_song_sources_table(self):
		self._cursor.execute(u'''
			CREATE TABLE IF NOT EXISTS song_sources (
				songid      BIGINT UNSIGNED NOT NULL, FOREIGN KEY (songid) REFERENCES songs.id,
				fileid      BIGINT UNSIGNED NOT NULL, FOREIGN KEY (fileid) REFERENCES files.id
			);
		''')
		return self._db.insert_id()
		
	def create_tables(self):
		self._create_songs_table()
		self._create_song_sources_table()
		
	def add_sources(self,songid,sources):
		s = []
		q = ''
		for source in sources:
			s.append(songid)
			s.append(source)
			q+=u'(%s,%s),'
		q = q[0:-1]+u";"

		self._cursor.execute(u'''
			INSERT INTO song_sources (
				songid,fileid
			) VALUES '''+q,s)

	def add_songs(self,songs):
		"""Insert multiple songs into the index."""
		for s in songs:
			self.add_song(self,s)		
		
	def add_song(self,song):
		"""Inserts a song into the index."""
		self._cursor.execute(u'''
			INSERT INTO songs (
				copyid,	duration, artist, `release`, track,
				date, tracknumber, genre, label, musictype
			) VALUES (
				%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
			);
		''',
			(song.copyid, song.duration, song.artist,
			song.release, song.track, song.date, song.tracknumber,
			song.genre, song.label, song.musictype)
		)
		song.id = self._db.insert_id()
		self.add_sources(song.id,song.sources)
		return song.id

	def get_music_file_ids_md5_ordered(self):
		self._cursor.execute(u'''
			SELECT 
				id
			FROM
				files
			WHERE
				musictype IS NOT NULL
			ORDER BY
				md5id;
			''')
		ids = self._cursor.fetchall()
		simpleids = []
		for id_ in ids:
			simpleids.append(id_[0])
		return simpleids


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

