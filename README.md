# academic-calendar-scraper
[![Build Status](https://www.johnnyw.ca/jenkins/buildStatus/icon?job=academic-calendar-scraper%2Fcalendar-scrape-regression%2Fmain)](https://www.johnnyw.ca/jenkins/job/academic-calendar-scraper/job/calendar-scrape-regression/job/main/)

## Django webserver
To launch the Django server for local development, navigate to the academic_calendar_scraper/academic_calendar_scraper directory. You can verify you are in the correct directory by ensuring there is a file called manage.py. From there, you can run the following command:
```
$ python manage.py runserver
```

The above command with output some status information. You will likely see a message regarding "18 unapplied migration(s)," as mentioned in the docs [here](https://docs.djangoproject.com/en/4.2/intro/tutorial01/); they can be ignored at this time.

You will find the server running [here](http://127.0.0.1:8000/); note, the local development url is also given as part of the above command's output.

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

