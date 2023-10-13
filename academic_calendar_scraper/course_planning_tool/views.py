from django.template import loader
from django.http import HttpResponse


def course_planning_tool(request):
    template = loader.get_template("course_planning_tool_ui.html")
    return HttpResponse(template.render())
