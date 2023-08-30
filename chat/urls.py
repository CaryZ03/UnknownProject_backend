from django.urls import path
from .views import *

urlpatterns = [
    path('get_team_members_and_permissions', get_team_members_and_permissions, name='get_team_members_and_permissions'),
    path('get_teams_for_user', get_teams_for_user, name='get_teams_for_user'),
    path('store_message', store_message, name='store_message'),
    path('get_team_chat_history', get_team_chat_history, name='get_team_chat_history'),
    path('search_chat_message', search_chat_message, name='search_chat_message'),
    path('create_private_chat', create_private_chat, name='create_private_chat'),
]
