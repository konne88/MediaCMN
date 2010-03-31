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
from filter.entries import Song

class OrganizerIndex(Index):
    def __init__(self,reference):
        super(OrganizerIndex,self).__init__(reference)

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
            ''',(id_,))
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

