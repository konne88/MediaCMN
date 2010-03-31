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

class TaggerIndex(Index):
    def __init__(self,reference):
        super(TaggerIndex,self).__init__(reference)

    def set_file_musicbrainz_online(self,fileid,val):
        self._cursor.execute(u'''UPDATE files SET musicbrainz_online = %s 
                     WHERE id = %s''',(val,fileid))

    def append_to_files_table(self):
        try:
            self._cursor.execute(u'''ALTER TABLE files ADD 
                musicbrainz_online BOOL NOT NULL DEFAULT false;''')
        except _mysql_exceptions.OperationalError as err:
            if err[0] != 1060:
                raise
            # if 1060 this means that the column was already added

    def get_file_ids_if_puid_and_not_online(self):
        self._cursor.execute(u'''
            SELECT 
                id
            FROM
                files
            WHERE
                puidid IS NOT NULL AND
                NOT musicbrainz_online
            ;''')
        ids = self._cursor.fetchall()
        simpleids = []
        for id_ in ids:
            simpleids.append(id_[0])
        return simpleids

