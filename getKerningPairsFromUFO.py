#!/usr/bin/python
# coding: utf-8
import sys
import os
import itertools


class UFOkernReader(object):

    def __init__(self, font):
        self.f = font
        self.classKerningPairs = {}
        self.singleKerningPairs = {}

        self.allKerningPairs = self.makePairDicts()
        self.output = []

        for (left, right), value in self.allKerningPairs.items():
            self.output.append('/%s /%s %s' % (left, right, value))
        self.output.sort()

        self.totalKerning = sum(self.allKerningPairs.values())
        self.absoluteKerning = sum([abs(value) for value in self.allKerningPairs.values()])


    def allCombinations(self, left, right):
        leftGlyphs = self.f.groups.get(left, [left])
        rightGlyphs = self.f.groups.get(right, [right])
        combinations = list(itertools.product(leftGlyphs, rightGlyphs))
        return combinations


    def makePairDicts(self):
        kerningPairs = {}

        for (left, right), value in self.f.kerning.items():

            if not '@' in left and not '@' in right:
                self.singleKerningPairs[(left, right)] = value

            else:
                for combo in self.allCombinations(left, right):
                    self.classKerningPairs[combo] = value

        kerningPairs.update(self.classKerningPairs)
        kerningPairs.update(self.singleKerningPairs) # overwrites any given class kern values with exceptions.


        # delete any kerning values == 0. 
        # This cannot be done in the loop, since exceptions might undo a previously set kerning pair to be 0.

        cleanKerningPairs = dict(kerningPairs)
        for pair in kerningPairs:
            if kerningPairs[pair] == 0:
                del cleanKerningPairs[pair]

        return cleanKerningPairs



def run(font):
    ukr = UFOkernReader(font)
    scrap = os.popen('pbcopy', 'w')
    output = '\n'.join(ukr.output)
    scrap.write(output)
    scrap.close()

    if inRF:
        pass        
        # print 'Total length of kerning:', ukr.totalKerning

    if inCL:
        print '\n'.join(ukr.output), '\n'

    print 'Total amount of kerning pairs:', len(ukr.output)
    print 'List of kerning pairs copied to clipboard.'


if __name__ == '__main__':
    inRF = False
    inCL = False

    try: 
        import mojo
        inRF = True
        f = CurrentFont()
        if f:
            run(f)
        else:
            print u'You need to open a font first. \U0001F625'

    except ImportError:
        try:
            import defcon
            inCL = True
            path = sys.argv[-1].rstrip(os.sep)
            if os.path.splitext(path)[-1] in ['.ufo', '.UFO']:
                f = defcon.Font(path)
                run(f)
            else:
                print 'No UFO file given.'
        except ImportError:
            print u'You don’t have Defcon installed. \U0001F625'



