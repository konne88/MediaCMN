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

# description of what is valid
# http://dev.mysql.com/doc/refman/5.0/en/identifiers.html
def make_mysql_identifier(name):
	if name!='' and name.find('/')==-1 and name.find('\\')==-1 and name.find('.')==-1 and len(name) <= 64:
		return name.replace('`','``')
	else:
		return None

def make_float_between_zero_and_one(v):
	try:
		l = float(v)
		if 0<=l and l<=1:
			return l
		else:
			return None
	except:
		return None

def make_positive_int(v):
	try:
		r = int(v)
		if r < 0:
			return None
		return r
	except:
		return None

