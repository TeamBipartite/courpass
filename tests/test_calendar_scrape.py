#! /bin/env python3

import pytest
import calendar_scrape


class TestCalendarScrape:
    
    def test_both_pre_co_reqs(self):
        url = "https://www.uvic.ca/calendar/undergrad/index.php#/courses/ryzikO6QN?q=CSC%20361&&limit=20&skip=0&bc=true&bcCurrent=&bcCurrent=Computer%20Communications%20and%20Networks&bcItemType=courses"
        results = calendar_scrape.get_calendar_info(url)

        assert results[0] is not None \
               and results[1] is not None

    def test_empty(self):
        url = 'https://www.uvic.ca/calendar/undergrad/index.php#/courses/HJZck_TmV?q=CSC105&&limit=20&skip=0&bc=true&bcCurrent=&bcCurrent=Computers%20and%20Information%20Processing&bcItemType=courseis'

        results = calendar_scrape.get_calendar_info(url)
        assert len(results) == 0

    def test_no_coreqs(self):
        url = "https://www.uvic.ca/calendar/undergrad/index.php#/courses/r1l00yY67E?q=SENG265&&limit=20&skip=0&bc=true&bcCurrent=&bcCurrent=Software%20Development%20Methods&bcItemType=courses"

        results = calendar_scrape.get_calendar_info(url)
        assert len(results) == 1

    def test_many_prereqs(self):
        url = 'https://www.uvic.ca/calendar/undergrad/index.php#/courses/r1e06RP6XN'
        # for testing purposes
        assert False

    def test_many_coreqs(self):
        url = 'https://www.uvic.ca/calendar/undergrad/index.php#/courses/HytcJuaQV?q=CSC%20361&&%20%20%20%20limit=20&skip=0&bc=true&bcCurrent=&bcCurrent=Computer%20Communications%20and%20Networks&bcIt%20%20%20%20emType=courses'

        # for testing purposes
        assert False
