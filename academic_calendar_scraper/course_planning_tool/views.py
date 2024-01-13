from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.template.context_processors import csrf
from .utils.view_helpers import get_group_legend, get_header_legend_data, get_processed_grid_data
from .utils.prereqgrid.prereqgrid import PrereqGrid
from .utils.calendar_scrape.calendar_scrape import *
from .utils.search_scraper.search_scraper import *

@csrf_protect
def course_planning_tool(request):
    c = {}
    c.update(csrf(request))

    if request.method == "POST":
        c["prereq_search"] = request.POST["prereq-search"]
        c["courses_search"] = request.POST["courses-search"]
        grid = PrereqGrid(c['courses_search'].split(','), c['prereq_search'].split(','))
        c["query_courses"] = grid.get_query_courses()
        c["prereq_courses"] = grid.get_prereq_courses()
        c["grid_data"] = get_processed_grid_data(grid.get_grid_data())
        c["group_info"] = get_group_legend(grid.get_group_info()[1:])
        c["header_legend"] = get_header_legend_data(c["query_courses"])
        
        return render(request, "./scraper/course_planning_tool_ui.html", c)
    else:
        return render(request, "./scraper/course_planning_tool_ui.html", c)


def home(request):
    return render(request, "./scraper/home.html", {})

