#!/usr/bin env python3

from prereqgrid import PrereqGrid
import sys

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("usage: %s <list of courses to search through> <list of prereqs to search for> [-d]" % (sys.argv[0]))
        sys.exit(1)

    if len(sys.argv) > 3 and '-d' in sys.argv[3]: DEBUG = True
    
    targets = sys.argv[1].split(',')
    prereqs = sys.argv[2].split(',')
    grid = PrereqGrid(targets, prereqs)
    print(grid)

