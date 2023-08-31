from django.urls import path
from .views import *

urlpatterns = [
    path('get_team_members_and_permissions', get_team_members_and_permissions, name='get_team_members_and_permissions'),
    path('get_teams_for_user', get_teams_for_user, name='get_teams_for_user'),
    path('store_message', store_message, name='store_message'),
    path('get_team_chat_history', get_team_chat_history, name='get_team_chat_history'),
    path('search_chat_message', search_chat_message, name='search_chat_message'),
    path('create_private_chat', create_private_chat, name='create_private_chat'),
    path('acquire_private_chat', acquire_private_chat, name='acquire_private_chat'),
    path('store_private_message', store_private_message, name='store_private_message'),
    path('get_private_chat_history', get_private_chat_history, name='get_private_chat_history'),
    path('create_group_chat', create_group_chat, name='create_group_chat'),
    path('acquire_group_chat', acquire_group_chat, name='acquire_group_chat'),
    path('store_group_message', store_group_message, name='store_group_message'),
    path('get_group_chat_history', get_group_chat_history, name='get_group_chat_history'),
    path('update_leave_message', update_leave_message, name='update_leave_message'),
    path('acquire_unread_message', acquire_unread_message, name='acquire_unread_message'),
    path('get_group_chat_members', get_group_chat_members, name='get_group_chat_members'),
]
