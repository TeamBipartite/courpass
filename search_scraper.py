#! /bin/env python3

from course import Course
from bs4 import BeautifulSoup
import urllib.request

#NOTE: only needed for cli interactive functionality
DEBUG = False
import sys
import pprint

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

    if DEBUG: print(ntdefault_entry)
    # FIXME: searching for string value of Calendar on first tag works
    #        but is a bodge and should be fixed
    cal_link = cal_link_tag['href'] if (cal_link_tag and 
                                        cal_link_tag.string == 'Calendar') else None

    long_name = nttitle_entry.find('a').string

    # long_name has a format like 'CSC 110 - Fundamentals of Programming I'
    # The spaces surrounding '-' are needed to avoid splitting on 'CO-OP'
    course_name, course_title = long_name.split(' - ')
    dep, num = course_name.strip().split(' ')
    course_title = course_title.strip()

    return Course(dep, num, course_title, {}, {}, cal_link)
  
 
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: %s <UVic Banner search link> <-d>" % (sys.argv[0]))
        sys.exit(1)

    if len(sys.argv) > 2 and '-d' in sys.argv[2]: DEBUG = True

    results = get_courses(sys.argv[1])
    pprint.pprint(results)
