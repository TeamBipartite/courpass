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

    # this is just used to create more readable repr output
    NUM_REQD_TO_TYPE = {0: 'PrereqTree.ALL', -1: 'PrereqTree.SINGLE_COURSE', 
                        -2: 'PrereqTree.DEPMT_PERMSN', -3: 'PrereqTree.AWR',
                        -4: 'PrereqTree.MIN_YR_STNDG'}

    def __init__(self, num_reqd: int, 
                       reqs_list: any([list[Course], Course]) = [],
                       min_grade: str = '', is_coreq: bool = False,
                       notes: str = None):
        self.__num_reqd  = num_reqd
        self.__reqs_list = reqs_list
        self.__min_grade = min_grade
        self.__is_coreq  = is_coreq
        self.__notes     = notes

    def __repr__(self):
        num_reqd_type = self.__class__.NUM_REQD_TO_TYPE[self.__num_reqd] if self.__num_reqd in self.__class__.NUM_REQD_TO_TYPE else self.__num_reqd
        return 'PrereqTree(%s, %r, %r, %r)' % (self.__num_reqd, self.__reqs_list,
                                               self.__min_grade, self.__notes)

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.__num_reqd == other.__num_reqd and \
               self.__reqs_list == other.__reqs_list and \
               self.__min_grade == other.__min_grade and \
               self.__notes == other.__notes

    def __iter__(self):
        return iter(self.__reqs_list)

    def __hash__(self):
        # should work because reqs_list cannot be mutated after the object is
        # created
        return hash('%d%s' % (self.__num_reqd, self.__reqs_list))
    
    def get_all_prereq_courses(self):
        # all special cases are less than SINGLE_COURSE, these are not implemented here yet
        if (self.__num_reqd < self.__class__.SINGLE_COURSE):
            return
        if (self.__num_reqd == self.__class__.SINGLE_COURSE):
            yield self.__reqs_list
            return
            
        for course in self.__reqs_list:
            for req in course:
                yield req

    def get_num_reqd(self):
        return self.__num_reqd

    def get_type(self):
        return self.__num_reqd

    def get_reqs_list(self):
        return self.__reqs_list

    def get_min_grade(self):
        return self.__min_grade

    def is_coreq(self):
        return self.__is_coreq
        
    def get_notes(self):
        return self.__notes
