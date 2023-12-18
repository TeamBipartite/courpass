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
$ python3 -O main.py CSC360,CSC361,CSC370,CSC421 CSC226,SENG265,CSC230
Prereq of: CSC360*    CSC361   CSC370*   CSC421⁴   MATH100*+ 
    CSC226    ✗         ✗         ✗         ✓         ✗     
   SENG265    ✓         ✓         ✓         ✗         ✗     
    CSC230    ✓¹        ✓¹        ✗         ✗         ✗     
    ECE255    ✓¹        ✓¹        ✗         ✗         ✗     
-----------
Header legend:
     ²³⁴⁵: Minimum year standing required.
        *: Not all prereqs shown. See calendar for details.
        +: Or department permission.
-----------
Grid legend:
  Group 1: Any 1 of these. Not all courses in this group shown. See calendar for details.
```

To enable debuging output, remove the `-O` argument from the launch command.

