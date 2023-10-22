from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.template.context_processors import csrf
from .utils.course import Course

@csrf_protect
def course_planning_tool(request):
    c = {}
    c.update(csrf(request))

    course1 = Course("CSC", 225, "Algorithms and Data Structures I", {}, {}, "https://www.uvic.ca/calendar/undergrad/index.php#/courses/Bk_cy_a7V" )
    course2 = Course("MATH", 222, "Discrete Math", {}, {}, "https://www.uvic.ca/calendar/undergrad/index.php#/courses/Sye1xndp74" )
    
    courses = ["MATH 222", "CSC 226"]
    """
    TODO:
    Use this list of Course objects once a custom tag is created
    courses = [course1, course2]
    """

    if request.method == "POST":
        c['searched'] = request.POST["prereq-search"]
        c['course'] = request.POST["course"]
        c['course_list'] = courses

        return render(request, "course_planning_tool_ui.html", c)
    else:
        return render(request, "course_planning_tool_ui.html", c)
