import os, sys
import time
from modules.fromGPOS import *
import operator
from defcon import Font

	
def outputFile(path, suffix):
 	return '%s.%s' % (os.path.splitext(fontPath)[0], suffix)


def write2file(path, list):
	o = open(path, 'w')
	o.write('\n'.join(list))
	o.close()

def makeMMK(name, side):
	if name[0] == '@' and name[0:3] != '@MMK':
		name = '@MMK_%s_%s' % (side[0], name[1:])
	return name
	
	
def stripClasses(ufo):
	f = Font(ufo)
	for name, group in f.groups.items()[::-1]:
		if len(group) == 0:
			del f.groups[name]
	f.save()

def madLib(ufo, orderFile):
	f = Font(ufo)
	enc = readFile(orderFile)
	print enc.split()
	f.lib['public.glyphOrder'] = enc.split()
	f.save()

def renameGlyphs(ufo):
	proportional = 'guOne.pnum guSix.pnum guTwo.pnum guSeven.pnum guEight.pnum guZero.pnum guNine.pnum guFour.pnum guThree.pnum guFive.pnum'.split()
	tabular = 'guOne guSix guTwo guSeven guEight guZero guNine guFour guThree guFive'.split()
	swapdict = dict(zip(tabular, proportional))
	f = Font(ufo)
	for (left, right), value in f.kerning.items():
		if left in swapdict:
			del f.kerning[left,right]
			left = swapdict[left]
			f.kerning[left,right] = value
		if right in swapdict:
			del f.kerning[left,right]
			right = swapdict[right]
			f.kerning[left,right] = value
		else:
			continue

def makePairlist(ufo):
	pairlist = ['#KPL:P: noName']
	f = Font(ufo)
	for left, right in f.kerning.keys():
		if left in f.groups: 
		 	l = f.groups[left][0]
		else:
			l = left
		if right in f.groups:
			r = f.groups[right][0]
		else:
			r = right
		pairlist.append('%s %s' % (l,r))
	return pairlist
# 	for left, right in f.kerning.keys():
# 		if left in swapdict:
# 			print left, right, '->',
# 			left = swapdict[left]
# 			print left, right
# 			print
# 		if right in swapdict:
# 			print left, right, '->',
# 			right = swapdict[right]
# 			print left, right
# 			print
	print 'done'
#	f.save()

if __name__ == "__main__":
	startTime = time.time()
	# option = sys.argv[1]
	ufo = sys.argv[-1]
 	orderFile = sys.argv[1]
# 	madLib(ufo, orderFile)
	desktop = os.path.expanduser('~/Desktop')
	write2file(os.sep.join((desktop, 'pL.txt')), makePairlist(ufo))
# 	filePath = sys.argv[1]
# 	classes = readKerningClasses(filePath)
# 	pairs = readKerningPairs(filePath)
# 	renameGlyphs(ufo)
	endTime = round(time.time() - startTime, 2)
	print '%s seconds.' % endTime
	# 
# 	replaceKerning(ufo, classes, pairs)
	