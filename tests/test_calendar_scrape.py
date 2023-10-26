#! /bin/env python3

import pytest
import calendar_scrape
from course import Course
from prereqtree import PrereqTree

class TestCalendarScrape:


    CSC115_COURSE  = Course('CSC', '115', 'Fundamentals of Programming II', None, None,
                            'https://www.uvic.ca/calendar/undergrad/index.php#/courses/view/5cbdf4e567a5c324003b0bb6' )
    CSC116_COURSE  = Course('CSC', '116', 'Fundamentals of Programming II with Engineering Applications', None, None,
                            'https://www.uvic.ca/calendar/undergrad/index.php#/courses/view/5cbdf4e667a5c324003b0bb9')
    CSC225_COURSE  = Course('CSC', '225', 'Algorithms and Data Structures I', None, None, 
                            'https://www.uvic.ca/calendar/undergrad/index.php#/courses/view/5cbdf4ea67a5c324003b0bbd')
    CSC226_COURSE  = Course('CSC', '226', 'Algorithms and Data Structures II', None, None, 
                            'https://www.uvic.ca/calendar/undergrad/index.php#/courses/view/6307b1bdfe51a12031b36bfa')
    CSC230_COURSE  = Course('CSC', '230', 'Introduction to Computer Architecture', None, None, 
                            'https://www.uvic.ca/calendar/undergrad/index.php#/courses/view/5cbdf4ec67a5c324003b0bc3')
    CENG255_COURSE = Course('CENG', '255', 'Introduction to Computer Architecture', None, None,
                            'https://www.uvic.ca/calendar/undergrad/index.php#/courses/view/5c4feeb019654524003846d1')
    CHEM11_COURSE  = Course('unknown', 'Chemistry 11', '', None, None, '')
    ECE255_COURSE  = Course('ECE', '255', 'Introduction to Computer Architecture', None, None, 
                            'https://www.uvic.ca/calendar/undergrad/index.php#/courses/view/5cbdf57704ce072400155f52')
    GEOG226_COURSE = Course('GEOG', '226', 'Introduction to Quanitative Methods in Geography', None, None, 
                            'https://www.uvic.ca/calendar/undergrad/index.php#/courses/view/6137a4830dbd1d32a146ff78')
    MATH120_COURSE = Course('MATH', '120', 'Precalculus Mathematics', None, None, 
                            'https://www.uvic.ca/calendar/undergrad/index.php#/courses/view/63168d5cbee7272a8be640b9')
    PRECALC12_COURSE=Course('unknown', 'Pre-Calculus 12', '', None, None, '')
    PRNCPLES12_COURSE=Course('unknown', 'Principles of Mathematics 12', '', None, None, '')
    SENG265_COURSE = Course('SENG', '265', 'Software Development Methods', None, None, 
                            'https://www.uvic.ca/calendar/undergrad/index.php#/courses/view/5cbdf65404ce072400156009')
    PSYC300A_COURSE= Course('PSYC', '300A', 'Statistical Methods in Psychology', None, None,
                            'https://www.uvic.ca/calendar/undergrad/index.php#/courses/view/5d8d839e015c5b2400a72992')
    STAT254_COURSE = Course('STAT', '254', 'Probability and Statistics for Engineers', None, None,
                            'https://www.uvic.ca/calendar/undergrad/index.php#/courses/view/5d1f6895fb68f3240022ccec')
    STAT255_COURSE = Course('STAT', '255', 'Statistics for Life Sciences I', None, None,
                            'https://www.uvic.ca/calendar/undergrad/index.php#/courses/view/5e615df5109f5025006793a7')
    STAT260_COURSE = Course('STAT', '260', 'Introduction to Probability and Statistics I', None, None,
                            'https://www.uvic.ca/calendar/undergrad/index.php#/courses/view/5e615e517eb8e0250078b7da')
                            


    def test_both_pre_co_reqs_csc361(self):
        url = "https://www.uvic.ca/calendar/undergrad/index.php#/courses/ryzikO6QN"
        results = calendar_scrape.get_calendar_info(url)

        assert len(results) == 2 and  \
               calendar_scrape.parse_reqs(results[0]) == PrereqTree(1, 
                            [
                             PrereqTree(PrereqTree.ALL,
                               [
                                PrereqTree(PrereqTree.ALL, 
                                 [                                 
                                  PrereqTree(PrereqTree.SINGLE_COURSE, self.__class__.SENG265_COURSE, None, None)
                                 ], None, None
                                ),
                                PrereqTree(1, 
                                 [
                                  PrereqTree(PrereqTree.SINGLE_COURSE, self.__class__.CSC230_COURSE, None, None),
                                  PrereqTree(PrereqTree.SINGLE_COURSE, self.__class__.CENG255_COURSE, None, None),
                                  PrereqTree(PrereqTree.SINGLE_COURSE, self.__class__.ECE255_COURSE, None, None)
                                 ], None, None
                                )
                               ], None, None
                              )
                             ], None, None
                            ) and \
               calendar_scrape.parse_reqs(results[1]) == PrereqTree(1,
                             [
                               PrereqTree(PrereqTree.ALL,
                                [
                                 PrereqTree(PrereqTree.SINGLE_COURSE, self.__class__.CSC226_COURSE, None, None)
                                ], None, None
                               )
                              ], None, None
                             )

    def test_empty_csc105(self):
        url = 'https://www.uvic.ca/calendar/undergrad/index.php#/courses/HJZck_TmV'
        results = calendar_scrape.get_calendar_info(url)

        assert len(results) == 0

    def test_no_coreqs_seng265(self):
        url = "https://www.uvic.ca/calendar/undergrad/index.php#/courses/r1l00yY67E?q=SENG265&&limit=20&skip=0&bc=true&bcCurrent=&bcCurrent=Software%20Development%20Methods&bcItemType=courses"

        results = calendar_scrape.get_calendar_info(url)
        assert len(results) == 1 and \
               calendar_scrape.parse_reqs(results[0]) == PrereqTree(1,
                              [
                               PrereqTree(1, 
                                [
                                 PrereqTree(PrereqTree.SINGLE_COURSE, self.__class__.CSC115_COURSE, None, None),
                                 PrereqTree(PrereqTree.SINGLE_COURSE, self.__class__.CSC116_COURSE, None, None)
                                ], None, None
                               )
                              ], None, None 
                             )

    def test_many_prereqs_chem101(self):
        url = 'https://www.uvic.ca/calendar/undergrad/index.php#/courses/r1e06RP6XN'
        results = calendar_scrape.get_calendar_info(url)

        assert len(results) == 1 and \
               calendar_scrape.parse_reqs(results[0])== PrereqTree(1,
                             [
                              PrereqTree(PrereqTree.ALL,
                               [
                                PrereqTree(PrereqTree.SINGLE_COURSE, self.__class__.CHEM11_COURSE, None, None),
                                PrereqTree(1,
                                 [
                                  PrereqTree(PrereqTree.ALL,
                                   [
                                    PrereqTree(PrereqTree.SINGLE_COURSE, self.__class__.MATH120_COURSE, None, None)
                                   ], None, None
                                  ),
                                  PrereqTree(PrereqTree.SINGLE_COURSE, self.__class__.PRECALC12_COURSE, None, None),
                                  PrereqTree(PrereqTree.SINGLE_COURSE, self.__class__.PRNCPLES12_COURSE, None, None)
                                 ], None, None
                                )
                               ], None, None
                              ),
                              PrereqTree(PrereqTree.DEPMT_PERMSN, [], None, None)
                             ], None, None
                            )


    def test_many_coreqs_csc226(self):
        url = 'https://www.uvic.ca/calendar/undergrad/index.php#/courses/HytcJuaQV'
        results = calendar_scrape.get_calendar_info(url)

        assert len(results) == 2 and \
               calendar_scrape.parse_reqs(results[0]) == PrereqTree(1,
                              [
                               PrereqTree(PrereqTree.ALL,
                                [
                                 PrereqTree(PrereqTree.SINGLE_COURSE, self.__class__.CSC225_COURSE, None, None)
                                ], None, None
                               )
                              ], None, None
                             ) and \
                calendar_scrape.parse_reqs(results[1]) == PrereqTree(1, 
                               [
                                PrereqTree(1,
                                 [
                                  PrereqTree(PrereqTree.SINGLE_COURSE, self.__class__.GEOG226_COURSE, None, None),
                                  PrereqTree(PrereqTree.SINGLE_COURSE, self.__class__.PSYC300A_COURSE, None, None),
                                  PrereqTree(PrereqTree.SINGLE_COURSE, self.__class__.STAT254_COURSE, None, None),
                                  PrereqTree(PrereqTree.SINGLE_COURSE, self.__class__.STAT255_COURSE, None, None),
                                  PrereqTree(PrereqTree.SINGLE_COURSE, self.__class__.STAT260_COURSE, None, None)
                                 ], None, None
                                )
                               ], None, None
                              )

    def test_min_grade_reqs_math100(self):
        url = 'https://www.uvic.ca/calendar/undergrad/index.php#/courses/ByxQ12d6QE'
        results = calendar_scrape.get_calendar_info(url)

        assert len(results) == 1 and \
               calendar_scrape.parse_reqs(results[0]) == PrereqTree(1,
                              [
                               PrereqTree(1, 
                                [
                                 PrereqTree(PrereqTree.ALL, 
                                  [
                                   PrereqTree(PrereqTree.SINGLE_COURSE, self.__class__.MATH120_COURSE, None, None)
                                  ], 'C+', None
                                 ),
                                 PrereqTree(PrereqTree.SINGLE_COURSE, self.__class__.PRECALC12_COURSE, 'B', None),
                                 PrereqTree(PrereqTree.DEPMT_PERMSN, [], None, None)
                                ], None, None
                               )
                              ], None, None
                             )

    def test_awr_req_atwp305(self):
        url = 'https://www.uvic.ca/calendar/undergrad/index.php#/courses/r1rPrjq_t?q=CSC%20361' 
        results = calendar_scrape.get_calendar_info(url)

        assert len(results) == 1 and \
               calendar_scrape.parse_reqs(results[0]) == PrereqTree(1, 
                              [
                               PrereqTree(PrereqTree.AWR, [], None, None)
                              ], None, None
                             )

    def test_min_yr_req_csc421(self):
        url = 'https://www.uvic.ca/calendar/undergrad/index.php#/courses/HyeHjkO674'
        results = calendar_scrape.get_calendar_info(url)

        assert len(results) == 1 and \
               calendar_scrape.parse_reqs(results[0]) == PrereqTree(1, 
                              [
                               PrereqTree(PrereqTree.ALL,
                                [
                                 PrereqTree(PrereqTree.ALL,
                                  [
                                   PrereqTree(PrereqTree.SINGLE_COURSE, self.__class__.CSC226_COURSE, None, None)
                                  ], None, None
                                 ),
                                 PrereqTree(PrereqTree.MIN_YR_STNDG, [], 4, None)
                                ], None, None
                               )
                              ], None, None
                             )

