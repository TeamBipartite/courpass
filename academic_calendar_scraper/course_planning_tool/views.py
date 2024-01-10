from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.template.context_processors import csrf
from .utils.view_helpers import get_group_legend, get_header_legend_data, get_processed_grid_data
from .utils.prereqgrid.prereqgrid import PrereqGrid
from .utils.calendar_scrape.calendar_scrape import get_calendar_info

@csrf_protect
def course_planning_tool(request):
    c = {}
    c.update(csrf(request))

    if request.method == "POST":
        c["prereq_search"] = request.POST["prereq-search"]
        c["courses_search"] = request.POST["courses-search"]
        grid = PrereqGrid("CSC360", "CSC226")
        c["query_courses"] = grid.get_query_courses()
        c["prereq_courses"] = grid.get_prereq_courses()
        # TODO use proper class method for grid data
        c["grid_data"] = get_processed_grid_data([
            # is_prereq, is_corereq, group_id
            [(False, False, []), (True, False, [1, 0])], [(False, True, []), (True, False, [1, 0])], 
            [(False, False, []), (True, False, [1, 1])], [(True, False, []), (False, False, [])]
            ])
        c["group_info"] = get_group_legend(grid.get_group_info()[1:])
        c["header_legend"] = get_header_legend_data(c["query_courses"])
        
        

        return render(request, "./scraper/course_planning_tool_ui.html", c)
    else:
        return render(request, "./scraper/course_planning_tool_ui.html", c)


def home(request):
    return render(request, "./scraper/home.html", {})

