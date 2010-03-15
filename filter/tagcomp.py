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

from astrcmp import astrcmp

# constants to define what kind of tags we prefer
NONE_NONE_MUL = 1
TYPE_NONE_MUL = 2
TYPE_TYPE_MUL = 4
NO_MATCH_MUL  = 1
TYPE_MUL = {
	'artist':2,
	'release':2,
	'track':4,
	'duration':1,
	'date':1,
	'tracknumber':1,
	'genre':1,
	'label':1
}
SOURCE_MUL = {
	'metadata':3,
	'filename':2,
	'path':1,
	'musicbrainz':7,
	'musicip':2,
	None:1
}
SOURCE_RATING = {
	'musicbrainz':1,
	'musicip':0.9,
	'metadata':0.8,
	'filename':0.6,
	'path':0.2,
	None:0.0
}

def find_best_tag_of_type(ts,type,minRating):
	bestRating = minRating
	bestTag = None
	for t in ts:
		if t.type == type:
			rating = SOURCE_RATING[t.source]
			if rating >= bestRating:
				bestRating = rating
				bestTag = t
	return bestTag

def tag_group_similarity(tgs1,tgs2,exclude_sources):
	"""Calculates the similarity of two lists of groups of tags.
	`tgs1` and `tgs2` are those two lists, `exclude_sources` is a list
	of sources that will not be used, to calc the similarity
	"""
	# How to calculate group similarity
	#
	# Well let's assume we have two lists of tag groups tgs1 and tgs2.
	# We now need to compare each group from tgs1 with each group from
	# tgs2. We then pick the highest value and return that.
	#
	# This algorithm should work pretty well. Groups always represent one
	# set of tags, where either all of them are true or none of them are.
	# Since groups may be wrong we just use the best match.
	#	
	# Indeed with millions of tag groups it might be questionable if it is
	# smart to only pick out the best and discard all the wrong ones, but I
	# think that with so many tag groups (which is unrealistic) still that
	# single highest match would mean a lot, cause we always use tag similarity
	# to determine if already very strongly similar appearing files (same hash)
	# are the same. Chances that two songs have the same hash and a similar
	# tags group is unlikly.
	#
	# EXCEPT FOR WITH DIRECTORY TAGS WHERE THE SAME FILE STRUCTURE WOULD
	# MAKE ALL OF THEM BE THE SAME.
	highest = 0
	for ts1 in tgs1:
		if sources_used.find( ts1.source ) == -1:
			for ts2 in tgs2:
				if sources_used.find( ts2.source ) == -1:
					highest = max( tag_similarity(ts1,ts2),highest )
	return highest

def tag_similarity(tgs1,tgs2):
	"""Calculates the similarity of two lists of tags."""

	# How to calculate tag similarity
	#
	# one compares each the tag from ts1 with all tags from ts2
	# the result of the comparison is then stored in a 2D array 
	# with the height of ts1 and  width of ts2
	# 
	# to calculate the similarity of ts1 towards ts2 one iterates
	# throught ts1 and stores for each t1 the hightest similarity
	# it got to a tag in ts2
	# after all the maximum similarities are calculated they are
	# added up to one value. This value is then divided by
	# the total amount of tags in the list. 
	# this value represents the similarity of t1 towards t2
	# and should be >=0 and <=1.
	# equal is done to calculate the similarity of ts2 towards ts1
	#
	# the similarity of the ts that is heighter is returned
	# 
	# to make the whole thing more complicated, (and hopefully more
	# accurate) with each comparison of tags a multiplier is also
	# calculated. This multiplier is calculated using involved tag's
	# informatio that is independant of the value like rating and type
	#
	# The multiplier makes a tag weight more than other tags in the
	# same list. A multiplier of 2 is equal to the tag beeing added 
	# to the list twice.
	#
	# to speed it up, the ts1 similarity is calculated in the 
	# array generation loop. the ts2 similarity is calculated
	# in a loop that has array lookup
	# 
	# to implement the multiplier, a second 2d array is created, that 
	# stores the multiplier at the same position the similariy array
	# stores a coresponding similarity
	# 
	# if the maximal similarity value for a tag is searched, each value
	# is multiplied by the multiplier. 
	# The total amount of similarities isn't devided by the total number
	# of tags in the list but by the total amount of the multipliers
	#
	# for speed reasons, the similarity array actually stores the 
	# product of multiplier and similarity

	# variable names:
	#
	# sim stands for similarity
	# mul stands for multiplicator
	# t stands for tag
	# 1 is appended for the first tag list to be compared
	# 2 is appended for the second tag list to be compared
	# i stands for iterator
	# adding an s to a variable means that 
	# it has something to do with a list
	
	# generate 2d arrays and 
	# create the t1 similarity (marked with #)
	muls = []
	sims = []

	tsSim1 = 0			#
	tsSimSum1 = 0		#
	tsMul1 = 0			#
	for i1 in xrange(len(ts1)):
		muls.append([])
		sims.append([])
		tMaxSim1 = 0				#
		tMul1 = NO_MATCH_MUL		#
		for i2 in xrange(len(ts2)):
			t1 = ts1[i1]
			t2 = ts2[i2]
			type1 = t1.type
			type2 = t2.type
			
			mul = 0.0
			if type1 == None and type2 == None:
				mul = NONE_NONE_MUL
			elif type1 == None:
				mul = TYPE_NONE_MUL*TYPE_MUL[type2]
			elif type2 == None:
				mul = TYPE_NONE_MUL*TYPE_MUL[type1]
			elif type1 == type2:
				mul = TYPE_TYPE_MUL*TYPE_MUL[type1]
			else:
				mul = 0	
			
			mul = mul * SOURCE_MUL[t1.source] * SOURCE_MUL[t2.source]
			
			sim = astrcmp(t1.value.lower(),t2.value.lower())*mul
			muls[i1].append(mul)
			sims[i1].append(sim)
			
			if sim > tMaxSim1:						#
				tMaxSim1 = sim						#
				tMul1 = mul							#
				
		tsSimSum1 =	tsSimSum1 + tMaxSim1	#
		tsMul1 = tsMul1 + tMul1				#
	
	# calc the t2 similarity
	tsSim2 = 0
	tsSimSum2 = 0
	tsMul2 = 0
	for i2 in xrange(len(ts2)):
		tMaxSim2 = 0
		tMul2 = NO_MATCH_MUL
		for i1 in xrange(len(ts1)):		
			sim = sims[i1][i2]
			if sim > tMaxSim2:
				tMaxSim2 = sim
				tMul2 = muls[i1][i2]
		tsSimSum2 =	tsSimSum2 + tMaxSim2
		tsMul2 = tsMul2 + tMul2	
	
	# get the final similarity
	if tsMul1 != 0:
		tsSim1 = tsSimSum1 / tsMul1
	if tsMul2 != 0:
		tsSim2 = tsSimSum2 / tsMul2
	
	if tsSim1 > tsSim2:
		return tsSim1
	else:
		return tsSim2


