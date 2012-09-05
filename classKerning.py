import os, sys
import itertools
import time
from modules.fromGPOS import *
from fontTools import ttLib

__doc__ ='''\

	This script is capable of extracting a viable features.kern file from a compiled font.
	To be expanded with multiple options; e.g. AFM-export; and export of all possible (exploded) pairs.

	usage: python getKerning font.otf > outputfile

	'''

def askForClass(glyph, classes):
	for singleClass in classes:
		if glyph in singleClass:
			return singleClass
			break

class collectClasses:
	def __init__(self):
		self.pairs = []
		self.count = 0
		
		
def outputFile(path, suffix):
 	return '%s.%s' % (os.path.splitext(fontPath)[0], suffix)


def write2file(path, list):
	o = open(path, 'w')
	o.write('\n'.join(list))
	o.close()


def main(fontPath):
	singlePairsList = getSinglePairs(fontPath)

	leftKeyGlyphs = []
	rightKeyGlyphs = []
	finalLeftClasses = []
	finalRightClasses = []
	

	def makeGlyphValueDict(flag):
		" Creating dictionaries filled with dictionaries, for all the and right and left glyphs that are in a flat kerning pair. "
		" Those are containers used in the next loop. "
		
		glyphsDict = {}
	 	
		for left, right, value in singlePairsList:
			 # the same function can be used for right-left kerning pairs; for the sake of simplicity; the variables are just flipped.
			if flag == 'right':
				left, right = right, left
			if not left in glyphsDict:
				glyphsDict[left] = {}

			""" 
			Filling dicts created above; creating a list of glyphs that are kerned to their kern partner _value_.
			This creates dictionaries like this:
	
			q:	{
				-61: ['quoteright.latn', 'quoteright.latn', 'quotedblright.latn'], 
				-57: ['quoteleft.latn', 'quoteleft.latn', 'quotedblleft.latn'],
				}

			Same is happening for the right side; where the kerning needs to be imagined in reverse (right glyph to left glyph: value).
			"""

		for left, right, value in singlePairsList:
			if flag == 'right':
				left, right = right, left
				
			if not value in glyphsDict[left]:
				glyphsDict[left][value] = []
				glyphsDict[left][value].append(right)
			else:
				if not left in glyphsDict[left][value]:
					glyphsDict[left][value].append(right)

		return glyphsDict
		
		
	leftGlyphsDict = makeGlyphValueDict('left')
	rightGlyphsDict = makeGlyphValueDict('right')

	def reduceClasses(flag):
		" Sorting aforementioned lists of glyphs; adding them to a list that contains all the right/left classes found via above method. "
		" This will not be the final list of classes, just all possible ones. "
		
		if flag == 'right':
			glyphsDict = leftGlyphsDict
		if flag == 'left':
			glyphsDict = rightGlyphsDict

		allClasses = []
		potentialClasses = []

		for glyph in glyphsDict:
			for kernValue in glyphsDict[glyph]:
				kernClass = sortGlyphs(glyphsDict[glyph][kernValue])
				allClasses.append(kernClass)

		" Counting occurrence and length of those classes; throwing out the ones that have length == 1 or occur only once. "

		for c in allClasses:
			occurrence = allClasses.count(c)
			
			# the occurrence value could be higher; probably this would increase accuracy in the end.
			if occurrence > 3 and len(c) > 1:
			 	if (occurrence, c) not in potentialClasses:
			 		potentialClasses.append((occurrence, c))


		" Sorting the potential right and left classes by occurrence; so we can parse them by importance. "
		potentialClasses.sort()
		potentialClasses.reverse()
		# print flag
		# for i in potentialClasses:
		# 	print i
		# print
		return potentialClasses

	potentialRightClasses = reduceClasses('right')
	potentialLeftClasses = reduceClasses('left')

	print potentialLeftClasses

	def makeFinalClasses(potentialClasses):
		""" 
		The potential classes are sorted by occurrence.
		In this function, we parse the list of classes over and over again, removing the higher-ranked class
		from all the remaining classes below, to come up with classes that have the highest probability. 
		"""
		finalClasses = []
		for i in potentialClasses:
			classIndex = potentialClasses.index(i)
			glyphs = i[1]

			for k in potentialClasses[classIndex:]:
				targetIndex = potentialClasses.index(k)
				otherglyphs = k[1]
				k = (k[0], list(set(otherglyphs) - set(glyphs)))
				potentialClasses[targetIndex] = k

			if len( glyphs ) > 1:
				finalClasses.append(glyphs)
		return finalClasses
		
	finalRightClasses = makeFinalClasses(potentialRightClasses)
	finalLeftClasses = makeFinalClasses(potentialLeftClasses)
	
	print
	for i in finalLeftClasses:
		print '/%s' % ' /'.join(i)
#		for i in range(potentialRightClasses.index(i),len(potentialRightClasses)):
			

		# print list(set(a) & set(b))
		# print glyphs
		# print list(set(glyphs) & set(glyphs))
		# print
		
		# if not keyGlyph in leftKeyGlyphs:
		# 	leftKeyGlyphs.append(keyGlyph)


	# " Creating lists of keyGlyphs. The glyphs have been sorted with sortGlyphs() before, which leaves important glyphs at the first position in the list. "
	# " Like that, similar classes are flagged, and can later be compared to find out which classes have an intersection. "
	# 
	# # This is the weak point! Find better compare flag!!
	# 
	# for i in potentialRightClasses:
	# 	keyGlyph = i[1][0]
	# 	print keyGlyph
	# 	if not keyGlyph in leftKeyGlyphs:
	# 		leftKeyGlyphs.append(keyGlyph)
	# 
	# for i in potentialLeftClasses:
	# 	keyGlyph = i[1][0]
	# 	if not keyGlyph in rightKeyGlyphs:
	# 		rightKeyGlyphs.append(keyGlyph)
	# 
	# 
	# " Taking out the occurrence information. This ranking is now stored in the order of keyGlyphs. "
	# 
	# potentialRightClasses = sorted([i[1] for i in potentialRightClasses])
	# potentialLeftClasses = sorted([i[1] for i in potentialLeftClasses])
	# 
	# 
	# 
	# " Going through the keyglyphs, which are sorted by occurrence. Building classes. "
	# 
	# allRightGlyphsInClass = []
	# for keyGlyph in leftKeyGlyphs:
	# 	l = []
	# 	for i in potentialRightClasses:
	# 		if i[0] == keyGlyph:
	# 			l.append(i)
	# 	for i in range(len(l)):
	# 		if len(l) > 1:
	# 			baseSet = set(l[0])
	# 		 	final = list(baseSet.intersection(l[i]))
	# 		else:
	# 			final = l[i]
	# 	final = sortGlyphs(final)
	# 
	# 	" Going through the class, removing glyphs that have already previously been assigned to another class. "
	# 	" This happens in reverse order, as otherwise we run into problems during removal. " 
	# 
	# 	for glyph in final[::-1]:
	# 		if len(final) > 1:
	# 			if not glyph in allRightGlyphsInClass:
	# 				allRightGlyphsInClass.append(glyph)
	# 			else:
	# 				final.remove(glyph)
	# 	
	# 	if len(final) == 1:
	# 		continue
	# 	else:
	# 		finalRightClasses.append(final)
	# 
	# 
	# " Same for the other side. "
	# 
	# allLeftGlyphsInClass = []
	# for keyGlyph in rightKeyGlyphs:
	# 	l = []
	# 	for i in potentialLeftClasses:
	# 		if i[0] == keyGlyph:
	# 			l.append(i)
	# 			
	# 	for i in range(len(l)):
	# 		if len(l) > 1:
	# 			baseSet = set(l[0])
	# 		 	final = list(baseSet.intersection(l[i]))
	# 		else:
	# 			final = l[i]
	# 
	# 	final = sortGlyphs(final)
	# 		
	# 
	# 	" Step 2 for the other side. "
	# 
	# 	for glyph in final[::-1]:
	# 		if len(final) > 1:
	# 			if not glyph in allLeftGlyphsInClass:
	# 				allLeftGlyphsInClass.append(glyph)
	# 			else:
	# 				final.remove(glyph)
	# 	
	# 	if len(final) == 1:
	# 		continue
	# 	else:
	# 		finalLeftClasses.append(final)
	# 
	# 
	# # finalRightClasses = buildFinalClasses('right')
	# # finalLeftClasses = buildFinalClasses('left')
	# 
	# explodedClasses = []
	# for leftClass, rightClass in list(itertools.product(finalLeftClasses, finalRightClasses)):
	# 	explodedClasses.extend(list(itertools.product(leftClass, rightClass)))
	# 	
	# 
	# " In some cases, glyphs are not consistenly kerned, although the classing in other cases might suggest so. "
	# " Therefore, we here analyze the kerning classes created, and sort them by occurrence. "
	# " If the same kerning class pair exists twice or more with different kerning values, the pair that has the highest occurrence is preferred. "
	# 
	# classKerning = []
	# classKerningExport = []
	# classKerningStorage = {}
	# for left, right, value in singlePairsList[::-1]:
	# 	if (left, right) in explodedClasses:
	# 		leftClass = nameClass(askForClass(left, finalLeftClasses), '_LEFT')
	# 		rightClass = nameClass(askForClass(right, finalRightClasses), '_RIGHT')
	# 		classKernPair = leftClass, rightClass, value
	# 		
	# 		if not classKernPair in classKerningStorage:
	# 			c = collectClasses()
	# 			c.count = 1
	# 			c.pairs.append((left, right, value))
	# 			classKerningStorage[classKernPair] = c
	# 			
	# 		else:
	# 			classKerningStorage[classKernPair].count += 1
	# 			classKerningStorage[classKernPair].pairs.append((left, right, value))
	# 
	# 		singlePairsList.remove((left, right, value))
	# 
	# 
	# " Creating a ranking of kerning class combinations: "
	# ranking = []
	# for i in classKerningStorage:
	# 	ranking.append((classKerningStorage[i].count, i))
	# 
	# ranking.sort()
	# ranking.reverse()
	# 
	# 
	# " After the sorting; we don't need the count any more, therefore it is stripped. "
	# ranking = [i[1] for i in ranking]
	# 
	# for left, right, value in ranking:
	# 
	# 	if not (left, right) in classKerning: 
	# 		classKerning.append((left, right))
	# 		classKerningExport.append((left, right, value))
	# 	else:
	# 		" Pairs are thrown back into the single pairs list, and will be exceptions from the highest-ranked kerning class. "
	# 		singlePairsList.extend(classKerningStorage[(left, right, value)].pairs)
	# 			
	# " Everything is ready for the output. "
	# output = [ ]
	# 
	# for i in finalLeftClasses:
	# 	output.append( '%s = [ %s ];' % (nameClass(i, '_LEFT'), ' '.join(i)) )
	# output.append('')
	# 
	# for i in finalRightClasses:
	# 	output.append( '%s = [ %s ];' % (nameClass(i, '_RIGHT'), ' '.join(i)) )
	# output.append('')
	# 	
	# 
	# for left, right, value in singlePairsList:
	# 	output.append( 'pos %s %s %s;' % (left, right, value) )
	# output.append('')
	# 
	# for left, right, value in classKerningExport:
	# 	output.append( 'pos %s %s %s;' % (left, right, value) )
	# output.append('')
	# 
	# 
	# outputFileName = outputFile(fontPath, 'kern')
	# write2file(outputFileName, output)
	# 
	# print 'done'


if __name__ == "__main__":
	startTime = time.time()
	
	if len(sys.argv) == 2:
		if os.path.exists(sys.argv[1]):
			fontPath = sys.argv[1]
    		main(fontPath)
	else:
		print "No valid font provided."
	endTime = round(time.time() - startTime, 2)
	print endTime, 'seconds'
	