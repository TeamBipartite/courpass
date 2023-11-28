from course import Course
from prereqtree import PrereqTree
import search_scraper

TO_SUPERSCRIPT = {0: '\u2070', 1: '\u00B9', 2: '\u00B2', 3: '\u00B3', 4: '\u2074',
                  5: '\u2075', 6: '\u2076', 7: '\u2077', 8: '\u2078', 9: '\u2079'}

class PrereqGrid:
   
    def __init__(self, target_coursecodes: list[str], prereqs_to_search: list[str]):
        #         calendar_server: str = DEFAULT):
        self.__target_courses = search_scraper.get_course_objs(target_coursecodes)
        search_scraper.populate_reqs(self.__target_courses)

        self.__query_courses = search_scraper.get_course_objs(prereqs_to_search)

        self.__assemble_prereq_grid()          

    def __str__(self) -> str:
        return self.print_grid()

    def __assemble_prereq_grid(self):
        '''
        Given a list of Course objects to search and a list of Course objects
        representing prereqs to search for, return the corresponding prereqGrid.
        Note that the Course objects in the given self.__query_courses must have their
        pre/coreqs populated, but this is not necessary for the self.__query_courses.
        '''
        # for faster searching through these courses
        # add +1 to key to mind the header column in the cur_course_reqs lists
        course_to_idx = {course: idx for (idx, course) in enumerate(self.__query_courses)}
        if __debug__: print("INITALIZING COURSE_TO_IDX: %s" % (course_to_idx))

        self.__grid = []
        self.__header_row = []
        # group 0 always reserved for courses which are not part of any group
        self.__groups = {'ROOT': True}
        self.__num_groups = 0

        for course in self.__target_courses:
            # again, +1 to account for the header column
            cur_course_reqs  = [None for idx in range(len(self.__query_courses))]
            cur_course_notes = ''
            #if .get_num_reqd() == PrereqTree.MIN_YR_STNDG:
            #    cur_course_reqs[0] += req.get_num_reqd()

            if __debug__: print("COURSE %r" % (course))
            cur_course_notes += self.__parse_prereq_tree(cur_course_reqs, course.prereqs(), course_to_idx=course_to_idx)
            #for req_tree in course.prereqs():
                #cur_course_notes += self.__parse_prereq_tree(cur_course_reqs, req_tree, course_to_idx=course_to_idx)
            '''
            if __debug__: print("SEARCHING %r" % (req))

            if req in self.__query_courses:
                cur_course_reqs[course_to_idx[req]] = True
            else:
                cur_course_notes = '*'
            '''
            self.__grid.append(cur_course_reqs)
            self.__header_row.append(cur_course_notes)

    def __parse_prereq_tree(self, course_reqs, req_tree, parent_group = 'ROOT', course_to_idx = None, course_header = ''):
        '''
        '''
        #course_header = ''
        if course_to_idx == None:
            course_to_idx = {course: idx for (idx, course) in enumerate(self.__query_courses)}
            if __debug__: print("INITALIZING COURSE_TO_IDX: %s" % (course_to_idx))

        for sub_tree in req_tree:
            if __debug__: print("SEARCHING %r" % (sub_tree))
            tree_type = sub_tree.get_type()

            if tree_type == PrereqTree.DEPMT_PERMSN:
                course_header += '+'
            elif tree_type == PrereqTree.MIN_YR_STNDG:
                course_header += TO_SUPERSCRIPT[sub_tree.get_min_grade()]
            elif tree_type == PrereqTree.SINGLE_COURSE:
                req = sub_tree.get_reqs_list()
                if req in self.__query_courses:
                    if parent_group not in self.__groups:
                        self.__groups[parent_group] = True
                    course_reqs[course_to_idx[req]] = parent_group
                elif type(parent_group) != str and parent_group in self.__groups:
                    self.__groups[parent_group] = False
                elif '*' not in course_header:
                    course_header += '*'
            elif tree_type >= PrereqTree.ALL:
                course_header = self.__parse_prereq_tree(course_reqs, sub_tree, parent_group=sub_tree if tree_type > PrereqTree.ALL else parent_group, course_to_idx=course_to_idx, course_header=course_header)
                
        return course_header

    def html_grid(self) -> str:
        '''
        Stub function for now
        '''
        return 'This feature is not currently implemented...'


    def print_grid(self, width: int = 10) -> str:
        group_to_num = {group: idx for idx, group in enumerate(self.__groups.keys()) if type(group) != str}
        result = "Prereq of: "
        for idx,course in enumerate(self.__target_courses):
            result += (course.get_coursecode() + self.__header_row[idx]).center(width)

        result += "\n"
        for idx,course in enumerate(self.__query_courses):
            result += ("%" + "%ds" % (width+1)) % (course.get_coursecode())
            for col in range(len(self.__target_courses)):
                if not self.__grid[col][idx]:
                    result += '✗'.center(width)
                elif self.__grid[col][idx] != 'ROOT':
                    result += ('✓'+TO_SUPERSCRIPT[group_to_num[self.__grid[col][idx]]%10]).center(width)
                else:
                    result += '✓'.center(width)
                #result += (('✓'+TO_SUPERSCRIPT[self.__grid[col][idx]%10] if self.__grid[col][idx] != 0 else '✓') if self.__grid[col][idx] else '✗').center(width)
            result += "\n" 

        if any(self.__header_row):
            result += "----------\n"
            result += "*    : has other prereqs not shown, see calendar for details\n"
            result += "+    : Or department permission\n"
            result += "[%s-%s]: Minimum year requried.\n" % (TO_SUPERSCRIPT[1],
                                                           TO_SUPERSCRIPT[5])
        for group in [group for group in self.__groups if type(group) != str]:
            group_num = group_to_num[group]
            group_num_reqd = group.get_num_reqd()
            result += 'Group %d: Any %d of these.' % (group_num, group_num_reqd)
            if not self.__groups[group]:
                result += ' Not all courses in this group shown. See calendar for details.'
            result += '\n'
        return result
