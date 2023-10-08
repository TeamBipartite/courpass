#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.common.exceptions import NoSuchDriverException
from selenium.webdriver.remote.webdriver import WebDriver
from bs4 import BeautifulSoup
import pprint
from collections import namedtuple

'''
numReqd is an integer representing the number of items from the reqs_list are 
        required, where:
        - 0 represents 'ALL'
        - -1 is used to indidate a single course entry itself
        - -2 is used to indicate 'or permission from the department'  
reqs_list is a list of PrereqTrees representing the items that are requied. If
          num_reqd == -1, then this is a single course (Course object)
'''          
PrereqTree = namedtuple('PrereqTree', ['num_reqd', 'reqs_list'])

WEBDRIVERS  = {webdriver.ChromeOptions: webdriver.Chrome, 
               webdriver.EdgeOptions: webdriver.Edge,
               webdriver.SafariOptions: webdriver.Safari,
               webdriver.FirefoxOptions: webdriver.Firefox}

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

    return scrape_calendar_page(driver)

def scrape_calendar_page(driver: WebDriver) -> list[str]:
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
    return (1, [parse_reqs_rec(root) for root in roots])

def parse_reqs_rec(reqs_tree: BeautifulSoup) -> PrereqTree:
    '''
    Given a BeautifulSoup tag to the li element representing the root of a UVic
    pre/coreq tree, parse the tree and return a PrereqTree with the data
    represented
    '''
    # needs to be saved to its own variable as we may call next() on it again
    title_strings = reqs_tree.strings
    req_title = next(title_strings)

    if req_title == 'or permission of the department.': return (-2, None)

    children = reqs_tree.find('ul')
    if not children: return PrereqTree(-1, req_title)

    # we can simply grab next(title_strings) here, because the cases where there
    # is a number, the number is in its own <span> (grabbed by the call to next),
    # but the entire 'Complete all of the following:' strings is together as
    # one string
    req_num = int(next(title_strings)) if 'all' not in req_title else 0
    pprint.pprint(children.contents)
    results = [parse_reqs_rec(child) for child in children.contents]
    
    return PrereqTree(req_num, results)

if __name__ == '__main__':
    # TODO: remove mock urls
    # CASE 1: Pre and Coreqs present
    # url = "https://www.uvic.ca/calendar/undergrad/index.php#/courses/ryzikO6QN?q=CSC%20361&&limit=20&skip=0&bc=true&bcCurrent=&bcCurrent=Computer%20Communications%20and%20Networks&bcItemType=courses"
    # CASE 2: No pre or coreqs
    #url = "https://www.uvic.ca/calendar/undergrad/index.php#/courses/HJZck_TmV?q=CSC105&&limit=20&skip=0&bc=true&bcCurrent=&bcCurrent=Computers%20and%20Information%20Processing&bcItemType=courses"
    # CASE 3: Prereqs only
    # url = "https://www.uvic.ca/calendar/undergrad/index.php#/courses/r1l00yY67E?q=SENG265&&limit=20&skip=0&bc=true&bcCurrent=&bcCurrent=Software%20Development%20Methods&bcItemType=courses"
    # CASE 4: more complicated trees
    #url ='https://www.uvic.ca/calendar/undergrad/index.php#/courses/Hkfbhda7E?q=SENG265&&%20%20%20%20limit=20&skip=0&bc=true&bcCurrent=&bcCurrent=Software%20Development%20Methods&bcItemType=cou%20%20%20%20rses'
    url = 'https://www.uvic.ca/calendar/undergrad/index.php#/courses/r1e06RP6XN'
    # CASE 5: complicated coreqs
    #url = 'https://www.uvic.ca/calendar/undergrad/index.php#/courses/HytcJuaQV?q=CSC%20361&&%20%20%20%20limit=20&skip=0&bc=true&bcCurrent=&bcCurrent=Computer%20Communications%20and%20Networks&bcIt%20%20%20%20emType=courses'

    # TODO: remove for loop below once implementation complete
    
    pre_and_coreqs = get_calendar_info(url)
    '''
    for idx in range(len(pre_and_coreqs)):
        print(f"pre_and_coreqs[{idx}] =")
        print(pre_and_coreqs[idx])
    '''
    pprint.pprint(parse_reqs(pre_and_coreqs[0]))
