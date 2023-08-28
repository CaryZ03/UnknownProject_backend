from django.urls import path
from .views import *

urlpatterns = [
    path('group_send_notification_to_user', group_send_notification_to_user, name='group_send_notification_to_user'),
    path('check_notification_list', check_notification_list, name='check_notification_list'),
    path('post_skip_info', post_skip_info, name='post_skip_info'),
]
