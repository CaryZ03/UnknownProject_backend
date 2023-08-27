from django.urls import path
from .views import *

urlpatterns = [
    path('group_send_notification_to_user', group_send_notification_to_user, name='group_send_notification_to_user'),
]
