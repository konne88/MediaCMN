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

#include "protocol.h"

#include <fcntl.h>
#include <stdio.h>
#include <sys/wait.h>

#include <iostream>

using namespace std;

static bool readBytes(int fd, unsigned char *buf, int size) {
    int ct = 0;
    while (ct < size) {
	unsigned char tmp[4096];

	int x = size - ct;
	if (x > 4096)
	    x = 4096;

	int n = read(fd, tmp, x);

	if (n <= 0) {
	    return false;
	}

	for (int i = 0; i < n; ++i) {
	    buf[ct + i] = tmp[i];
	}
	ct += n;
    }
    return true;
}

// This method only supports PCM/uncompressed format, with a single fmt
// chunk followed by a single data chunk
AudioData* loadWaveFile(int fd) {

    int srate = 0;
    int channels = 0;

    if (fd == -1)
	return 0;

    unsigned char hdr[36];
    if (!readBytes(fd, hdr, 36)) {
	close(fd);
	return 0;
    }
    if (hdr[0] != 'R' || hdr[1] != 'I' || hdr[2] != 'F' || hdr[3] != 'F') {
	close(fd);
	return 0;
    }
    // Note: bytes 4 thru 7 contain the file size - 8 bytes
    if (hdr[8] != 'W' || hdr[9] != 'A' || hdr[10] != 'V' || hdr[11] != 'E') {
	close(fd);
	return 0;
    }
    if (hdr[12] != 'f' || hdr[13] != 'm' || hdr[14] != 't' || hdr[15] != ' ') {
	close(fd);
	return 0;
    }

    long extraBytes = hdr[16] + (hdr[17] << 8) + (hdr[18] << 16) + (hdr[19] << 24) - 16;
    int compression = hdr[20] + (hdr[21] << 8);
    // Type 1 is PCM/Uncompressed
    if (compression != 1) {
	close(fd);
	return 0;
    }
    channels = hdr[22] + (hdr[23] << 8);
    // Only mono or stereo PCM is supported in this example
    if (channels < 1 || channels > 2) {
	close(fd);
	return 0;
    }
    // Samples per second, independent of number of channels
    srate = hdr[24] + (hdr[25] << 8) + (hdr[26] << 16) + (hdr[27] << 24);
    // Bytes 28-31 contain the "average bytes per second", unneeded here
    // Bytes 32-33 contain the number of bytes per sample (includes channels)
    // Bytes 34-35 contain the number of bits per single sample
    int bits = hdr[34] + (hdr[35] << 8);
    // Supporting othe sample depths will require conversion
    if (bits != 16) {
	close(fd);
	return 0;
    }
    
    // Skip past extra bytes, if any
    unsigned char extraskip[extraBytes];
    if(!readBytes(fd,extraskip,extraBytes)){
    	return 0;
    }
    
    // Start reading the next frame.  Only supported frame is the data block
    unsigned char b[8];
    if (!readBytes(fd, b, 8)) {
	close(fd);
	return 0;
    }
    // Do we have a fact block?
    if (b[0] == 'f' && b[1] == 'a' && b[2] == 'c' && b[3] == 't') {
	// Skip the fact block
    unsigned char factskip[12];
    if(!readBytes(fd,factskip,12)){
    	return 0;
    }
    
	// Read the next frame
	if (!readBytes(fd, b, 8)) {
	    close(fd);
	    return 0;
	}
    }
    
    // Now look for the data block
    if (b[0] != 'd' || b[1] != 'a' || b[2] != 't' || b[3] != 'a') {
   	close(fd);
	return 0;
    }
    
    // this will be 0 if ffmpeg is used
    // since it can't seek the stream to write this value
    // so we ignore this value and just read to the end if it is 0
    long bytes = b[4] + (b[5] << 8) + (b[6] << 16) + (b[7] << 24);

    // No need to read the whole file, just the first 135 seconds
    long bytesPerSecond = srate * 2 * channels;
    
    if(bytes == 0)
    	//maximum data is 2 gigabyte, getting a puid won't work with bigger files
    	bytes = 2*1000*1000*1000;
    
    // Now we read parts of the file until the eof or bytes is reached
    // bytesPerSecond is used as puffersize
    int readSize = bytesPerSecond;
    
    unsigned char* samples = NULL;
    int size = 0;
    while(size<bytes){
    	samples = (unsigned char*)realloc ( samples, size+readSize );
    	int n = read(fd,samples+size,readSize);
    	
    	if(n < 0){
    		delete[] samples;
    		close(fd);
    		return 0;
    	}
    	size += n;
    	if(n == 0)
    		break;
    }
    close(fd);

    long ms = (size/2)/(srate/1000);
    if ( channels == 2 ) ms /= 2;
    
    AudioData *data = new AudioData();

    data->setData(samples, OFA_LITTLE_ENDIAN, size/2, srate,
	    channels == 2 ? 1 : 0, ms, "wav");
    
    return data;
}

// explanation for popen
// http://www.lix.polytechnique.fr/~liberti/public/computing/prog/c/C/FUNCTIONS/popen.html
// http://www.opengroup.org/onlinepubs/009695399/functions/popen.html
// explanation for exec
// http://www.opengroup.org/onlinepubs/000095399/functions/exec.html
// explanation for wait
// http://linux.die.net/man/2/wait
// stdin etc filedescriptors
// http://learnlinux.tsf.org.za/courses/build/shell-scripting/ch12s04.html
// putting it all together (writing custom popen)
// http://wps.prenhall.com/wps/media/objects/510/522376/Molay_Unix_SourceCode/ch11/popen.c

//	Opens an audio file and converts it to a temp .wav file
//	Calls loadWaveFile to load the data
AudioData* loadAudioData(int fd) {
	int pid;
	int ret;
	int childout[2];
	
	if ( fd == -1)
		return NULL;	
	if ( pipe(childout) == -1 )
		return NULL;
	
	pid = fork();
	
	if (pid == 0){		//child
		// close the read part of the output
		if(close(childout[0]) == -1)
			exit(1);
		// redirect fd to stdin
		if(dup2(fd,0) == -1)
			exit(1);
		// redirect stdout to childout
		if(dup2(childout[1],1) == -1)
			exit(1);
		// close stderr of ffmpeg, cause it uses it for progress infos
		//if(close(2) == -1)
		//	exit(1);
		// exec ffmpeg
		execlp("ffmpeg","ffmpeg","-i","-","-f","wav","-",NULL);
		
		exit(1);
	}
	else if(pid > 0){	//parent
		// close the write part of the output
		if(close(childout[1]) == -1)
			return NULL;

		AudioData* data = loadWaveFile(childout[0]);

		if(waitpid(pid,&ret,0) == -1)
			return NULL;
			
	    if(ret != 0)
	    	return NULL;
	    
	    return data;
	}
	else {	//error forking
		return NULL;
	}	
}
