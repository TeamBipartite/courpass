from course import Course
from prereqtree import PrereqTree
import search_scraper

# unicode superscirpt string versions of the keys
TO_SUPERSCRIPT = {0: '\u2070', 1: '\u00B9', 2: '\u00B2', 3: '\u00B3', 4: '\u2074',
                  5: '\u2075', 6: '\u2076', 7: '\u2077', 8: '\u2078', 9: '\u2079'}
# length of '0123456789:'                  
MIN_TEXT_GRID_WIDTH = 11

class PrereqGrid:
   
    def __init__(self, target_coursecodes: list[str], prereqs_to_search: list[str]):
        self.__target_courses = search_scraper.get_course_objs(target_coursecodes)
        search_scraper.populate_reqs(self.__target_courses)

        self.__query_courses = search_scraper.get_course_objs(prereqs_to_search)

        self.__assemble_prereq_grid()          

    def __str__(self) -> str:
        return self.text_grid()

    def __assemble_prereq_grid(self):
        '''
        Given a list of Course objects to search and a list of Course objects
        representing prereqs to search for, return the corresponding prereqGrid.
        Note that the Course objects in the given self.__query_courses must have their
        pre/coreqs populated, but this is not necessary for the self.__query_courses.
        '''
        self.__grid = []
        self.__header_row = []
        # None serves as a group for all manditory prereqs
        self.__groups = {None: True}

        for course in self.__target_courses:
            cur_course_reqs  = [None for idx in range(len(self.__query_courses))]

            if __debug__: print("COURSE %r" % (course))
            _, _, cur_course_notes= self.__parse_prereq_tree(cur_course_reqs, course.prereqs())
            self.__grid.append(cur_course_reqs)
            self.__header_row.append(cur_course_notes)

    def __parse_prereq_tree(self, course_reqs: list[PrereqTree], req_tree: PrereqTree,
                            parent_group: PrereqTree = None, course_to_idx: dict[Course, int] = None, 
                            course_header: str = ''):
        '''
        Parse the information in the given req_tree into the given course_reqs 
        'array' (list), creating and/or adding to this PrereqGrid's groups as 
        necessary.
        Returns: a 3-tuple with
            - found_course_in_query - True if a prereq in this query was found
                                      in req_tree, False otherwise
            - found_notin_query - True if a prereq that is not in this query was
                                  found in req_tree, False otherwise
            - course_header - the given course_header updated with any additional
                              notes discovered while parsing req_tree
        '''
        # for faster searching through these courses
        if course_to_idx == None:
            course_to_idx = {course: idx for (idx, course) in enumerate(self.__query_courses)}
            if __debug__: print("INITALIZING COURSE_TO_IDX: %s" % (course_to_idx))

        found_course_in_query = found_course_not_in_query = found_in_query_below \
                              = found_notin_below = False

        for sub_tree in req_tree:
            if __debug__: print("SEARCHING %r" % (sub_tree))
            tree_type = sub_tree.get_type()

            # TODO: possibility of DEMPT_PERMSN within a non-root group?
            # TODO: cleanup in WEBSCRAPE_0031
            if tree_type == PrereqTree.DEPMT_PERMSN and '+' not in course_header:
                course_header += '+'
            elif tree_type == PrereqTree.MIN_YR_STNDG:
                course_header += TO_SUPERSCRIPT[sub_tree.get_min_grade()]
            elif tree_type == PrereqTree.SINGLE_COURSE:
                req = sub_tree.get_reqs_list()
                if req in self.__query_courses:
                    found_course_in_query = True
                    course_reqs[course_to_idx[req]] = parent_group
                elif parent_group and parent_group in self.__groups:
                    found_course_not_in_query = True
                # this is if req is a course not in query_courses and we are in
                # the root group
                elif '*' not in course_header:
                    course_header += '*'
            elif tree_type >= PrereqTree.ALL:
                next_group = sub_tree if tree_type > PrereqTree.ALL else parent_group 
                found_in_query_below, found_notin_below, course_header = self.__parse_prereq_tree(course_reqs, sub_tree, parent_group=next_group,\
                                                                                                  course_to_idx=course_to_idx, course_header=course_header)
                
        found_course_in_query = any([found_course_in_query, found_in_query_below])
        found_course_not_in_query = any([found_course_not_in_query, found_notin_below])
   
        # this may cause the value in the dictionary to be updated several times
        # though the recursion, but that's okay - the top-level recursion will
        # always be the correct answer and that's set last!
        if found_course_in_query:
            self.__groups[parent_group] = not found_course_not_in_query

        return found_course_in_query, found_course_not_in_query, course_header

    def html_grid(self) -> str:
        '''
        Stub function for now
        '''
        return 'This feature is not currently implemented...'

    @staticmethod
    def to_superscript(num) -> str:
        '''
        return the superscript string representation of the given integer num.
        - Uses unicode superscript characters.
        '''
        return ''.join([TO_SUPERSCRIPT[int(char)] for char in str(num)])


    def text_grid(self, width: int = 10) -> str:
        '''
        Return a human-readable, graphical string representation of this PrereqGrid,
        with the column width specified by width. The default value should be 
        acceptable for all but exeptionally long course titles with exepectionally
        many header notes, but a narrorwer width may be preferred if all coursecodes
        are short/there are few header notes.
        '''
        group_to_num = {group: idx for idx, group in enumerate(self.__groups.keys()) if group}
        left_col_width = width if width > MIN_TEXT_GRID_WIDTH else MIN_TEXT_GRID_WIDTH

        result = "Prereq of:".rjust(left_col_width)
        for idx,course in enumerate(self.__target_courses):
            result += (course.get_coursecode() + self.__header_row[idx]).center(width)

        result += "\n"
        for row, course in enumerate(self.__query_courses):
            result += course.get_coursecode().rjust(left_col_width)
            for col in range(len(self.__target_courses)):
                if not self.__grid[col][row]:
                    result += '✗'.center(width)
                elif self.__grid[col][row]:
                    result += ('✓'+ self.to_superscript(group_to_num[self.__grid[col][row]])).center(width)
                else:
                    result += '✓'.center(width)
            result += "\n" 

        # TODO: cleanup this code in WEBSCRAPE_0031
        if any(self.__header_row):
            result += "-----------\nHeader legend:\n"
            result += "%10s:" % (''.join(TO_SUPERSCRIPT.values())) \
                      + " Minimum year required.\n"
        if any(['*' in header for header in self.__header_row]):
            result += "%10s:" % ('*') + " Not all prereqs shown. See calendar for details.\n"
        if any(['+' in header for header in self.__header_row]):
            result += "%10s:" % ('+') + " Or department permission.\n"

        result += '-----------\nGrid legend:\n' if len(self.__groups.keys()) > 1 else ''
        for group in [group for group in self.__groups if group]:
            group_num       = group_to_num[group]
            group_num_reqd  = group.get_num_reqd()
            group_min_grade = group.get_min_grade()
            result += '%10s:' % ('Group %d' % (group_num)) + ' Any %d of these.' % (group_num_reqd)
            if group_min_grade:
                result += ' Minimum grade of %s required.' % (group_min_grade)
            if not self.__groups[group]:
                result += ' Not all courses in this group shown. See calendar for details.'
            result += '\n'

        return result.rstrip('\n')
