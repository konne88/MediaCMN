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

from subprocess import *

from mutagen.mp3 import MP3,InvalidMPEGHeader,HeaderNotFoundError
from mutagen.asf import ASF,ASFHeaderError

from share.entries import FileTag, TagGroup

# mutagen
# http://code.google.com/p/quodlibet/wiki/Mutagen
# http://svn.sacredchao.net/svn/quodlibet/trunk/mutagen/TUTORIAL

def get_from_file(fullname,metaExt):
    metaExt = metaExt.lower()
    trans = []
    meta = None
    
    #try:
    argv = [u"file",fullname]
    # the file cmd prints the filename and adds the filetype after a ':'
    # we use rsplit since filename may contain a :
    res = Popen(argv, stdout=PIPE).communicate()[0].rsplit(':',1)
    
    if len(res) != 2:
        return []
    
    fileType = res[1]

    if fileType.find("ID3") != -1:
        metaExt = ".mp3"
    elif fileType.find("ASF") != -1:
        metaExt = ".wma"

    #id3
    if metaExt in (".tta",".mp3",".mp2"):
        try:
            meta = MP3(fullname)
        except InvalidMPEGHeader:
            meta = {}
        except HeaderNotFoundError:
            meta = {}
        # http://www.id3.org/id3v2.4.0-frames
        trans = {
        'TPE1': u'artist',
        'TPE2': u'artist',
        'TCON': u'genre',
        'TALB': u'release',
        'TIT2': u'track',
        'TDRC': u'date',
        'TRCK': u'tracknumber',
        'TPUB': u'label'}
    
    #asf
    elif metaExt in (".wma",):
        try:
            meta = ASF(fullname)
        except ASFHeaderError:
            meta = {}
        trans = {
        'WM/Year'        : u'date',
        'Author'         : u'artist',
        'WM/AlbumArtist' : u'artist',
        'WM/AlbumTitle'  : u'release',
        'WM/TrackNumber' : u'tracknumber',
        'Title'          : u'track',
        'WM/Publisher'   : u'label',
        'WM/Genre'       : u'genre'}
        
    #apev2 not yet implemented
    if metaExt in (".mpc", ".mp+",".wv",".ofr", ".ofs",".ape",".tak"):
        pass
    #mp4 not yet implemented
    elif metaExt in (".m4a",".m4b",".m4p",".mp4"):
        pass
    #vobis not yet implemented
    elif metaExt in (".flac",".oggflac",".spx",".oggtheora",".ogg"):
        pass

    taggroup = TagGroup(None,None)

    for t in trans:
        try:
            d = unicode(meta[t][0])
            taggroup.tags.append( FileTag(None,d,trans[t],'metadata',None) )
        except KeyError:  # this tag doesn't exist in the file
            pass
    
    return [taggroup]
    
if __name__ == "__main__":
    s= [
    ["Benzin.mp3",".mp3"],
    ["10 All We Are.wma",".wma"]]
    
    print "Testing the extraction of tags from file metadata."
    print "Place the following files into the src directory"
    for i in s:
        print s[0]
    print "--------------------------------------------------"
    print 
    
    for i in s:
        print i
        print get_from_file_metadata(i[0],i[1])
        print
