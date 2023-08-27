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
    path('invite_link', invite_link, name='invite_link'),
    path('show_check', show_check, name='show_check'),
    path('check_member', check_member, name='check_member'),
    path('join_team_url', join_team_url, name='join_team_url'),
    path('join_team_straight', join_team_straight, name='join_team_straight'),
    path('change_nickname', change_nickname, name='change_nickname'),
    path('member_role', member_role, name='member_role'),
]
