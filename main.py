#!/usr/bin env python3

from utils.prereqgrid.prereqgrid import PrereqGrid
import sys
import pprint

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: %s <list of courses to search through> <list of prereqs to search for> OR" \
                    " %s <saved query filename>" % (sys.argv[0], sys.argv[0]))
        sys.exit(1)

    if len(sys.argv) > 2:
        targets = sys.argv[1].split(',')
        prereqs = sys.argv[2].split(',')
        grid = PrereqGrid(targets, prereqs)
    else:
        grid = PrereqGrid(sys.argv[1])

    print(grid)
    if __debug__:
        print("---\nDEBUG: GRID DATA\n---")
        print(grid.get_query_courses())
        print(grid.get_prereq_courses())
        pprint.pprint(grid.get_grid_data())
        pprint.pprint(grid.get_group_info())
