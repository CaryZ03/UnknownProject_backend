from django.urls import path
from .views import *

urlpatterns = [
    path('create_project', create_project, name='create_project'),
    path('delete_project', delete_project, name='change_team_profile'),
    path('show_profile', show_profile, name='change_team_avatar'),
    path('change_profile', change_profile, name='add_manager'),
    path('add_recycle', add_recycle, name='delete_manager'),
]