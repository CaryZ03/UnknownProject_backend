from django.urls import path
from .views import *

urlpatterns = [
    path('send_notification_to_user', send_notification_to_user, name='send_notification_to_user'),
]
