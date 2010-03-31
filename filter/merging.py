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

# The problem of grouping songs
#
# well the first problem is that you should group the sobngs, so that it doesn't
# matter a which song you start or somthing like that. So it is very important, 
# that no song is worth more then another song for a reason that doesn't have to
# do with the song itsself. Let's assume
#
#        (a)
# 33%  /     \  66%
#    (b)-----(c)
#        66%
#  
# we could NOT go and say we start at b and group it only with, let's say;
# all songs that have a relation higher 50%. If we did so it would matter
# where we started and the result would be different starting at c.
#
# A fairly simple solution is to just go along the chain of high relations
# and group that way.
#
# But this leads to the following problem, that long chains can lead to
# totally different songs being grouped.
#
# There is this great song Wonderful World (WW) by Armstrong and Sam Cooke,
# some let's assume they were released in the following way, how would we 
# group the songs if only tags would matter?
# 
#  WW              66%      WW
#  Sam Cooke  (d) <---> (c) Sam Cooke
#  Album B     ^  \   /  ^  Album Mix
#              |   \ /33%|
#          33% |    x    | 66%
#              |   / \33%|
#  WW          v  /   \  v  WW
#  Armstrong  (a) <---> (b) Armstrong
#  Album A         66%      Album Mix
#
# Obviously the right grouping would be a,b and c,d but how is the computer
# supposed to know such a thing? If we replace the names by random letters
# how would we get the grouping right?
#
# Well we can state that the group a,b and c,d do make sense for a computer,
# since the elements of the group are strongly related (66%) among eachother.
# Interesting is that the groups a,d and b,c would not be stronly related,
# neither would be a,c and b,d. So if we knew that we would have to form
# two groups we could get the right result.
#
# This wouldn't work anymore if we removed d. Then there would be no difference
# between an a,b and c or an a and b,c grouping. So that case seems to be pretty
# unsolveable due to the lack of information and maybe a grouping of all of them
# would be the thing to do, or a grouping of none of them.
# 
# Let's introduce the average group similarity AGS.
# It is calculated by adding up all the connections that exist in a group
# and then dividing the result by the amount of relations.
#
# The a,b,c,d example above shows a relatively low AGS for grouping all songs.
# 
# AGS(a,b,c,d) = ( 3*33%+3*66% )/6 = 50%
#
# The less elements we put in a group the higher our AGS can be. I assume that
# would be 100% if there was a single element group since really the AGS is 
# representing how similar the elements of the group are, which is with one
# element 100%.
#
# In the example with only 3 elements our AGS would be rather high grouping all
# the items together.
#
# AGS(a,b,c) = ( 33%+2*66% )/3 = 55%
#
# With only two elements, the highest would be
#
# AGS(a,b) = 66%
#
# The total AGS tAGS, being the average AGS of all groups 
#
# 
# Well maybe be chaining isn't too bad. After all it is non discriminating,
# simple to implement and has relatively view realworld cases that I could think
# of it really failing to do its job.

from entries import Song

from tagcomp import tag_group_similarity,find_best_tag_group

class MergeFile(object):
    """Object holding all information needed to create a song
    Is basically a conclumeration of multiple, similar, files.
    """

    def __init__(self,file_ = None):
        """Constructs the conclumeration and is adding the optional `file_`"""
        self.taggroups = []
        self.sourcefiles = []
        self.flags = {}
        if file_ != None:
            self.add_source(file_)

    def add_source(self,file_):
        """Adds a source `file_` to the merge."""
        self.sourcefiles.append(file_.id)
        self.taggroups.extend(file_.taggroups)
        self.flags = file_.flags

    def to_song(self):
        """Creates a `Song` out of the data stored in itsself."""
        song = Song(None,self.sourcefiles[0],self.sourcefiles)
        song.duration = 1337
        song.musictype = 'other'

        # best tag group
        btg = find_best_tag_group(self.taggroups,0)

        for tag in btg.tags:
            if tag.type==u'artist':
                song.artist = tag.value
            elif tag.type==u'release':
                song.release = tag.value
            elif tag.type==u'track':
                song.track = tag.value
            elif tag.type==u'date':
                song.date = tag.value
            elif tag.type==u'tracknumber':
                song.tracknumber = tag.value
            elif tag.type==u'genre':
                song.genre = tag.value
            elif tag.type==u'label':
                song.label = tag.value

        return song

    def merge_with_mergefile(self,mf):
        """Merges this mergefile with another one called `mf`."""
        if self.flags != mf.flags:
            print "*********************************************************"
            print "*********************************************************"
            print
            print "ALERT! YOU ARE ABOUT TO ADD FILES WITH VERYING FLAGS!!!"
            print
            print "*********************************************************"
            print "*********************************************************"
        self.sourcefiles.extend(mf.sourcefiles)
        self.taggroups.extend(mf.taggroups)

    def __repr__(self):
        return str(self.taggroups)

def find_tagwise_similar_files(mf,mfs,level):
    """
    Merge one mergefile with all other mergefiles sharing a flag.
    Finds files similar to the passed `mf`.
    `mfs` is a list of all files that will be compared to the tags of `mf`.
    If the similarity of the tags is > level, they count as similar.
    Return a tupple containing a list of similar files and a list of
    unsimilar files.
    The similar files will include `mf` for sure
    """
    # this algorythm moves all similar entries from the mfs to the similar list
    similar = []
    for s in similar:
        for i in xrange(len(mfs)):
            # We can not use those groups of tags that were downloaded from the
            # internet since that would manipulate our result.
            # E.g. all files with identical puids would match 100% since
            # musicbrainz gives them all exactly the same result
            if tag_group_similarity(s.taggroups,mfs[i].taggroups, ('musicbrainz','musicdns')) > level:
                similar.append(mfs[i])
                del mfs[i]
    return similar,mfs

def merge_files_by_similar_tags(mfs,level):
    """
    Merge all mergefiles sharing a flag.
    Creates a list of `MergeFile`s. In this new list all elements
    of the `MergeFile` list `mfs` were merged.
    """
    result = []
    while len(mfs)>0:
        mf = mfs[0]
        del mfs[0]
        similar,mfs = find_tagwise_similar_files(mf,mfs,level)
        for s in similar:
            mf.merge_with_mergefile(s)
        result.append(mf)
    return result

def merge_files_by_flag_and_tags(mfs,level,flag):
    """
    Merge all mergefiles.
    Merge all files that have the same `flag` and similar tags.
    `mfs` represents all files that need to be merged.
    Returns a new list of mergefiles, holding all possible merges
    """
    if len(mfs)==0:
        return []
    else:
        mfs.sort(lambda a,b : int(a.flags[flag]-b.flags[flag]))
        mergefile = mfs[0]
        result = []
        group = [mergefile]
        flagval = mfs[0].flags[flag]
        for mf in mfs[1:]:
            if flagval != mf.flags[flag]:
                # a group just ended here. Check for similarity
                result.extend(merge_files_by_similar_tags(group,level))
                # a new group starts here
                mergefile = mf
                group = [mergefile]
                flagval = mf.flags[flag]
            else:
                group.append(mf)

        # here ends the very last group
        result.extend(merge_files_by_similar_tags(group,level))
    return result

def merge_files_by_md5(mfs):
        """
        Merge all files that have the same md5 hash.
        `mfs` represents all files that need to be merged.
        Make sure those files are sorted by their md5 hash!
        """
        if len(mfs)==0:
                return []
        else:
                mergefile = mfs[0]
                result = [mergefile]
                md5 = mfs[0].flags['md5id']

                for mf in mfs[1:]:
                        if md5 != mf.flags['md5id']:
                                mergefile = mf
                                result.append(mergefile)
                                md5 = mf.flags['md5id']
                        else:
                            mergefile.merge_with_mergefile(mf)
        return result

def _recursive_property_merge(songs,filters):   
    if len(songs) <= 1: 
        return songs

    # no filter left, everything that is still the same, must be merged 
    if len(filters) == 0:
        for s in songs[1:]:
            songs[0].sources.extend(s.sources)
        return songs[0:1]

    filt = filters[0]
    filts = filters[1:]

    songs.sort(filt)

    ret = []
    oldsong = songs[0]
    same = [oldsong]
    for s in songs[1:]:
        if filt(oldsong,s) == 0:    # they are the same
            same.append(s)
        else:
            ret.extend( _recursive_property_merge(same,filts) )
            oldsong = s
            same = [oldsong]
    
    ret.extend( _recursive_property_merge(same,filts) ) # merge the last matches

    return ret

def merge_songs_by_properties(songs):
    """
    Merges passed `songs` by comparing their properties. If they are the same
    they will be merged into one song.
    """

    filters = [ lambda a,b : cmp(a.track,b.track),
                    lambda a,b : cmp(a.release,b.release),
                    lambda a,b : cmp(a.artist,b.artist),
                    lambda a,b : cmp(a.date,b.date),
                    lambda a,b : cmp(a.tracknumber,b.tracknumber),
                    lambda a,b : cmp(a.label,b.label),
                    lambda a,b : cmp(a.release,b.release) ]
    
    return _recursive_property_merge(songs,filters)
