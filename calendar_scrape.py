#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.common.exceptions import NoSuchDriverException
from selenium.webdriver.remote.webdriver import WebDriver
from bs4 import BeautifulSoup
import pprint
from collections import namedtuple
import re
from course import Course
from prereqtree import PrereqTree

WORD_TO_RANK = {'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5}

WEBDRIVERS  = {webdriver.ChromeOptions: webdriver.Chrome, 
               webdriver.EdgeOptions: webdriver.Edge,
               webdriver.SafariOptions: webdriver.Safari,
               webdriver.FirefoxOptions: webdriver.Firefox}

UVIC_ACADEMIC_CAL_INDEX = 'https://www.uvic.ca/calendar/undergrad/index.php'

def get_calendar_info(url) -> list[str]:
    driver = None

    for driver_options in WEBDRIVERS:
        try:
           options = driver_options()
           # ensure browser opens in backgound
           options.add_argument("--headless=new")
           driver = WEBDRIVERS[driver_options](options = options)
           # if we get here, we found an available driver
           break
        except Exception as e:
            # TODO: may need a better message here (maybe?)
            if type(e) is not NoSuchDriverException:
                print(e)

    if not driver:
        print("Sorry, you do not have a browser that supports this application.")
        print("Please download Chrome (or any Chrome-based browser), Edge, Safari, or Firefox to use this application.")
        return []

    return scrape_calendar_page(driver,  url)

def scrape_calendar_page(driver: WebDriver, url: str) -> list[str]:
    pre_and_coreq_html = []
     # Open browser at the given url
    driver.get(url)
    # Wait (up to) 10 seconds for the browser to load at the url
    driver.implicitly_wait(10)
    # Search for <span> who has a direct child of tag <h3> containing Prerequisites or Pre- or corequisites
    cal_sections = driver.find_elements(By.XPATH, "//span[h3[contains(text(), 'Prerequisites') or contains(text(), 'Pre- or corequisites')]]")

    for section in cal_sections:
        pre_and_coreq_html.append(section.get_attribute("innerHTML"))
    
    return pre_and_coreq_html

def parse_course_link(element) -> str:
    '''
    Given a Tag of an 'a' element which has a link to a UVic academic calendar
    entry (where the link is relative to the academic calendar index), extract
    and return the (absolute) link to the course, as a string
    '''
    if not element: return ''

    # links in the element are in the format '#/courses/view/...'
    return UVIC_ACADEMIC_CAL_INDEX +  element['href']

def split_course_code(code: str) -> (str, str):
    '''
    Splits course codes in forms such as 'CSC110', 'CSC 110 ', or 'CS 110' into
    their respective department and course number components.
    Returns: string with course department, followed by string with course num
    '''
    matches = re.match(r"([A-Za-z]*)\s*(\d\w*)", code)
    return matches.groups('') if matches is not None else ('unknown', code)


def parse_reqs(raw_html: str) -> PrereqTree:
    '''
    Parse raw html representing a Pre/Coreq list from a UVic
    acadmeic calendar webpage, returning a PrereqTree with the data represented
    '''
    parser = BeautifulSoup(raw_html, 'html.parser')

    # grab all topmost li elements, even if they are nested within divs, etc
    list_tree = parser.find('ul')
    roots = [child_tag.find('li') if child_tag.name != 'li' else child_tag for child_tag in list_tree.contents] if list_tree else []

    # always 'complete one of' for the top-level items?
    return PrereqTree(1, [parse_reqs_rec(root) for root in roots], None, None)

def parse_reqs_rec(reqs_tree: BeautifulSoup) -> PrereqTree:
    '''
    Given a BeautifulSoup tag to the li element representing the root of a UVic
    pre/coreq tree, parse the tree and return a PrereqTree with the data
    represented
    '''
    # needs to be saved to its own variable as we may call next() on it again
    title_strings = reqs_tree.strings
    req_title = next(title_strings)
    min_grade = None
    notes     = None

    # special cases that do not follow any other format
    if req_title == 'or permission of the department.': 
        return PrereqTree(PreqreqTree.DEPMT_PERMSN)
    elif req_title == 'Academic Writing Requirement (AWR) satisfied':
        return PrereqTree(PrereqTree.AWR)
    elif '-year standing' in req_title: # for 'minimum xyz-year standing'
        year_str = re.match(r'\S*\s(\w+)-.*', req_title).group(1) 
        return PrereqTree(PrereqTree.MIN_YR_STNDG, min_grade = WORD_TO_RANK[year_str])

    children = reqs_tree.find('ul')
    if not children:
        # for lines like 
        # 'Completed /Pre-Calculus 12/ with a minimum grade of /B (73%)'
        if req_title == 'Completed ': 
            req_title = next(title_strings)
            # skip over 'with a minimum grade of'
            next(title_strings)
            # here, next(title_strings) is something like 'B (73%)'
            min_grade = next(title_strings).split()[0]
            course_desc = ''
        else:
            # here the next strings are:
            # <whitespace>, - , <whitespace>, <course_desc>
            for count in range(3): next(title_strings)
            course_desc = next(title_strings)

        course_link = parse_course_link(reqs_tree.find('a', href=True))
        course_dep, course_num = split_course_code(req_title)
        cur_course = Course(course_dep, course_num, course_desc, None, None, course_link) 
        return PrereqTree(SINGLE_COURSE, reqs_list = [cur_course], 
                          min_grade = min_grade, notes = notes)

    # for lines like 'Earn a minimum grade of /C+/ in each of the following:'
    if 'minimum grade' in req_title:
        min_grade = next(title_strings)
        req_title = next(title_strings)

    # we can simply grab next(title_strings) here, because the cases where there
    # is a number, the number is in its own <span> (grabbed by the call to next),
    # but the entire 'Complete all of the following:' strings is together as
    # one string
    req_num = int(next(title_strings)) if ('all' not in req_title and 'each' not in req_title) \
                                       else ALL
    results = [parse_reqs_rec(child) for child in children.contents]
    
    return PrereqTree(req_num, reqs_list = results, min_grade = min_grade, 
                               notes = notes)

if __name__ == '__main__':
    # TODO: incorporate into Jenkins regression (WEBSCRAPE_0014)
    # CASE 1: Pre and Coreqs present
    #url = "https://www.uvic.ca/calendar/undergrad/index.php#/courses/ryzikO6QN?q=CSC%20361&&limit=20&skip=0&bc=true&bcCurrent=&bcCurrent=Computer%20Communications%20and%20Networks&bcItemType=courses"
    # CASE 2: No pre or coreqs
    #url = "https://www.uvic.ca/calendar/undergrad/index.php#/courses/HJZck_TmV?q=CSC105&&limit=20&skip=0&bc=true&bcCurrent=&bcCurrent=Computers%20and%20Information%20Processing&bcItemType=courses"
    # CASE 3: Prereqs only
    # url = "https://www.uvic.ca/calendar/undergrad/index.php#/courses/r1l00yY67E?q=SENG265&&limit=20&skip=0&bc=true&bcCurrent=&bcCurrent=Software%20Development%20Methods&bcItemType=courses"
    # CASE 4: more complicated trees
    #url ='https://www.uvic.ca/calendar/undergrad/index.php#/courses/Hkfbhda7E?q=SENG265&&%20%20%20%20limit=20&skip=0&bc=true&bcCurrent=&bcCurrent=Software%20Development%20Methods&bcItemType=cou%20%20%20%20rses'
    #url = 'https://www.uvic.ca/calendar/undergrad/index.php#/courses/r1e06RP6XN'
    # CASE 5: complicated coreqs
    #url = 'https://www.uvic.ca/calendar/undergrad/index.php#/courses/HytcJuaQV?q=CSC%20361&&%20%20%20%20limit=20&skip=0&bc=true&bcCurrent=&bcCurrent=Computer%20Communications%20and%20Networks&bcIt%20%20%20%20emType=courses'
    # CASE 6: min grade requirements
    # url = 'https://www.uvic.ca/calendar/undergrad/index.php#/courses/ByxQ12d6QE'
    # CASE 7: AWR
    url = 'https://www.uvic.ca/calendar/undergrad/index.php#/courses/r1rPrjq_t?q=CSC%20361'
    # CASE 8: min year standing
    # url = 'https://www.uvic.ca/calendar/undergrad/index.php#/courses/HyeHjkO674'

    # TODO: remove for loop below once implementation complete
    
    pre_and_coreqs = get_calendar_info(url)
    '''
    for idx in range(len(pre_and_coreqs)):
        print(f"pre_and_coreqs[{idx}] =")
        print(pre_and_coreqs[idx])
    '''
    pprint.pprint(parse_reqs(pre_and_coreqs[0]))
