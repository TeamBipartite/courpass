from course import Course


class PrereqTree:
    
    # Constants for num_reqd field
    ALL           =  0 # All subtrees in reqs_list
    SINGLE_COURSE = -1 # Reqs list is a single course and not a PrereqTree, (ie,
                       # leaf of the tree
    DEPMT_PERMSN  = -2 # 'permission from the deparment' option. Empty reqs_list
    AWR           = -3 # Academic Writing Requirement. Empty reqs_list
    MIN_YR_STNDG  = -4 # Minimum year standing required. Year specified as an int
                       # by min_grade field

    NUM_REQD_TO_TYPE = {0: 'PrereqTree.ALL', -1: 'PrereqTree.SINGLE_COURSE', 
                        -2: 'PrereqTree.DEPMT_PERMSN', -3: 'PrereqTree.AWR',
                        -4: 'PrereqTree.MIN_YR_STNDG'}

    def __init__(self, num_reqd: int, 
                       reqs_list: any([list[Course], Course]) = [],
                       min_grade: str = None, notes: str = None):
        self.__num_reqd  = num_reqd
        self.__reqs_list = reqs_list
        self.__min_grade = min_grade
        self.__notes     = notes

    def __repr__(self):
        num_reqd_type = self.__class__.NUM_REQD_TO_TYPE[self.__num_reqd] if self.__num_reqd in self.__class__.NUM_REQD_TO_TYPE else self.__num_reqd
        return 'PrereqTree(%s, %r, %r, %r)' % (self.__num_reqd, self.__reqs_list,
                                               self.__min_grade, self.__notes)

    def __eq__(self, other):
        return self.__num_reqd == other.__num_reqd and \
               self.__reqs_list == other.__reqs_list and \
               self.__min_grade == other.__min_grade and \
               self.__notes == other.__notes

    def get_num_reqd(self):
        return self.__num_reqd

    def get_reqs_list(self):
        return self.__reqs_list

    def get_min_grade(self):
        return self.__min_grade
        
    def get_notes(self):
        return self.__notes
