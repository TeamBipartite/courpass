#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.common.exceptions import NoSuchDriverException
from selenium.webdriver.remote.webdriver import WebDriver
from bs4 import BeautifulSoup
import pprint
from collections import namedtuple

# numReqd is an integer representing the numbeof items from the reqs_list are 
#         required, where 0 represents 'ALL', and -1 is used to indicate a
#         single course entry itself
# reqs_list is a list of PrereqTrees representing the items that are requied. If
#           num_reqd == -1, then this is a single course (Course object)
PrereqTree = namedtuple('PrereqTree', ['num_reqd', 'reqs_list'])

def get_calendar_info(url) -> list[str]:
    pre_and_coreq_html = []

    try:
        # Attempt scrape using Chrome
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new") # ensure browser opens in background
        driver = webdriver.Chrome(options = options)
    except NoSuchDriverException:
        # Attempt scrape using Edge
        try:
            options = webdriver.EdgeOptions()
            options.add_argument("--headless=new")
            driver = webdriver.Edge(options = options)
        except NoSuchDriverException:
            # Attempt scrape using Safari
            try:
                options = webdriver.SafariOptions()
                options.add_argument("--headless=new")
                driver = webdriver.Safari(options = options)
            # TODO: could technically be a different error
            except:
                print("Sorry, you do not have a browser that supports this application.")
                print("Please download one of Chrome, Edge, or Safari to use this application.")
            else:
                scrape_calendar_page(driver, pre_and_coreq_html)
        except Exception as e:
            # TODO: may need a better message here (maybe?)
            print(f"{e}")
        else:
            scrape_calendar_page(driver, pre_and_coreq_html)
    except Exception as e:
        print(f"{e}")
    else:
        scrape_calendar_page(driver, pre_and_coreq_html)

    
    return pre_and_coreq_html

def scrape_calendar_page(driver: WebDriver, pre_and_coreq_html: list[str]) -> None:
     # Open browser at the given url
    driver.get(url)
    # Wait 5 seconds for the browser to load at the url
    driver.implicitly_wait(5)
    # Search for <span> who has a direct child of tag <h3> containing Prerequisites or Pre- or corequisites
    cal_sections = driver.find_elements(By.XPATH, "//span[h3[contains(text(), 'Prerequisites') or contains(text(), 'Pre- or corequisites')]]")

    for section in cal_sections:
        pre_and_coreq_html.append(section.get_attribute("innerHTML"))
    
    return

def parse_reqs(raw_html: str) -> PrereqTree:
    '''
    Parse raw html representing a Pre/Coreq list from a UVic
    acadmeic calendar webpage, returning a PrereqTree with the data represented
    '''
    parser = BeautifulSoup(raw_html, 'html.parser')

    list_tree = parser.find('li')
    return parse_reqs_rec(list_tree) if list_tree else []

def parse_reqs_rec(reqs_tree: BeautifulSoup) -> PrereqTree:
    '''
    Given a BeautifulSoup tag to the li element representing the root of a UVic
    pre/coreq tree, parse the tree and return a PrereqTree with the data
    represented
    '''
    # needs to be saved to its own variable as we may call next() on it again
    title_strings = reqs_tree.strings
    req_title = next(title_strings)

    children = reqs_tree.find('ul')
    if not children: return PrereqTree(-1, req_title)

    req_num = int(next(title_strings)) if req_title == 'Complete ' else 0

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
    # CASE 4: more complicated tree
    url ='https://www.uvic.ca/calendar/undergrad/index.php#/courses/Hkfbhda7E?q=SENG265&&%20%20%20%20limit=20&skip=0&bc=true&bcCurrent=&bcCurrent=Software%20Development%20Methods&bcItemType=cou%20%20%20%20rses'

    # TODO: remove for loop below once implementation complete
    
    pre_and_coreqs = get_calendar_info(url)
    '''
    for idx in range(len(pre_and_coreqs)):
        print(f"pre_and_coreqs[{idx}] =")
        print(pre_and_coreqs[idx])
    '''
    pprint.pprint(parse_reqs(pre_and_coreqs[0]))
    pprint.pprint(parse_reqs(''))
    # TODO: Left for testing purposes - to remove
    """
    try:
        print("outer try block")
        x = 5/0
    except ZeroDivisionError:
        print("outer except block")
        try:
            print("Middle try block")
            x = 5/0
        except ZeroDivisionError:
            print("Middle except block")
            try:
                print("Inner try block")
            except ZeroDivisionError:
                print("Inner except block")
            else:
                print("Inner else block")
        else:
            print("Middle else block")
    else:
        print("outer else block")

    print("After all try except blocks")
    """
