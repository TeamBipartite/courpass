from ..course.course import Course
from ..prereqtree.prereqtree import PrereqTree
from .. import search_scraper
import itertools

# unicode superscript string versions of the keys
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
    GridData = tuple[bool, bool, list[int]]
    GD_IS_PREREQ = 0
    GD_IS_COREQ  = 1
    GD_GROUP_KEY = 2

    # group info tuple definitions
    GroupInfo = tuple[int, bool, str, list['GroupInfo']]
    GI_NUM_REQD  = 0
    GI_ALL_SHOWN = 1
    GI_MIN_GRADE = 2
    GI_SUBGROUPS = 3

    # internal expanded group info to help creating group info tuples
    GroupInfoInternal = tuple[int, bool, str, list[tuple]]
    GI_TARGETS        = 4

    def __init__(self, first_arg: str, prereqs_to_search: str = None):
        '''
        SIMULATED MULTIPLE CONSTURCTORS: if prereqs_to_search is not defined, 
        first_arg is assumed to be a filename with saved target_courses on the 
        first line and query_courses on the second line. Else, if prereqs_to_search
        is defined, then first_arg is assumed to be a (comma-separated) list of
        target_coursecodes.
        '''
        if not prereqs_to_search:
            self.__init_from_file(first_arg)
        else: 
            self.__init_from_coursecodes(first_arg, prereqs_to_search)

    def __init_from_coursecodes(self, target_coursecodes: str, prereqs_to_search: str):
        self.__target_courses = search_scraper.get_course_objs(target_coursecodes)
        search_scraper.populate_reqs(self.__target_courses)

        self.__query_courses = search_scraper.get_course_objs(prereqs_to_search)

        self.__assemble_prereq_grid()

    def __init_from_file(self, fname: str):
        fp = open(fname)
        target_str, query_str = fp.read().strip().split("\n")

        # these prompts are kept in due to risks of blindly using eval()
        confirm = input("TARGET_COURSES: %s. Confirm? " % target_str)
        if confirm.lower() != "y":
            exit()

        self.__target_courses = eval(target_str)

        confirm = input("QUERY_COURSES: %s. Confirm? " % query_str)
        if confirm.lower() != "y":
            exit()

        self.__query_courses = eval(query_str) 
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
        # pre-append the default group 0 for "always required" to the groups list
        self.__groups_list = [(PrereqTree.ALL, True, '', [], [])]

        for idx, course in enumerate(self.__target_courses):
            cur_course_reqs  = [(False, False, []) for req in self.__query_courses]

            if __debug__: print("COURSE %r" % (course))
            cur_course_notes= self.__parse_prereq_tree(idx, course.prereqs_tree(), \
                                                       course_header = [course, True, False, 0])
            self.__grid.append(cur_course_reqs)
            self.__header_row.append(tuple(cur_course_notes))

        # now we have to sort out the nested groups - specifically, sort out
        # where we need to create single-course groups for nested groups
        if __debug__: print("BEFORE AUGMENTING:", self.__groups_list)
        self.__create_singleton_groups(self.__groups_list)

        # we haven't actually filled in the grid at this point, just set up the
        # appripiete targets in the groups, so we need to fil in the group keys
        # in the grid now
        self.__fill_group_nums(self.__groups_list, [])

        # delete temp data from groups list
        self.__cleanup_init_data(self.__groups_list)

    def __cleanup_init_data(self, groups_list: list[GroupInfoInternal]) -> None:
        '''
        removes temporary targets information from the given groups_list,
        recursively, mutating it into a list[GroupInfo] to use for client-facing
        functions
        '''
        for idx, group in enumerate(groups_list):
            groups_list[idx] = tuple(group[:-1])
            self.__cleanup_init_data(group[type(self).GI_SUBGROUPS])

    def __fill_group_nums(self, groups_list: list[GroupInfoInternal], 
                                parent_group_key: list[int]) -> None:
        '''
        Uses the information stored in the GI_TARGETS fields in the groups in
        the given groups_list to fill in this PrereqGrid's grid, with list[int]
        group keys, recursively
        '''
        for idx, group in enumerate(groups_list):
            cur_group_key = parent_group_key + [idx]
            for req, course in group[type(self).GI_TARGETS]:
               # FIXME: hardcoding not prereq for now
               self.__grid[course][req] = (True, False, cur_group_key)
            self.__fill_group_nums(group[type(self).GI_SUBGROUPS], cur_group_key)

    def __create_singleton_groups(self, groups_list: list[GroupInfoInternal]) -> None:
        '''
        In order to accuretely represent groups in the prereqgrid, this function
        creates singleton (single course) groups where nesessary: that is,
        groups for single courses in a group which as both subgroups and
        single courses in it
        '''
        for group in groups_list:
            if group[type(self).GI_SUBGROUPS] and group[type(self).GI_TARGETS]:
                for target in group[type(self).GI_TARGETS]:
                    group[type(self).GI_SUBGROUPS].append( (PrereqTree.ALL, True, '', [], target) )
                group[type(self).GI_TARGETS] = []
            self.__create_singleton_groups(group[type(self).GI_SUBGROUPS])

    def __parse_prereq_tree(self, course: Course, req_tree: PrereqTree,
                            parent_groupinfo: GroupInfo = None,
                            course_to_idx: dict[Course, int] = None, 
                            course_header: list = [None, True, False, 0],
                            group_0: bool = True):
        '''
        Parse the information in the given req_tree into the given course_reqs 
        'array' (list), creating and/or adding to this PrereqGrid's groups as 
        necessary.
        Returns: the given course_header updated with any additional notes 
                 discovered while parsing req_tree
        '''
        # for faster searching through these courses
        if not course_to_idx:
            course_to_idx = {course: idx for (idx, course) in enumerate(self.__query_courses)}
            if __debug__: print("INITALIZING COURSE_TO_IDX: %s" % (course_to_idx))

        found_course_not_in_query = False
        
        cur_tree_groupinfo = [req_tree.get_num_reqd(), True, req_tree.get_min_grade(), \
                              [], []]
        if req_tree.get_num_reqd() > PrereqTree.ALL and len(req_tree.get_reqs_list()) > 1:
            if __debug__: print("%r: SETTING GROUP_0 = False" % req_tree)
            group_0 = False

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
                    req_targets = (course_to_idx[req], course)
                    # this is cleaned up later - at this stage we do not know if
                    # we will find any other nested groups in the group or not.
                    # we assume here that we will not, but we will cleanup later 
                    if group_0:
                        self.__groups_list[0][type(self).GI_TARGETS].append(req_targets) 
                    else:
                        cur_tree_groupinfo[type(self).GI_TARGETS].append(req_targets) 
                elif not group_0:
                    course_header[type(self).CH_ALL_PREREQS_SHOWN] = False
                    found_course_not_in_query = True
                # this is if req is a course not in query_courses and we are in
                # the root group
                else:
                    course_header[type(self).CH_ALL_PREREQS_SHOWN] = False
            elif tree_type >= PrereqTree.ALL:
                len_before = len(cur_tree_groupinfo[type(self).GI_SUBGROUPS])
                course_header = self.__parse_prereq_tree(course, sub_tree, parent_groupinfo=cur_tree_groupinfo,\
                                                                                                  course_to_idx=course_to_idx, course_header=course_header, group_0 = group_0)
                len_after = len(cur_tree_groupinfo[type(self).GI_SUBGROUPS])
                if (len_after == len_before):
                    cur_tree_groupinfo[type(self).GI_ALL_SHOWN] = False
        
        # don't set it back to True if it is already False!
        if cur_tree_groupinfo[type(self).GI_ALL_SHOWN]:
            cur_tree_groupinfo[type(self).GI_ALL_SHOWN] = not found_course_not_in_query
        
        if (cur_tree_groupinfo[type(self).GI_TARGETS] != [] or cur_tree_groupinfo[type(self).GI_SUBGROUPS] != []):
            if parent_groupinfo and not group_0:
                parent_groupinfo[type(self).GI_SUBGROUPS].append(cur_tree_groupinfo)
            elif group_0:
                # if we are adding a non-empty list, group_0 was just set to 0
                # in the children, so put them at the top level here
                self.__groups_list.extend([tuple(subgroup) for subgroup in cur_tree_groupinfo[type(self).GI_SUBGROUPS]])
            # shouldn't happen, but kept for error handing (NOTE may run into this
            # later when adding coreq support...)
            else:
                self.__groups_list.append(cur_tree_groupinfo)

        return course_header

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
        return self.__grid

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
                if not self.__grid[col][row][type(self).GD_IS_PREREQ]:
                    result += '✗'.center(width)
                elif self.__grid[col][row][type(self).GD_GROUP_KEY] != [0]:
                    cur_group_str = "".join([str(val) for val in self.__grid[col][row][type(self).GD_GROUP_KEY]])
                    result += ('✓'+ self.to_superscript(cur_group_str)).center(width)
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

        # chop off index 0 to skip the always-present group 0 that is used for
        # prereqs that are always required
        result += self.__text_grid_legend(self.__groups_list[1:], '', width = width)
        return result.rstrip('\n')

    def __text_grid_legend(self, root_group, parent_level, width = 10, ident = 0):
        '''
        Generate and return a human-redable description of the (potentionally) 
        nested groups in this PrereqGrid. 
        '''
        result = '-----------\nGrid legend:\n' if parent_level == ''  and len(root_group) > 1 else ''
        for group_idx, group_info in enumerate(root_group):
            # adjust for root group 0 being used for always necesary
            group_num = parent_level + '%d' % (group_idx+1)
            group_num_reqd, group_all_shown, group_min_grade, subgroups = group_info
            result += '\t' * ident + ('%s:' % (group_num)).rjust(width) + \
                      (' Any %d of these.' % (group_num_reqd) if group_num_reqd > PrereqTree.ALL else " All of these.")
            if group_min_grade:
                result += ' Minimum grade of %s required.' % (group_min_grade)
            if not group_all_shown:
                result += ' Not all options in this group shown. See calendar for details.'
            result += '\n' + self.__text_grid_legend(subgroups, group_num + ' ', width = width, ident = ident + 1)
        return result
