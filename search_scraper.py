from course import Course
from prereqtree import PrereqTree
from bs4 import BeautifulSoup
import calendar_scrape
import urllib.request

CURRENT_TERM = '202309'

def get_course_objs(courses: list[str]) -> list[Course]:
    '''
    Given a list of coursecodes, query UVic for the matching courses and return
    a list of the corresponding Course objects. Course codes which do not match
    a UVic course are ignored. Pre/coreqs are not queried in this function, use
    populate_reqs function to query for pre/coreqs.    
    '''
    results = []
    for course_query in create_query(courses):
        results.extend(get_courses(course_query))

    return results

# TODO: does not yet implement all possible search criteria
def get_search_url(dep: str, course_num_strt: str, course_num_end: str,
                   term: str = CURRENT_TERM) -> str:
    '''
    Creates a UVic banner search URL for the course with the given information
    '''
    return ( 'https://www.uvic.ca/BAN1P/bwckctlg.p_display_courses?term_in=%s'
           + '&one_subj=%s&sel_crse_strt=%s&sel_crse_end=%s&sel_subj=' 
           + '&sel_levl=&sel_schd=&sel_coll=&sel_divs=&sel_dept=&sel_attr=') \
           % (term, dep, course_num_strt, course_num_end)

def create_query(course_titles: list[str], term: str = CURRENT_TERM) -> list[str]:
    '''
    Creates a UVic banner search URL for each course title in the given list of
    course_titles, returning the results in a list.
    '''
    results = []

    for course_title in course_titles:
        course_dep, course_num = calendar_scrape.split_course_code(course_title)
        results.append(get_search_url(course_dep, course_num, course_num, term))

    return results

def populate_reqs(courses: list[Course]) -> None:
    '''
    Mutate the given list of Courses to fill in their prerequsite information
    '''
    for course in courses:
        course_reqs = calendar_scrape.get_reqs_tuple(course.get_cal_weblink())
        course.set_reqs(*course_reqs)


def get_courses(href: str) -> list[Course]:
    '''
    Reterieve the UVic banner course search page located to at href, and return
    a list of Course instances in the search results
    '''
    fd = urllib.request.urlopen(href)
    webpage = BeautifulSoup(fd, 'html.parser')

    # Course entries are stored in a big table 1-column table
    # (class=datadisplaytable):
    #   <td class="nttitle"> for course headers
    #   <td class="ntdefault"> for course info
    #   usually these entries are in successive rows
    data_display_table = webpage.find('table', class_='datadisplaytable')
    table_entries = data_display_table.find_all('td')
        
    if len(table_entries) == 0:
        return []

    prev_entry = table_entries[0]    
    results = []
    
    for cur_entry in table_entries:
        if cur_entry['class'][0] == 'ntdefault' and prev_entry['class'][0] == 'nttitle':
            results.append(parse_course_info(cur_entry, prev_entry))
        prev_entry = cur_entry

    return results

def parse_course_info(ntdefault_entry, nttitle_entry) -> Course:
    '''
    Parse the ntdefault and nttitle entries of a course, creating and returning
    a Course object based on the entries
        - Returned Course has empty prereq and coreq data
    '''
    cal_link_tag  = ntdefault_entry.find('a')

    if __debug__: print(ntdefault_entry)
    cal_link = cal_link_tag['href'] if (cal_link_tag and 
                                        cal_link_tag.string == 'Calendar') else None

    long_name = nttitle_entry.find('a').string

    # long_name has a format like 'CSC 110 - Fundamentals of Programming I'
    # The spaces surrounding '-' are needed to avoid splitting on 'CO-OP'
    course_name, course_title = long_name.split(' - ')
    dep, num = course_name.strip().split(' ')
    course_title = course_title.strip()

    return Course(dep, num, course_title, None, None, cal_link)
  
 
