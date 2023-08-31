from django.urls import path
from .views import *

urlpatterns = [
    path('user_register_check', user_register_check, name='user_register_check'),
    path('user_register', user_register, name='user_register'),
    path('send_verification_code', send_verification_code, name='send_verification_code'),
    path('check_verification_code', check_verification_code, name='check_verification_code'),
    path('user_login', user_login, name='user_login'),
    path('reset_password_check', reset_password_check, name='reset_password_check'),
    path('reset_password', reset_password, name='reset_password'),
    path('logout', logout, name='logout'),
    path('cancel_account', cancel_account, name='cancel_account'),
    path('check_profile_self', check_profile_self, name='check_profile_self'),
    path('check_profile', check_profile, name='check_profile'),
    path('change_profile', change_profile, name='change_profile'),
    path('upload_avatar', upload_avatar, name='upload_avatar'),
    path('upload_email_check', upload_email_check, name='upload_email_check'),
    path('upload_email', upload_email, name='upload_email'),
    path('deploy_test', deploy_test, name='deploy_test'),
    path('check_token', check_token, name='check_token'),
    path('check_team_list', check_team_list, name='check_team_list'),
    path('search_user_by_username', search_user_by_username, name='search_user_by_username'),
    path('user_change_password', user_change_password, name='user_change_password')
]
