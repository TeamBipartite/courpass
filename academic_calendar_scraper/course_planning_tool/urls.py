from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('course_planning_tool/', views.course_planning_tool, name='course_planning_tool')
]