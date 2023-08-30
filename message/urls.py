from django.urls import path
from .views import *

urlpatterns = [
    path('group_send_notification_to_user', group_send_notification_to_user, name='group_send_notification_to_user'),
    path('check_notification_list', check_notification_list, name='check_notification_list'),
    path('post_skip_info', post_skip_info, name='post_skip_info'),
    path('mark_unread_notification', mark_unread_notification, name='mark_unread_notification'),
    path('mark_read_notification', mark_read_notification, name='mark_read_notification'),
    path('mark_all_read_notification', mark_all_read_notification, name='mark_all_read_notification'),
    path('delete_read_notifications', delete_read_notifications, name='delete_read_notifications'),
    path('delete_notification', delete_notification, name='delete_notification'),

]
