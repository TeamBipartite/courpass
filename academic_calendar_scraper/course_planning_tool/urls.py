from django.urls import path
from . import views

urlpatterns = [
    path('course_planning_tool/', views.course_planning_tool, name='course_planning_tool')
]