from django.urls import path
from .views import *

urlpatterns = [
    path('create_team', create_team, name='create_team'),
    path('change_team_profile', change_team_profile, name='change_team_profile'),
    path('change_team_avatar', change_team_avatar, name='change_team_avatar'),
    path('add_manager', add_manager, name='add_manager'),
    path('delete_manager', delete_manager, name='delete_manager'),
    path('add_member', add_member, name='add_member'),
    path('delete_member', delete_member, name='delete_member'),
    path('show_member', show_member, name='show_member'),
    path('show_team', show_team, name='show_team'),
    path('delete_team', delete_team, name='delete_team'),
]
