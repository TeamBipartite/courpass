from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.template.context_processors import csrf
from .utils.view_helpers import get_group_legend, get_header_legend_data, get_processed_grid_data
from .utils.course import Course

@csrf_protect
def course_planning_tool(request):
    c = {}
    c.update(csrf(request))

    # Mock query courses
    math346 = Course("MATH", 346, "Introduction to Partial Differential Equations", {}, {}, "https://www.uvic.ca/calendar/future/undergrad/index.php#/courses/Hkfbhda7E?q=MATH346&&limit=20&skip=0&bc=true&bcCurrent=&bcCurrent=Introduction%20to%20Partial%20Differential%20Equations&bcItemType=courses")
    csc360 =  Course("CSC", 360, "Operating Systems", {}, {}, "https://www.uvic.ca/calendar/future/undergrad/index.php#/courses/SkWiJ_6mE?q=CSC360&&limit=20&skip=0&bc=true&bcCurrent=&bcCurrent=Operating%20Systems&bcItemType=courses")


    # Mock prereq courses
    math200 = Course("MATH", 200, "Calculus III", {}, {}, "https://www.uvic.ca/calendar/future/undergrad/index.php#/courses/view/5d1f76e5d2bc1524008cb6b4" )
    math201 = Course("MATH", 201, "Introduction to Differential Equations", {}, {}, "https://www.uvic.ca/calendar/future/undergrad/index.php#/courses/view/5c4ffbe436d45224006d0fce" )
    math204 = Course("MATH", 204, "Calculus IV", {}, {}, "https://www.uvic.ca/calendar/future/undergrad/index.php#/courses/view/5d1f71b694e82e2400a236df" )
    csc225 = Course("CSC", 225, "Algorithms and Data Structures I", {}, {}, "https://www.uvic.ca/calendar/undergrad/index.php#/courses/Bk_cy_a7V" )


    if request.method == "POST":
        c["prereq_search"] = request.POST["prereq-search"]
        c["courses_search"] = request.POST["courses-search"]
        # Mock data for call to get_query_courses()
        c["query_courses"] = [(csc360, True, True, 2), (math346, False, False, 0)]
        # Mock data for call to get_prereq_courses()
        c["prereq_courses"] = [math200, math201, math204, csc225]
        # Mock data for call to get_grid_data()
        c["grid_data"] = get_processed_grid_data([
            # is_prereq, is_corereq, group_id
            [(False, False, []), (True, False, [1, 0])], [(False, True, []), (True, False, [1, 0])], 
            [(False, False, []), (True, False, [1, 1])], [(True, False, []), (False, False, [])]
            ])
        # Mock data for get_group_info()
        #TODO be sure to use correct constants!!! 
        mock_group_info = [(0, False, "", []),
                           (1, True, "", [(2, True, "C+", []), (1, False, "A", [(1, True, "A", []), (2, True, "A", [])])]
                            )
                          ]
        c["group_info"] = get_group_legend(mock_group_info[1:])
        # Process header legend data
        c["header_legend"] = get_header_legend_data(c["query_courses"])
        
        

        return render(request, "./scraper/course_planning_tool_ui.html", c)
    else:
        return render(request, "./scraper/course_planning_tool_ui.html", c)


def home(request):
    return render(request, "./scraper/home.html", {})

