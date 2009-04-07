/* MediaCMN - Tools to create a consistent music library.
 * Copyright (C) 2009 Konstantin Weitz
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 3
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 */

#include <iostream>
#include <utility>
#include <sys/types.h>
#include <unistd.h> 
#include <fcntl.h>
#include <stdio.h>

#include "protocol.h"
#include "musicdata.h"
#include "simplexml.h"

int main(int argc, char **argv) {
    startTagOut("files");
    
    // Go through each filename passed on the command line
    for (int i = 1; i < argc; ++i) {
    	startTagOut("file");
		
    	// convert the input file to wav data
    	string filename = string(argv[i]);
    	
    	dataTagOut("filename",filename);
    	
    	int file = open(filename.c_str(),O_RDONLY|0x8000);
    	
    	AudioData* data = loadAudioData(file);
    	
    	if(!data){
    		endTagOut("file");
    		continue;
    	}
    	
    	// get the fingerprint
    	if (!data->createPrint()) {
    		endTagOut("file");
    		delete data;
    	    continue;
    	}
    	
		dataTagOut("fingerprint",data->info.getPrint());
		dataTagOut("duration",toString(data->info.getLengthInMS()));
		
    	// Get the metadata.  
    	// Client id recved from http://www.musicdns.org
    	TrackInformation *info = data->getMetadata("378af2f8f41a4764a1f700a94fb40eb2", "cmnFingerprinter", true);
    	
    	if (info) {
    		dataTagOut("track",info->getTrack());
    		dataTagOut("puid",info->getPUID());
    		dataTagOut("artist",info->getArtist());
    		dataTagOut("release",info->getAlbum());
    		dataTagOut("tracknumber",toString(info->getTrackNum()));
    		dataTagOut("genre",info->getGenre());
    		dataTagOut("date",info->getYear());
    		dataTagOut("online","true");
    	}
    	else {
    		dataTagOut("online","false");
    	}
    	delete data;
    	
    	endTagOut("file");
    }
	
    endTagOut("files");
}
