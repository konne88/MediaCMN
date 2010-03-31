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

from share.options import CommonCmnOptions
from share.options import check

#http://www.rubyrobot.org/article/duplicate-a-mysql-database
#mysqladmin create DB_name -u DB_user --password=DB_pass mysqldump -u DB_user --password=DB_pass DB_name | mysql -u DB_user --password=DB_pass -h DB_host DB_name

class FilterOptions(CommonCmnOptions):
    def __init__(self):
        super(FilterOptions,self).__init__()
        self.filter = 'mpft'
        self.level = 0.0
        
        self._appname = "Filter"
        self._opts.append(('level','l',"NUMBER","some filters find duplicate files"
            " by scanning them for acoustic similarity\n"
            "that is important because the same track will look different to the computer\n"
            "depending on what encoding is used, but will still sound alike\n"
            "because of the nature of finding duplicates by similarity,\n"
            "the filter may make mistakes\n"
            "to find such mistakes the filter can also check if the tags of files\n"
            "sounding alike are also similar"
            "NUMBER is a value between 0 and 1. if 0 is passed, tags don't matter\n"
            "to the filter. the closer the value is to 1 the more the tags need to\n"
            "be similar in order for two files to be seen as the same",
            self.level))
        
        self._opts.append(('filter','f',"FILTER","FILTER is a combination"
            " of the following options:\n"
            "m  merge all files with a duplicate md5 hash\n"
            "f  merge all files with a duplicate fingerprint\n"
            "   makes use of the level argument\n"
            "p  merge all files with a duplicate puid\n"
            "   makes use of the level argument\n"
            "t  merge all files with duplicate tags",
            self.filter))
                
        self._appdesc="Filter the index by merging similar songs."

    def _set_option_value(self,opt,val):
        q = None
        if opt == 'level':
            v = check.make_float_between_zero_and_one(val)
            if v == None:
                print "The level argument is not a number between 0 and 1"
                q = 1
            else:
                self.level = val
        elif opt == 'filter':
            self.filter = val
        else:
            r = super(FilterOptions,self)._set_option_value(opt,val)
            if r != None:
                q = r
        return q

