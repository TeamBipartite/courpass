from course import Course
from prereqtree import PrereqTree
import search_scraper

# unicode superscirpt string versions of the keys
TO_SUPERSCRIPT = {0: '\u2070', 1: '\u00B9', 2: '\u00B2', 3: '\u00B3', 4: '\u2074',
                  5: '\u2075', 6: '\u2076', 7: '\u2077', 8: '\u2078', 9: '\u2079'}
# length of 'Prereq of:'  
MIN_TEXT_GRID_WIDTH = 10

class PrereqGrid:
    # definitions for the course header
    CourseHeader = tuple[Course, bool, bool, int]
    CH_COURSE_OBJ = 0
    CH_ALL_PREREQS_SHOWN = 1
    CH_DEPMT_PERMSN = 2
    CH_MIN_YR_STNDG = 3
    
    # grid data tuple definitions
    GridData = tuple[bool, int]
    GD_IS_PREREQ = 0
    GD_GROUP_NUM = 1

    # group info tuple definitions
    GroupInfo = tuple[int, bool]
    GI_NUM_REQD  = 0
    GI_ALL_SHOWN = 1

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
        self.__groups = {}

        for course in self.__target_courses:
            cur_course_reqs  = [None for idx in range(len(self.__query_courses))]

            if __debug__: print("COURSE %r" % (course))
            _, _, cur_course_notes= self.__parse_prereq_tree(cur_course_reqs, course.prereqs(), \
                                                             course_header = [course, True, False, 0])
            self.__grid.append(cur_course_reqs)
            self.__header_row.append(tuple(cur_course_notes))

        self.__group_to_num = {}
        self.__groups_list = [(PrereqTree.ALL, True)]
        group_num = 1
        for group in self.__groups.keys():
            if group.get_num_reqd() != PrereqTree.ALL:
                self.__group_to_num[group] = group_num
                self.__groups_list.append( (group.get_num_reqd(), self.__groups[group]) )
                group_num += 1

    def __parse_prereq_tree(self, course_reqs: list[PrereqTree], req_tree: PrereqTree,
                            parent_group: PrereqTree = PrereqTree(num_reqd = PrereqTree.ALL),
                            course_to_idx: dict[Course, int] = None, 
                            course_header: list = [None, True, False, 0]):
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
        if not course_to_idx:
            course_to_idx = {course: idx for (idx, course) in enumerate(self.__query_courses)}
            if __debug__: print("INITALIZING COURSE_TO_IDX: %s" % (course_to_idx))

        found_course_in_query = found_course_not_in_query = found_in_query_below \
                              = found_notin_below = False

        for sub_tree in req_tree:
            if __debug__: print("SEARCHING %r" % (sub_tree))
            tree_type = sub_tree.get_type()

            if tree_type == PrereqTree.DEPMT_PERMSN:
                course_header[type(self).CH_DEPMT_PERMSN] = True
            elif tree_type == PrereqTree.MIN_YR_STNDG:
                course_header[type(self).CH_MIN_YR_STNDG] = sub_tree.get_min_grade()
            elif tree_type == PrereqTree.SINGLE_COURSE:
                req = sub_tree.get_reqs_list()
                if req in self.__query_courses:
                    found_course_in_query = True
                    course_reqs[course_to_idx[req]] = parent_group
                elif parent_group and parent_group.get_num_reqd() != PrereqTree.ALL:
                    found_course_not_in_query = True
                # this is if req is a course not in query_courses and we are in
                # the root group
                else:
                    course_header[type(self).CH_ALL_PREREQS_SHOWN] = False
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

    @staticmethod
    def to_superscript(num) -> str:
        '''
        return the superscript string representation of the given integer num.
        - Uses unicode superscript characters.
        '''
        return ''.join([TO_SUPERSCRIPT[int(char)] for char in str(num)])

    def get_query_courses(self) -> list[tuple[Course, bool, bool, int]]:
        '''
        Returns a list of information about the query courses in this query,
        where each course has a tuple with:
            0: Course object
            1: bool - True if all prerqs for this course are in the prereq_courses,
                      False otherwise
            2: bool - True if prereqs can be overidden with permission from the 
                      department, False otherwise
            3: int - minimum year standing required to take the course
        '''
        return self.__header_row

    def get_prereq_courses(self) -> list[Course]:
        '''
        Returns the list of prereq courses in this query
        (without prereq information populated)
        '''
        return self.__query_courses

    def get_grid_data(self) -> list[list[tuple[bool, int]]]:
        '''
        Returns the data of the body of the grid, as a 2D-list, with the query
        courses on the x-axis and the prereq courses on the y-axis, indexed from
        the top-left corner. Each position (y, x) contains a tuple with:
            0: bool - True if course y is a prereq of course x, False otherwise
            1: int  - The group number assoated with x's prereq of y. 
                      0 indicates 'always required', and > 0 links to a group which
                      info about it can be obtained with get_grid_info
        '''
        results = []

        for row, course in enumerate(self.__query_courses):
            cur_row = []
            for col in range(len(self.__target_courses)):
                cur_col = [False, 0]
                if self.__grid[col][row]:
                    cur_col[type(self).GD_IS_PREREQ] = True
                    if self.__grid[col][row].get_num_reqd() != PrereqTree.ALL:
                       cur_col[type(self).GD_GROUP_NUM] = self.__group_to_num[self.__grid[col][row]]
                cur_row.append(tuple(cur_col))
            results.append(cur_row)

        return results

    def get_group_info(self) -> list[tuple[int, bool]]:
        '''
        Returns a list representing the groups found in this query. Each index i
        contains information about group i, in a tuple with:
            0: int - number of courses required from this group
            1: bool - True if all courses in this group are in the prereq courses,
                      False otherwise
        '''
        return self.__groups_list

    def text_grid(self, width: int = 10) -> str:
        '''
        Return a human-readable, graphical string representation of this PrereqGrid,
        with the column width specified by width. The default value should be 
        acceptable for all but exeptionally long course titles with exepectionally
        many header notes, but a narrorwer width may be preferred if all coursecodes
        are short/there are few header notes.
        '''
        left_col_width = width if width > MIN_TEXT_GRID_WIDTH else MIN_TEXT_GRID_WIDTH

        result = "Prereq of:".rjust(left_col_width)
        for idx,course in enumerate(self.__target_courses):
            cur_header_info = self.__header_row[idx]
            cur_header_str  = ''
            if not cur_header_info[type(self).CH_ALL_PREREQS_SHOWN]:
                cur_header_str += '*'
            if cur_header_info[type(self).CH_DEPMT_PERMSN]:
                cur_header_str += '+'
            if cur_header_info[type(self).CH_MIN_YR_STNDG]:
                cur_header_str += self.to_superscript(cur_header_info[type(self).CH_MIN_YR_STNDG])
            result += (course.get_coursecode() + cur_header_str).center(width)

        result += "\n"
        for row, course in enumerate(self.__query_courses):
            result += course.get_coursecode().rjust(left_col_width)
            for col in range(len(self.__target_courses)):
                if not self.__grid[col][row]:
                    result += '✗'.center(width)
                elif self.__grid[col][row].get_num_reqd() != PrereqTree.ALL:
                    result += ('✓'+ self.to_superscript(self.__group_to_num[self.__grid[col][row]])).center(width)
                else:
                    result += '✓'.center(width)
            result += "\n" 

        if any(self.__header_row):
            result += "-----------\nHeader legend:\n"
        if any([header[type(self).CH_MIN_YR_STNDG] > 0 for header in self.__header_row]):
            result += (self.to_superscript("2345") + ":").rjust(width) \
                      + " Minimum year standing required.\n"
        if any([not header[type(self).CH_ALL_PREREQS_SHOWN] for header in self.__header_row]):
            result += "*:".rjust(width) + " Not all prereqs shown. See calendar for details.\n"
        if any([header[type(self).CH_DEPMT_PERMSN] for header in self.__header_row]):
            result += "+:".rjust(width) + " Or department permission.\n"

        result += '-----------\nGrid legend:\n' if len(self.__groups_list) > 1 else ''
        for group_idx, group_info in enumerate(self.__groups_list[1:]):
            # adjust for no group 0 in the legend
            group_num = group_idx+1
            group_num_reqd, group_all_shown = group_info
            result += ('Group %d:' % (group_num)).rjust(width) + \
                      ' Any %d of these.' % (group_num_reqd) 
            # FIXME: reenable later after discusing interface          
            #if group_min_grade:
            #    result += ' Minimum grade of %s required.' % (group_min_grade)
            if not group_all_shown:
                result += ' Not all courses in this group shown. See calendar for details.'
            result += '\n'

        return result.rstrip('\n')
