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
 
#ifndef __SIMPLEXML_H__
#define __SIMPLEXML_H__

#include <iostream>
#include <sstream>

template <class T>
inline std::string toString (const T& t)
{
	std::stringstream ss;
	ss << t;
	return ss.str();
}

void dataTagOut(const std::string& name, const std::string& value);
void startTagOut(const std::string& name);
void endTagOut(const std::string& name);

#endif
