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

import os.path
import os
import shutil

from organizer.mp3file import transform_to_mp3, set_file_id3_tags

def get_copyfile(files):
    return files[0]

def _create_path_parts(path):
    pathParts = path.split('/')
    usedParts = '/'
    for p in pathParts:
        usedParts = os.path.join(usedParts,p)
        if not os.path.isdir(usedParts):
            os.mkdir(usedParts)

def create_source_symbols(path,files,copyfile,fullname):
    # create all the directories the file lies in
    _create_path_parts(path)

    # create source links
    i = 1
    for file_ in files:
        if file_.get_fullname() == copyfile.get_fullname():
            os.symlink(file_.get_fullname(),os.path.join(path,"copyfile"))
        else:
            os.symlink(copyfile.get_fullname(),os.path.join(path,"source %d"%i))
            i = i+1

    # create fullname link
    os.symlink(fullname,os.path.join(path,"targetfile"))

def copy_file_to_target(filename,copyname,ismp3,song):
    # create all the directories the file lies in   
    _create_path_parts( os.path.dirname(filename) )

    # now actually copy the file
    if ismp3:
        shutil.copyfile(copyname,filename)
    else:
        transform_to_mp3(copyname,filename)

    # and write id3 tags
    set_file_id3_tags(filename,song)
    
def get_new_filename(song,target,pattern,strict):
    """
    Creates the new relative name for a `song` in the music libarary.
    `patter` describes how the new name of the file should be created,
    `strict` will determine what characters are legal in a filename.
    So why do we pass `target` if we return a relative path?
    Well we do that so that we can check whether the file already
    exists and if so we can append it with some cool number.
    Then why don't we just return the aboslute path. Because then we 
    can't work that easily with it anymore. For example when creating 
    the symbolic references.
    """
    #define what s.th. is named if it's empty
    defaults = {
        u'track':u"Unknown Track",
        u'release':u"Unknown Release",
        u'artist':u"Unknown Artist",
        u'tracknumber':u"0",
        u'date':u"Unknown Date",
        u'genre':u"Unknown Genre"
    }

    # calc the infos about the song 
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
        infos[k] = getattr(song, k)
        if infos[k] == None:
            infos[k] = defaults[k]
        else:
            # remove the directory seperators,
            # so that names can't change directory structure
            infos[k] = infos[k].replace(u'/',u'-')
            # make tracknumber 2 digits
            if k == u'tracknumber':
                if len(infos[k]) == 1:
                    infos[k] = u"0"+infos[k]

    # create the filename from the template string
    reps = {
        u't':infos[u'track'],
        u'r':infos[u'release'],
        u'a':infos[u'artist'],
        u'n':infos[u'tracknumber'],
        u'%':u'%'
    }
    
    name = u''
    lastCharWasPercent = False
    for c in pattern:
        if c == '%':
            lastCharWasPercent = True
            continue        
        if lastCharWasPercent == True:
            try:
                name += reps[c]
            except KeyError:
                name += u'%'+c              
        else:
            name += c
        
        lastCharWasPercent = False
    
    # remove illegal chars from the filename ('/' was removed earlier)
    nogoes = None
    if strict >= 1:
        nogoes = (u'\0',u'\\',u':',u'*',u'?',u'"',u'<',u'>',u'|')
    else:
        nogoes = (u'\0',)
    
    for n in nogoes:
        name = name.replace(n,u'-')
    
    # check if the lenghts of directories and filenames are right,
    # 220 is to low of a value allowing for the extension
    # http://en.wikipedia.org/wiki/Comparison_of_file_systems#cite_note-note-12-8
    pathParts = name.split('/')
    for p in pathParts:
        if len(p) > 220:
            p = p[0:220]
    name = '/'.join(pathParts)
    
    # and finally append the extension
    # if files exists already append with a number
    # return the relative not the absolute path
    ext = '.mp3'
    i = 1
    relativename = name+ext
    fullname = os.path.join(target,relativename)
    while(True):
        if os.path.exists(fullname):
            relativename = name+(u" (%d)"%i)+ext
            fullname = os.path.join(target,relativename)
            i=i+1
        else:
            return relativename
