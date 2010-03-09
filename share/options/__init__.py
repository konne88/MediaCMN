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

import getopt

import check

class CommonCmnOptions(object):
	def __init__(self,name='',desc=''):
		self.index = 'cmn_index'
		self.user = 'root'
		self.pw = ''
		self._email = "konnew@gmx.de"
		self._appname = name
		self._appdesc = desc

		self._appargs = "[OPTION...]"
		self._opts = [
			('help','h',None,"display this help and exit",False),
			('index','i',"MYSQLDB",
				"MYSQLDB is the name of the mysql database, used to store the index",
				self.index),
			# set default to None, so it isn't shown when used as default
			('password','p',"PASSWORD","the USERNAME's password",None),
			('user','u',"USERNAME","the username used to login to mysql",self.user),
		]
		
	def usage(self):
		print "Usage: %s %s" % (self._appname,self._appargs)
		print self._appdesc
		print
		print "Mandatory arguments to long options are mandatory for short options too."
		
		for o in self._opts:		
			# writes short option
			if o[1] != None:
				s = '  -'+o[1]+', '
			else:
				s = '      '
			
			# write long option
			s+='--'+o[0]
			if o[2] != None:
				s+='=%s'%o[2]
			s+=' '
			
			# fill ip with spaces
			l = len(s)
			if l < 30:
				s += ' '*(30-l)
			
			# write message
			s+=o[3].replace('\n','\n'+30*' ')
			
			# write default value
			if o[2] == None:
				if o[4] == True:
					s+='\n'+30*' '+"(enabled by default)"
			elif o[4] != None:
				v = unicode(o[4])
				if v == '':
					v = "is an empty string"
				s+='\n'+30*' '+"(default %s)" % v
			
			# print the string
			print s
			
		print
		print "Report bugs to <%s>" % self._email
	
	def _handle_unused_args(self,args):
		return None
	
	def _all_options_loaded(self):
		return None
	
	def _set_option_value(self,opt,val):
		q = None
		if opt == 'help':
			q = 0
		elif opt == 'index':
		  	v = check.make_mysql_identifier(val)
		  	if v == None:
		  		print "Passed index is not a valid mysql database name."
		  		q = 1
		  	else:
		  		self.index = v
		elif opt == 'password':
			self.pw = val
		elif opt == 'user':
			self.user = val
		return q

	def print_sep(self):
		print '----------------------------------------------'		
		
	def print_init(self):
		print 'Starting',self._appname
		self.print_sep()

	def print_done(self):
		print self._appname, "done"
		self.print_sep()

	def print_terminated(self):
		print
		self.print_sep()
		print self._appname, "terminated."
		self.print_sep()

	def parse_cmdline_arguments(self,argv):
		self.appname = argv[0]
		argv = argv[1:]
		quit = None
		
		sopts =''
		lopts =[]
		for o in self._opts:
			sopts+=o[1]
			lopt=o[0]
			if o[2]:
				sopts+=':'
				lopt+='='
			lopts.append(lopt)
			
		try:
			params, args = getopt.getopt(argv, sopts, lopts) 

			for param, arg in params:
				for o in self._opts:
					if param in ('--'+o[0],'-'+o[1]):					
						if o[2] != None:
							q = self._set_option_value(o[0],arg)
						else:
							q = self._set_option_value(o[0],True)
						
						if q!=None:
							quit = q
						
						break
				
			q = self._handle_unused_args(args)
			if q!=None:
				quit = q
			
			q = self._all_options_loaded()
			if q!=None:
				quit = q
		
		except getopt.GetoptError, e:
			print e
			quit = 1
		
		if quit != None:
			self.usage()
			exit(quit)


class IndexOptions(CommonCmnOptions):
	def __init__(self):
		super(IndexOptions,self).__init__()
		self.drop = False
		self._opts.append(('drop','d',None,"drop all database entries in INDEX",self.drop))
	
	def _set_option_value(self,opt,val):
		q = None

		if opt == 'drop':
			self.drop = val
		else:
			r = super(IndexOptions,self)._set_option_value(opt,val)
			if r != None:
				q = r
		return q
		
class CopyIndexOptions(IndexOptions):
	def __init__(self):
		super(CopyIndexOptions,self).__init__()
		self.targetIndex = None
		self._opts.append(('copy','c',"MYSQLDB","copy all entries from the index"
			" databse to the MYSQLDB database\n"
			"if this option is used, all operations are performed on the copy"
			" of the index\n"
			"use with -d to remove entries from the target index before copying\n"
			"using this option you can protect your index from accidental altering",
			self.targetIndex))
	
	def _set_option_value(self,opt,val):
		q = None
		if opt == 'copy':
		  	v = check.make_mysql_identifier(val)
		  	if v == None:
		  		print "Passed copy target index is not a valid mysql database name."
		  		q = 1
		  	else:
		  		self.targetIndex = v
		else:
			r = super(CopyIndexOptions,self)._set_option_value(opt,val)
			if r != None:
				q = r
		
		return q
		
	def _all_options_loaded(self):
		quit = super(CopyIndexOptions,self)._all_options_loaded()
		
		if self.targetIndex == None and self.drop == True:
			print "Drop options can't be used without the copy option."
			quit=1
			
		return quit
