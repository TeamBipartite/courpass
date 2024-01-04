# academic-calendar-scraper
[![Build Status](https://www.johnnyw.ca/jenkins/buildStatus/icon?job=academic-calendar-scraper%2Fcalendar-scrape-regression%2Fmain)](https://www.johnnyw.ca/jenkins/job/academic-calendar-scraper/job/calendar-scrape-regression/job/main/)

## Django webserver

(in development)

## Command-line usage

Within the root directory, there is a main.py file which can be used to generate a text-based prereqsuite grid. Basic usage is as follows:

```bash
$ python3 -O main.py <LIST_OF_COURSES_TO_SEARCH> <LIST_OF_PREREQS_TO_FIND>
```
where `LIST_OF_COURSES_TO_SEARCH` and `LIST_OF_PREREQS_TO_FIND` are comma-separated lists. For example:

```bash
$ python3 -O main.py CSC360,CSC361,CSC370,CSC421,MATH100,MATH346 CSC226,SENG265,CSC230,ECE255,MATH204,MATH200
Prereq of: CSC360*    CSC361   CSC370*   CSC421⁴   MATH100+  MATH346  
    CSC226    ✗         ✗         ✗         ✓         ✗         ✗     
   SENG265    ✓         ✓         ✓         ✗         ✗         ✗     
    CSC230    ✓¹        ✓²        ✗         ✗         ✗         ✗     
    ECE255    ✓¹        ✓²        ✗         ✗         ✗         ✗     
   MATH204    ✗         ✗         ✗         ✗         ✗        ✓³¹    
   MATH200    ✗         ✗         ✗         ✗         ✗        ✓³⁰    
-----------
Header legend:
     ²³⁴⁵: Minimum year standing required.
        *: Not all prereqs shown. See calendar for details.
        +: Or department permission.
-----------
Grid legend:
        1: Any 1 of these. Not all courses in this group shown. See calendar for details.
        2: Any 1 of these. Not all courses in this group shown. See calendar for details.
        3: Any 1 of these.
              3 0: All of these. Not all courses in this group shown. See calendar for details.
              3 1: All of these.
```

To enable debuging output, remove the `-O` argument from the launch command.

