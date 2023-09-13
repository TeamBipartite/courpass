class Course:
    
    def __init__(self, dep: str, num: str, title: str, prereqs: dict,
                       coreqs: dict, cal_link: str) -> 'Course':
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
