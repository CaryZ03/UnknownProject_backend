from django.urls import path
from .views import *

urlpatterns = [
    path('create_project', create_project, name='create_project'),
    path('delete_project', delete_project, name='delete_project'),
    path('show_profile', show_profile, name='show_profile'),
    path('change_profile', change_profile, name='change_profile'),
    path('add_recycle', add_recycle, name='add_recycle'),
    path('create_requirement', create_requirement, name='create_requirement'),
    path('delete__requirement', delete__requirement, name='delete__requirement'),
    path('show_profile_requirement', show_profile_requirement, name='show_profile_requirement'),
    path('change_profile_requirement', change_profile_requirement, name='change_profile_requirement'),
    path('check_project_list', check_project_list, name='check_project_list'),
    path('search_status', search_status, name='search_status'),
    path('check_project_list_team', check_project_list_team, name='check_project_list_team'),
    path('check_requirement_list', check_requirement_list, name='check_requirement_list'),
    path('search_project_by_name', search_project_by_name, name='search_project_by_name'),
]