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

import os
from subprocess import *

from mutagen.easyid3 import EasyID3
import mutagen.easyid3 as easyid3 

# mutagen
# http://code.google.com/p/quodlibet/wiki/Mutagen
# http://svn.sacredchao.net/svn/quodlibet/trunk/mutagen/TUTORIAL
# popen
# http://docs.python.org/library/subprocess.html#subprocess.PIPE

def transform_to_mp3(copyname,fullname):
    argv = [u"ffmpeg",u"-i",copyname,u'-ab',u'256k',fullname]
    Popen(argv, stdout=PIPE,stderr=PIPE).communicate()

def set_file_id3_tags(fullname,song):
    # delete the old version tags
    easyid3.delete(fullname, delete_v1=True, delete_v2=True)

    infos = {
        u'track':None,
        u'release':None,
        u'artist':None,
        u'tracknumber':None,
        u'date':None,
        u'genre':None
    }

    # fill the infos structure with information about the song
    for k in infos:
        attr = getattr(song, k)
        infos[k] = attr
    
    mapping = {
        u'track':u'title',
        u'release':u'album',
        u'artist':u'artist',
        u'tracknumber':u'tracknumber',
        u'genre':u'genre',
        u'date':u'date'
    }
    
    # set the mp3 metatags
    meta = EasyID3()
    
    for k in infos:
        try:
            if infos[k] != None:
                meta[mapping[k]] = infos[k]
        except KeyError:
            pass

    meta.save(fullname,v1=2)
