# don't import prereq tree here...Python does everything at runtime!

class Course:
    
    def __init__(self, dep: str, num: str, title: str, prereqs: 'PrereqTree',
                       coreqs: 'PrereqTree', cal_link: str) -> 'Course':
        '''
        Create a Course object
        '''
        self.__dep = dep
        # num cannot be a str because some courses have lettered variants
        self.__num = num
        self.__title = title
        self.__prereqs = prereqs
        self.__coreqs  = coreqs
        self.__cal_weblink = cal_link

    def __repr__(self) -> str:
        '''
        Return a computer-readable string represention of this Course
        '''
        return 'Course(%r, %r, %r, %r, %r, %r)' % (self.__dep, self.__num, \
                self.__title, self.__prereqs, self.__coreqs, self.__cal_weblink)

    def __eq__(self, other):
        # note checking reqs for now, may change later...
        return self.__dep == other.__dep and \
               self.__num == other.__num 
               # it turns out the calendar weblinks are not unique, so not
               # checking in equality check here..
#               self.__cal_weblink == other.__cal_weblink

    # needed because we use dicts of Courses. I think for now just checking the
    # course code is enough, although we can alter this in future
    def __hash__(self):
        return hash(self.get_coursecode())

    def prereqs(self):
        '''
        returns a generator of the Course's prereqs
        '''
        return iter(self.__prereqs) if self.__prereqs else []

    def coreqs(self):
        '''
        returns a generator of the Course's coreqs
        '''
        return iter(self.__coreqs) if self.__coreqs else []

    def get_coursecode(self):
        if (self.__dep == 'unknown'): return self.__dep

        return ('%s%s' % (self.__dep, self.__num))

    def set_reqs(self, prereqs: 'PrereqTree', coreqs: 'PrereqTree') -> None:
        self.__prereqs = prereqs
        self.__coreqs  = coreqs

    def get_cal_weblink(self) -> str:        
        return self.__cal_weblink
