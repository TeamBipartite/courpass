#! /bin/env python3

from course import Course
from bs4 import BeautifulSoup
import urllib.request
import sys

def get_courses(href: str) -> list[Course]:
    '''
    Reterieve the UVic banner course search page located to at href, and return
    a list of Course instances in the search results
    '''
    fd = urllib.request.urlopen(href)
    webpage = BeautifulSoup(fd, 'html.parser')

    # Course entries are stored in a big table 1-column table
    # (class=dataidisplaytable):
    #   <td class="nttitle"> for course headers
    #   <td class="ntdefault"> for course info
    #   usually there entries are in successive rows
    data_display_table = webpage.find('table', class_='datadisplaytable')
    table_entries = data_display_table.find_all('td')
    #    for entry in table_entries:
    #       print('\n----\n%r' % entry)
        
    if len(table_entries) == 0:
        return []

    prev_entry = table_entries[0]    
    results = []
    
    for cur_entry in table_entries:
        #print('cur class: %s, prev_class: %s' % (cur_entry['class'],  prev_entry['class']))
        if cur_entry['class'][0] ==  'ntdefault' and prev_entry['class'][0] == 'nttitle':
            #print('inside')
            results.append(create_course(cur_entry, prev_entry))
        prev_entry = cur_entry

    return results

def create_course(ntdefault_entry, nttitle_entry) -> Course:
    '''
    ... 
    '''
    cal_link  = ntdefault_entry.find('a')['href']
    long_name = nttitle_entry.find('a').string
    course_name, course_title = long_name.split('-')
    dep, num = course_name.strip().split(' ')
    num = int(num)
    course_title = course_title.strip()

    return Course(dep, num, course_title, {}, {}, cal_link)
  
 
results = get_courses(sys.argv[1])
#results = get_courses('https://www.uvic.ca/BAN1P/bwckctlg.p_display_courses?term_in=202009&one_subj=CHEM&sel_crse_strt=101&sel_crse_end=115&sel_subj=&sel_levl=&sel_schd=&sel_coll=&sel_divs=&sel_dept=&sel_attr=')
print(results)
