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

#include "simplexml.h"

// Replaces what is mentioned here
// http://www.hdfgroup.org/HDF5/XML/xml_escape_chars.htm
std::string escapeXml (std::string in)
{
	typedef std::pair<std::string,std::string> rep;
	rep reps[] = {
		rep("\"","&quot;"),
		rep("'" ,"&apos;"),
		rep("&" ,"&amp;"),
		rep("<" ,"&lt;"),
		rep(">" ,"&gt;")
	};
	
	for(int x=0 ; x<5 ; ++x){
		std::string r = reps[x].first;
		std::string w = reps[x].second;
		
		int rlen = r.length();
		int pos = 0;
		
		while (true) {
			pos = in.find(r,pos);
		    if (pos == -1) {
		    	break;
		    } else {
		    	in.erase(pos, rlen);
		    	in.insert(pos, w);
		    	pos += rlen;
		    }
		}
	}
	return in;
}

void dataTagOut(const std::string& name, const std::string& value){
	if(value != "" && value != "0"){
		std::cout 
		<< "\t<" << name << ">"
		<< escapeXml(value)
		<< "</" << name << ">\n";
	}
}

void startTagOut(const std::string& name) {
	std::cout << "<" << name << ">\n";
}

void endTagOut(const std::string& name) {
	std::cout << "</"<< name <<">\n";
}

