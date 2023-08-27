from django.urls import path
from .views import *

urlpatterns = [
    path('get_team_members_and_permissions', get_team_members_and_permissions, name='get_team_members_and_permissions'),
]
