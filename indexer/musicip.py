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
import xml.dom.minidom as xml

from share.entries import TagGroup, FileTag

# xml parser
# http://docs.python.org/library/xml.dom.minidom.html
#
# popen
# http://docs.python.org/library/subprocess.html#subprocess.PIPE

def _get_text(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

# returns a tupple of
#   [0] fingerprint
#   [1] puid
#   [2] a list of tags
def generate_fingerprint_and_lookup_tags_if_online (fullname):
	argv = ["cmnfingerprinter",fullname]
	
	cmnf = Popen(argv, stdout=PIPE, stderr=PIPE)
	o = cmnf.communicate()[0]

	fingerprint = None
	puid = None
	taggroups = [TagGroup(None,None)]
	online = False
	playable = False
	duration = 0

	if cmnf.returncode == 0:
		dom = xml.parseString(o)
	
		# parse the first file that was returned
		props = dom.getElementsByTagName("file")[0].getElementsByTagName("*")

		for p in props:
			name = p.tagName
			text = _get_text(p.childNodes)
			if name == "puid":
				puid = text
			elif name == "fingerprint":
				fingerprint = text
			elif name == "filename":
				pass
			elif name == 'online': 
				if text == 'true':
					online = True
			elif name == 'playable':
				if text == 'true':
					playable = True
			elif name == 'duration':
				duration = int(text)
			else:
				taggroups[0].tags.append(FileTag(None,text,name,'musicip',None))
		
	return fingerprint,puid,taggroups,online,playable,duration

