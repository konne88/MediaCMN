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

import sys
import time

from musicbrainz2.webservice import Query, TrackFilter, WebServiceError

from tags.tag import Tag

# how to use musicbrainz2
# http://musicbrainz.org/doc/PythonMusicBrainz2

# the server should only be called once a second
# http://wiki.musicbrainz.org/XMLWebService#Limiting_Connections_to_the_MusicBrainz_Web_Service
_lastServerCall = 0

def get_puid_tags(puid):
	global _lastServerCall
	
	# wait at least a second
	while True:
		currentTime = time.time()
		if currentTime >= _lastServerCall+1:
			_lastServerCall = currentTime
			break
		time.sleep(0.05)

	q = Query()

	res = []

	try:
		f = TrackFilter(puid=puid)
		results = q.getTracks(f)
	except WebServiceError, e:
		print e
		return res
		
	for result in results:
		track = result.track
		artist = track.artist
		
		# for all releases in the track add a new set of tags
		# to the result. this way we don't choose the wrong one		
		rels = track.releases
		for release in rels:
			ts = []
			ts.append( Tag(track.title,"track","musicbrainz") )
			ts.append( Tag(artist.name,"artist","musicbrainz") )
			ts.append( Tag(unicode(track.duration),"duration","musicbrainz") )
			ts.append( Tag(release.title,"release","musicbrainz") )
			ts.append( Tag(unicode(release.tracksOffset),"tracknumber","musicbrainz") )
			
			res.append(ts)

	return res

