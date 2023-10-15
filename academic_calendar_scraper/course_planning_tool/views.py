from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.template.context_processors import csrf

@csrf_protect
def course_planning_tool(request):
    c = {}
    c.update(csrf(request))

    courses = ["CSC225", "MATH222"]

    if request.method == "POST":
        c['searched'] = request.POST["prereq-search"]
        c['course'] = request.POST["course"]
        c['course_list'] = courses

        return render(request, "course_planning_tool_ui.html", c)
    else:
        return render(request, "course_planning_tool_ui.html", c)
